from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func, extract
from app.models import db, Usuario, Veiculo, Servico, Orcamento, StatusServico
from functools import wraps

bp = Blueprint('views', __name__)


def login_required(f):
    """Decorator para proteger rotas que exigem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página', 'warning')
            return redirect(url_for('views.login'))
        return f(*args, **kwargs)
    return decorated_function


def tipo_usuario_required(*tipos_permitidos):
    """Decorator para verificar tipo de usuário"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('tipo_usuario') not in tipos_permitidos:
                flash('Você não tem permissão para acessar esta página', 'danger')
                return redirect(url_for('views.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============= Autenticação =============

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.verificar_senha(senha):
            session['user_id'] = usuario.id
            session['nome'] = usuario.nome
            session['email'] = usuario.email
            session['tipo_usuario'] = usuario.tipo.value
            
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            return redirect(url_for('views.dashboard'))
        else:
            flash('Email ou senha inválidos', 'danger')
    
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('views.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        tipo_usuario = request.form.get('tipo_usuario')
        
        # Validações
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'danger')
            return render_template('register.html')
        
        if tipo_usuario not in ['cliente', 'mecanico']:
            flash('Tipo de usuário inválido', 'danger')
            return render_template('register.html')
        
        # Criar usuário
        usuario = Usuario(
            nome=nome,
            email=email,
            tipo=tipo_usuario
        )
        usuario.set_senha(senha)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('views.login'))
    
    return render_template('register.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('views.login'))


# ============= Dashboard =============

@bp.route('/dashboard')
@login_required
def dashboard():
    tipo_usuario = session.get('tipo_usuario')
    user_id = session.get('user_id')
    
    if tipo_usuario == 'cliente':
        return dashboard_cliente(user_id)
    elif tipo_usuario == 'mecanico':
        return dashboard_mecanico(user_id)
    elif tipo_usuario == 'gerente':
        return dashboard_gerente()
    else:
        flash('Tipo de usuário inválido', 'danger')
        return redirect(url_for('views.logout'))


def dashboard_cliente(user_id):
    veiculos = Veiculo.query.filter_by(usuario_id=user_id).all()
    
    # Estatísticas
    stats = {
        'total_veiculos': len(veiculos),
        'servicos_andamento': Servico.query.join(Veiculo).filter(
            Veiculo.usuario_id == user_id,
            Servico.status == StatusServico.EM_ANDAMENTO
        ).count(),
        'servicos_concluidos': Servico.query.join(Veiculo).filter(
            Veiculo.usuario_id == user_id,
            Servico.status == StatusServico.CONCLUIDO
        ).count()
    }
    
    # Serviços recentes
    servicos = Servico.query.join(Veiculo).filter(
        Veiculo.usuario_id == user_id
    ).order_by(Servico.data_entrada.desc()).limit(10).all()
    
    # Adicionar classes de status
    for servico in servicos:
        servico.status_class = get_status_class(servico.status)
        servico.status_display = get_status_display(servico.status)
    
    return render_template('dashboard_cliente.html', 
                         stats=stats, 
                         veiculos=veiculos[:5], 
                         servicos=servicos)


def dashboard_mecanico(user_id):
    # Estatísticas
    stats = {
        'aguardando_orcamento': Servico.query.filter_by(
            mecanico_responsavel_id=user_id,
            status=StatusServico.AGUARDANDO_ORCAMENTO
        ).count(),
        'em_andamento': Servico.query.filter_by(
            mecanico_responsavel_id=user_id,
            status=StatusServico.EM_ANDAMENTO
        ).count(),
        'concluidos_mes': Servico.query.filter_by(
            mecanico_responsavel_id=user_id,
            status=StatusServico.CONCLUIDO
        ).filter(
            extract('month', Servico.data_conclusao) == datetime.now().month,
            extract('year', Servico.data_conclusao) == datetime.now().year
        ).count(),
        'total_servicos': Servico.query.filter_by(mecanico_responsavel_id=user_id).count()
    }
    
    # Serviços em atendimento
    servicos = Servico.query.filter_by(mecanico_responsavel_id=user_id).filter(
        Servico.status.in_([
            StatusServico.AGUARDANDO_ORCAMENTO,
            StatusServico.ORCAMENTO_APROVADO,
            StatusServico.EM_ANDAMENTO
        ])
    ).order_by(Servico.data_entrada.desc()).all()
    
    for servico in servicos:
        servico.status_class = get_status_class(servico.status)
        servico.status_display = get_status_display(servico.status)
    
    return render_template('dashboard_mecanico.html', stats=stats, servicos=servicos)


def dashboard_gerente():
    # Estatísticas gerais
    stats = {
        'total_clientes': Usuario.query.filter_by(tipo='cliente').count(),
        'receita_mensal': db.session.query(func.sum(Servico.valor_total)).filter(
            Servico.status == StatusServico.CONCLUIDO,
            extract('month', Servico.data_conclusao) == datetime.now().month,
            extract('year', Servico.data_conclusao) == datetime.now().year
        ).scalar() or 0,
        'servicos_ativos': Servico.query.filter(
            Servico.status.in_([
                StatusServico.AGUARDANDO_ORCAMENTO,
                StatusServico.ORCAMENTO_APROVADO,
                StatusServico.EM_ANDAMENTO
            ])
        ).count(),
        'total_veiculos': Veiculo.query.count(),
        'total_servicos': Servico.query.count(),
        'status_aguardando': Servico.query.filter_by(status=StatusServico.AGUARDANDO_ORCAMENTO).count(),
        'status_aprovado': Servico.query.filter_by(status=StatusServico.ORCAMENTO_APROVADO).count(),
        'status_andamento': Servico.query.filter_by(status=StatusServico.EM_ANDAMENTO).count(),
        'status_concluido': Servico.query.filter_by(status=StatusServico.CONCLUIDO).count()
    }
    
    # Estatísticas por mecânico
    mecanicos = Usuario.query.filter_by(tipo='mecanico').all()
    mecanicos_stats = []
    for mecanico in mecanicos:
        mecanicos_stats.append({
            'nome': mecanico.nome,
            'aguardando': Servico.query.filter_by(
                mecanico_responsavel_id=mecanico.id,
                status=StatusServico.AGUARDANDO_ORCAMENTO
            ).count(),
            'em_andamento': Servico.query.filter_by(
                mecanico_responsavel_id=mecanico.id,
                status=StatusServico.EM_ANDAMENTO
            ).count(),
            'concluidos': Servico.query.filter_by(
                mecanico_responsavel_id=mecanico.id,
                status=StatusServico.CONCLUIDO
            ).filter(
                extract('month', Servico.data_conclusao) == datetime.now().month,
                extract('year', Servico.data_conclusao) == datetime.now().year
            ).count(),
            'total': Servico.query.filter_by(mecanico_responsavel_id=mecanico.id).count()
        })
    
    # Serviços recentes
    servicos = Servico.query.order_by(Servico.data_entrada.desc()).limit(15).all()
    for servico in servicos:
        servico.status_class = get_status_class(servico.status)
        servico.status_display = get_status_display(servico.status)
    
    return render_template('dashboard_gerente.html', 
                         stats=stats, 
                         mecanicos_stats=mecanicos_stats,
                         servicos=servicos)


# ============= Veículos =============

@bp.route('/veiculos')
@login_required
def veiculos_list():
    if session.get('tipo_usuario') == 'cliente':
        veiculos = Veiculo.query.filter_by(usuario_id=session.get('user_id')).all()
    else:
        veiculos = Veiculo.query.all()
    
    return render_template('veiculos_list.html', veiculos=veiculos)


@bp.route('/veiculos/novo', methods=['GET', 'POST'])
@login_required
def veiculo_create():
    if request.method == 'POST':
        veiculo = Veiculo(
            marca=request.form.get('marca'),
            modelo=request.form.get('modelo'),
            ano=int(request.form.get('ano')),
            placa=request.form.get('placa').upper(),
            cor=request.form.get('cor'),
            usuario_id=session.get('user_id')
        )
        
        db.session.add(veiculo)
        db.session.commit()
        
        flash('Veículo cadastrado com sucesso!', 'success')
        return redirect(url_for('views.veiculos_list'))
    
    return render_template('veiculo_form.html', veiculo=None)


@bp.route('/veiculos/<int:id>')
@login_required
def veiculo_detail(id):
    veiculo = Veiculo.query.get_or_404(id)
    
    # Verificar permissão
    if session.get('tipo_usuario') == 'cliente' and veiculo.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para ver este veículo', 'danger')
        return redirect(url_for('views.veiculos_list'))
    
    servicos = Servico.query.filter_by(veiculo_id=id).order_by(Servico.data_entrada.desc()).all()
    for servico in servicos:
        servico.status_class = get_status_class(servico.status)
        servico.status_display = get_status_display(servico.status)
    
    return render_template('veiculo_detail.html', veiculo=veiculo, servicos=servicos)


@bp.route('/veiculos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def veiculo_edit(id):
    veiculo = Veiculo.query.get_or_404(id)
    
    # Verificar permissão
    if session.get('tipo_usuario') == 'cliente' and veiculo.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para editar este veículo', 'danger')
        return redirect(url_for('views.veiculos_list'))
    
    if request.method == 'POST':
        veiculo.marca = request.form.get('marca')
        veiculo.modelo = request.form.get('modelo')
        veiculo.ano = int(request.form.get('ano'))
        veiculo.placa = request.form.get('placa').upper()
        veiculo.cor = request.form.get('cor')
        
        db.session.commit()
        
        flash('Veículo atualizado com sucesso!', 'success')
        return redirect(url_for('views.veiculo_detail', id=id))
    
    return render_template('veiculo_form.html', veiculo=veiculo)


@bp.route('/veiculos/<int:id>/deletar', methods=['POST'])
@login_required
def veiculo_delete(id):
    veiculo = Veiculo.query.get_or_404(id)
    
    # Verificar permissão
    if session.get('tipo_usuario') == 'cliente' and veiculo.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para excluir este veículo', 'danger')
        return redirect(url_for('views.veiculos_list'))
    
    # Verificar se há serviços
    if veiculo.servicos:
        flash('Não é possível excluir um veículo com serviços cadastrados', 'danger')
        return redirect(url_for('views.veiculo_detail', id=id))
    
    db.session.delete(veiculo)
    db.session.commit()
    
    flash('Veículo excluído com sucesso!', 'success')
    return redirect(url_for('views.veiculos_list'))


# ============= Serviços =============

@bp.route('/servicos')
@login_required
def servicos_list():
    tipo_usuario = session.get('tipo_usuario')
    user_id = session.get('user_id')
    
    if tipo_usuario == 'cliente':
        servicos = Servico.query.join(Veiculo).filter(
            Veiculo.usuario_id == user_id
        ).order_by(Servico.data_entrada.desc()).all()
    elif tipo_usuario == 'mecanico':
        servicos = Servico.query.filter_by(
            mecanico_responsavel_id=user_id
        ).order_by(Servico.data_entrada.desc()).all()
    else:  # gerente
        servicos = Servico.query.order_by(Servico.data_entrada.desc()).all()
    
    for servico in servicos:
        servico.status_class = get_status_class(servico.status)
        servico.status_display = get_status_display(servico.status)
    
    return render_template('servicos_list.html', servicos=servicos)


@bp.route('/servicos/novo', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('mecanico', 'gerente')
def servico_create():
    if request.method == 'POST':
        servico = Servico(
            veiculo_id=int(request.form.get('veiculo_id')),
            descricao=request.form.get('descricao'),
            observacoes=request.form.get('observacoes'),
            data_entrada=datetime.strptime(request.form.get('data_entrada'), '%Y-%m-%d'),
            status=StatusServico[request.form.get('status', 'AGUARDANDO_ORCAMENTO').upper()]
        )
        
        if request.form.get('data_previsao'):
            servico.data_previsao = datetime.strptime(request.form.get('data_previsao'), '%Y-%m-%d')
        
        if request.form.get('mecanico_responsavel_id'):
            servico.mecanico_responsavel_id = int(request.form.get('mecanico_responsavel_id'))
        
        db.session.add(servico)
        db.session.commit()
        
        flash('Serviço cadastrado com sucesso!', 'success')
        return redirect(url_for('views.servicos_list'))
    
    # GET
    if session.get('tipo_usuario') == 'cliente':
        veiculos = Veiculo.query.filter_by(usuario_id=session.get('user_id')).all()
    else:
        veiculos = Veiculo.query.all()
    
    mecanicos = Usuario.query.filter_by(tipo='mecanico').all()
    
    return render_template('servico_form.html', 
                         servico=None, 
                         veiculos=veiculos, 
                         mecanicos=mecanicos)


@bp.route('/servicos/<int:id>')
@login_required
def servico_detail(id):
    servico = Servico.query.get_or_404(id)
    
    # Verificar permissão
    tipo_usuario = session.get('tipo_usuario')
    user_id = session.get('user_id')
    
    if tipo_usuario == 'cliente' and servico.veiculo.usuario_id != user_id:
        flash('Você não tem permissão para ver este serviço', 'danger')
        return redirect(url_for('views.servicos_list'))
    
    if tipo_usuario == 'mecanico' and servico.mecanico_responsavel_id != user_id:
        flash('Você não tem permissão para ver este serviço', 'danger')
        return redirect(url_for('views.servicos_list'))
    
    servico.status_class = get_status_class(servico.status)
    servico.status_display = get_status_display(servico.status)
    
    orcamentos = Orcamento.query.filter_by(servico_id=id).order_by(Orcamento.data_orcamento.desc()).all()
    
    return render_template('servico_detail.html', servico=servico, orcamentos=orcamentos)


@bp.route('/servicos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('mecanico', 'gerente')
def servico_edit(id):
    servico = Servico.query.get_or_404(id)
    
    if request.method == 'POST':
        servico.veiculo_id = int(request.form.get('veiculo_id'))
        servico.descricao = request.form.get('descricao')
        servico.observacoes = request.form.get('observacoes')
        servico.data_entrada = datetime.strptime(request.form.get('data_entrada'), '%Y-%m-%d')
        servico.status = StatusServico[request.form.get('status').upper()]
        
        if request.form.get('data_previsao'):
            servico.data_previsao = datetime.strptime(request.form.get('data_previsao'), '%Y-%m-%d')
        
        if request.form.get('mecanico_responsavel_id'):
            servico.mecanico_responsavel_id = int(request.form.get('mecanico_responsavel_id'))
        
        db.session.commit()
        
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('views.servico_detail', id=id))
    
    veiculos = Veiculo.query.all()
    mecanicos = Usuario.query.filter_by(tipo='mecanico').all()
    
    return render_template('servico_form.html', 
                         servico=servico, 
                         veiculos=veiculos, 
                         mecanicos=mecanicos)


@bp.route('/orcamentos/novo', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('mecanico', 'gerente')
def orcamento_create():
    servico_id = request.args.get('servico_id')
    servico = Servico.query.get_or_404(servico_id)
    
    if request.method == 'POST':
        valor_mao_obra = float(request.form.get('valor_mao_obra'))
        valor_pecas = float(request.form.get('valor_pecas'))
        
        orcamento = Orcamento(
            servico_id=servico.id,
            valor_mao_obra=valor_mao_obra,
            valor_pecas=valor_pecas,
            valor_total=valor_mao_obra + valor_pecas,
            data_orcamento=datetime.now()
        )
        
        db.session.add(orcamento)
        db.session.commit()
        
        flash('Orçamento criado com sucesso!', 'success')
        return redirect(url_for('views.servico_detail', id=servico.id))
    
    return redirect(url_for('views.servico_detail', id=servico.id))


@bp.route('/orcamentos/<int:id>/aprovar', methods=['POST'])
@login_required
@tipo_usuario_required('cliente')
def orcamento_approve(id):
    orcamento = Orcamento.query.get_or_404(id)
    servico = orcamento.servico
    
    # Verificar se é o dono do veículo
    if servico.veiculo.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para aprovar este orçamento', 'danger')
        return redirect(url_for('views.servicos_list'))
    
    orcamento.aprovado = True
    servico.status = StatusServico.ORCAMENTO_APROVADO
    servico.valor_mao_obra = orcamento.valor_mao_obra
    servico.valor_pecas = orcamento.valor_pecas
    servico.valor_total = orcamento.valor_total
    
    db.session.commit()
    
    flash('Orçamento aprovado com sucesso!', 'success')
    return redirect(url_for('views.servico_detail', id=servico.id))


# ============= Usuários (Gerente) =============

@bp.route('/usuarios')
@login_required
@tipo_usuario_required('gerente')
def usuarios_list():
    usuarios = Usuario.query.all()
    return render_template('usuarios_list.html', usuarios=usuarios)


@bp.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('gerente')
def usuario_create():
    if request.method == 'POST':
        usuario = Usuario(
            nome=request.form.get('nome'),
            email=request.form.get('email'),
            telefone=request.form.get('telefone'),
            tipo_usuario=request.form.get('tipo_usuario')
        )
        usuario.definir_senha(request.form.get('senha'))
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('views.usuarios_list'))
    
    return render_template('usuario_form.html', usuario=None)


# ============= Helpers =============

def get_status_class(status):
    """Retorna a classe Bootstrap para o badge de status"""
    classes = {
        StatusServico.AGUARDANDO_ORCAMENTO: 'secondary',
        StatusServico.ORCAMENTO_APROVADO: 'info',
        StatusServico.EM_ANDAMENTO: 'warning',
        StatusServico.CONCLUIDO: 'success',
        StatusServico.CANCELADO: 'danger'
    }
    return classes.get(status, 'secondary')


def get_status_display(status):
    """Retorna o texto amigável do status"""
    displays = {
        StatusServico.AGUARDANDO_ORCAMENTO: 'Aguardando Orçamento',
        StatusServico.ORCAMENTO_APROVADO: 'Orçamento Aprovado',
        StatusServico.EM_ANDAMENTO: 'Em Andamento',
        StatusServico.CONCLUIDO: 'Concluído',
        StatusServico.CANCELADO: 'Cancelado'
    }
    return displays.get(status, str(status))
