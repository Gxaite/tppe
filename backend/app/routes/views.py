from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func, extract
from app.models import db, Usuario, Veiculo, Servico, Orcamento, StatusServico, TipoUsuario
from functools import wraps

bp = Blueprint('views', __name__)


# ============= Landing Page =============

@bp.route('/')
def landing():
    """Landing page institucional"""
    if 'user_id' in session:
        return redirect(url_for('views.dashboard'))
    return render_template('landing.html')


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
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefone = request.form.get('telefone', '').strip()
        senha = request.form.get('senha')
        senha_confirm = request.form.get('senha_confirm')

        # Validação de nome (mínimo 3 caracteres)
        if not nome or len(nome) < 3:
            flash('O nome deve ter pelo menos 3 caracteres', 'danger')
            return render_template('register.html')

        # Validação de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_regex, email):
            flash('Digite um email válido', 'danger')
            return render_template('register.html')

        # Validação de telefone (11 dígitos)
        telefone_digits = re.sub(r'\D', '', telefone)
        if len(telefone_digits) != 11:
            flash('O telefone deve ter 11 dígitos (DDD + número)', 'danger')
            return render_template('register.html')

        # Validação de senha
        if not senha or len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres', 'danger')
            return render_template('register.html')

        if senha != senha_confirm:
            flash('As senhas não coincidem', 'danger')
            return render_template('register.html')

        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'danger')
            return render_template('register.html')

        # Criar usuário SEMPRE como cliente (apenas gerentes podem criar outros tipos)
        usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone_digits,  # Salva apenas os dígitos
            tipo='cliente'
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
    ).order_by(Servico.criado_em.desc()).limit(10).all()

    return render_template(
        'dashboard_cliente.html',
        stats=stats,
        veiculos=veiculos[:5],
        servicos=servicos
    )


def dashboard_mecanico(user_id):
    # Estatísticas - Aguardando orçamento: TODOS não atribuídos OU atribuídos a mim
    aguardando_orcamento = Servico.query.filter(
        Servico.status == StatusServico.AGUARDANDO_ORCAMENTO,
        db.or_(
            Servico.mecanico_id == None,
            Servico.mecanico_id == user_id
        )
    ).count()

    stats = {
        'aguardando_orcamento': aguardando_orcamento,
        'em_andamento': Servico.query.filter_by(
            mecanico_id=user_id,
            status=StatusServico.EM_ANDAMENTO
        ).count(),
        'concluidos_mes': Servico.query.filter_by(
            mecanico_id=user_id,
            status=StatusServico.CONCLUIDO
        ).count(),
        'total_servicos': Servico.query.filter_by(mecanico_id=user_id).count()
    }

    # Serviços: TODOS aguardando orçamento (não atribuídos) + meus serviços em andamento
    servicos = Servico.query.filter(
        db.or_(
            # Serviços aguardando orçamento sem mecânico atribuído
            db.and_(
                Servico.status == StatusServico.AGUARDANDO_ORCAMENTO,
                Servico.mecanico_id == None
            ),
            # Meus serviços em qualquer status ativo
            db.and_(
                Servico.mecanico_id == user_id,
                Servico.status.in_([
                    StatusServico.AGUARDANDO_ORCAMENTO,
                    StatusServico.ORCAMENTO_APROVADO,
                    StatusServico.EM_ANDAMENTO
                ])
            )
        )
    ).order_by(Servico.criado_em.desc()).all()

    return render_template('dashboard_mecanico.html', stats=stats, servicos=servicos)


def dashboard_gerente():
    # Estatísticas gerais
    stats = {
        'total_clientes': Usuario.query.filter_by(tipo=TipoUsuario.CLIENTE).count(),
        'receita_mensal': db.session.query(func.sum(Servico.valor)).filter(
            Servico.status == StatusServico.CONCLUIDO
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
    mecanicos = Usuario.query.filter_by(tipo=TipoUsuario.MECANICO).all()
    mecanicos_stats = []
    for mecanico in mecanicos:
        mecanicos_stats.append({
            'nome': mecanico.nome,
            'aguardando': Servico.query.filter_by(
                mecanico_id=mecanico.id,
                status=StatusServico.AGUARDANDO_ORCAMENTO
            ).count(),
            'em_andamento': Servico.query.filter_by(
                mecanico_id=mecanico.id,
                status=StatusServico.EM_ANDAMENTO
            ).count(),
            'concluidos': Servico.query.filter_by(
                mecanico_id=mecanico.id,
                status=StatusServico.CONCLUIDO
            ).filter(
                extract('month', Servico.data_conclusao) == datetime.now().month,
                extract('year', Servico.data_conclusao) == datetime.now().year
            ).count(),
            'total': Servico.query.filter_by(mecanico_id=mecanico.id).count()
        })

    # Serviços recentes
    servicos = Servico.query.order_by(Servico.criado_em.desc()).limit(15).all()

    return render_template(
        'dashboard_gerente.html',
        stats=stats,
        mecanicos_stats=mecanicos_stats,
        servicos=servicos
    )


# ============= Veículos =============

@bp.route('/veiculos')
@login_required
def veiculos_list():
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'cliente':
        veiculos = Veiculo.query.filter_by(usuario_id=session.get('user_id')).all()
        return render_template('veiculos_list.html', veiculos=veiculos, agrupado=False)
    else:
        # Para gerente/mecânico: agrupar veículos por cliente
        clientes = Usuario.query.filter_by(tipo=TipoUsuario.CLIENTE).order_by(Usuario.nome).all()
        veiculos_por_cliente = []
        for cliente in clientes:
            veiculos_cliente = Veiculo.query.filter_by(usuario_id=cliente.id).all()
            if veiculos_cliente:
                veiculos_por_cliente.append({
                    'cliente': cliente,
                    'veiculos': veiculos_cliente
                })

        return render_template('veiculos_list.html', veiculos_por_cliente=veiculos_por_cliente, agrupado=True)


@bp.route('/veiculos/novo', methods=['GET', 'POST'])
@login_required
def veiculo_create():
    if request.method == 'POST':
        placa = request.form.get('placa').upper()

        # Verificar se placa já existe
        if Veiculo.query.filter_by(placa=placa).first():
            flash('Placa já cadastrada no sistema!', 'danger')
            return render_template('veiculo_form.html', veiculo=None)

        veiculo = Veiculo(
            marca=request.form.get('marca'),
            modelo=request.form.get('modelo'),
            ano=int(request.form.get('ano')),
            placa=placa,
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
    veiculo = db.get_or_404(Veiculo, id)

    # Verificar permissão
    if session.get('tipo_usuario') == 'cliente' and veiculo.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para ver este veículo', 'danger')
        return redirect(url_for('views.veiculos_list'))

    servicos = Servico.query.filter_by(veiculo_id=id).order_by(Servico.criado_em.desc()).all()

    return render_template('veiculo_detail.html', veiculo=veiculo, servicos=servicos)


@bp.route('/veiculos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def veiculo_edit(id):
    veiculo = db.get_or_404(Veiculo, id)

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
    veiculo = db.get_or_404(Veiculo, id)

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
        ).order_by(Servico.criado_em.desc()).all()
    elif tipo_usuario == 'mecanico':
        # Mecânico vê: serviços aguardando orçamento (sem mecânico) + seus serviços
        servicos = Servico.query.filter(
            db.or_(
                db.and_(
                    Servico.status == StatusServico.AGUARDANDO_ORCAMENTO,
                    Servico.mecanico_id == None
                ),
                Servico.mecanico_id == user_id
            )
        ).order_by(Servico.criado_em.desc()).all()
    else:  # gerente
        servicos = Servico.query.order_by(Servico.criado_em.desc()).all()

    return render_template('servicos_list.html', servicos=servicos)


@bp.route('/servicos/solicitar', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('cliente')
def servico_solicitar():
    """Permite que clientes solicitem um orçamento/serviço"""
    if request.method == 'POST':
        veiculo_id = request.form.get('veiculo_id')

        # Verificar se veículo pertence ao cliente
        veiculo = db.get_or_404(Veiculo, veiculo_id)
        if veiculo.usuario_id != session.get('user_id'):
            flash('Você não tem permissão para solicitar serviço para este veículo', 'danger')
            return redirect(url_for('views.servicos_list'))

        servico = Servico(
            veiculo_id=int(veiculo_id),
            descricao=request.form.get('descricao'),
            observacoes=request.form.get('observacoes'),
            status=StatusServico.AGUARDANDO_ORCAMENTO
        )

        db.session.add(servico)
        db.session.commit()

        flash('Solicitação de orçamento enviada com sucesso! Aguarde nosso retorno.', 'success')
        return redirect(url_for('views.servicos_list'))

    # GET - Listar apenas veículos do cliente
    veiculos = Veiculo.query.filter_by(usuario_id=session.get('user_id')).all()

    if not veiculos:
        flash('Você precisa cadastrar um veículo antes de solicitar um serviço.', 'warning')
        return redirect(url_for('views.veiculo_create'))

    return render_template('servico_solicitar.html', veiculos=veiculos)


@bp.route('/servicos/novo', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('mecanico', 'gerente')
def servico_create():
    if request.method == 'POST':
        servico = Servico(
            veiculo_id=int(request.form.get('veiculo_id')),
            descricao=request.form.get('descricao'),
            observacoes=request.form.get('observacoes'),
            status=StatusServico[request.form.get('status', 'AGUARDANDO_ORCAMENTO').upper()]
        )

        # Data de entrada (criado_em) será automaticamente definida pelo model

        if request.form.get('data_previsao'):
            servico.data_previsao = datetime.strptime(request.form.get('data_previsao'), '%Y-%m-%d')

        if request.form.get('mecanico_id'):
            servico.mecanico_id = int(request.form.get('mecanico_id'))

        db.session.add(servico)
        db.session.commit()

        flash('Serviço cadastrado com sucesso!', 'success')
        return redirect(url_for('views.servicos_list'))

    # GET
    if session.get('tipo_usuario') == 'cliente':
        veiculos = Veiculo.query.filter_by(usuario_id=session.get('user_id')).all()
    else:
        veiculos = Veiculo.query.all()

    mecanicos = Usuario.query.filter_by(tipo=TipoUsuario.MECANICO).all()

    return render_template(
        'servico_form.html',
        servico=None,
        veiculos=veiculos,
        mecanicos=mecanicos
    )


@bp.route('/servicos/<int:id>')
@login_required
def servico_detail(id):
    servico = db.get_or_404(Servico, id)

    # Verificar permissão
    tipo_usuario = session.get('tipo_usuario')
    user_id = session.get('user_id')

    if tipo_usuario == 'cliente' and servico.veiculo.usuario_id != user_id:
        flash('Você não tem permissão para ver este serviço', 'danger')
        return redirect(url_for('views.servicos_list'))

    # Mecânico pode ver: seus serviços OU serviços aguardando orçamento sem mecânico
    if tipo_usuario == 'mecanico':
        pode_ver = (
            servico.mecanico_id == user_id or
            (servico.status == StatusServico.AGUARDANDO_ORCAMENTO and servico.mecanico_id is None)
        )
        if not pode_ver:
            flash('Você não tem permissão para ver este serviço', 'danger')
            return redirect(url_for('views.servicos_list'))

    orcamentos = Orcamento.query.filter_by(servico_id=id).order_by(Orcamento.criado_em.desc()).all()

    return render_template('servico_detail.html', servico=servico, orcamentos=orcamentos)


@bp.route('/servicos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@tipo_usuario_required('mecanico', 'gerente')
def servico_edit(id):
    servico = db.get_or_404(Servico, id)

    if request.method == 'POST':
        servico.veiculo_id = int(request.form.get('veiculo_id'))
        servico.descricao = request.form.get('descricao')
        servico.observacoes = request.form.get('observacoes')
        servico.status = StatusServico[request.form.get('status').upper()]

        if request.form.get('data_previsao'):
            servico.data_previsao = datetime.strptime(request.form.get('data_previsao'), '%Y-%m-%d')

        if request.form.get('mecanico_id'):
            servico.mecanico_id = int(request.form.get('mecanico_id'))

        db.session.commit()

        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('views.servico_detail', id=id))

    veiculos = Veiculo.query.all()
    mecanicos = Usuario.query.filter_by(tipo=TipoUsuario.MECANICO).all()

    return render_template(
        'servico_form.html',
        servico=servico,
        veiculos=veiculos,
        mecanicos=mecanicos
    )


@bp.route('/orcamentos/novo', methods=['POST'])
@login_required
@tipo_usuario_required('mecanico', 'gerente')
def orcamento_create():
    servico_id = request.args.get('servico_id')
    if not servico_id:
        flash('Serviço não especificado', 'danger')
        return redirect(url_for('views.servicos_list'))

    servico = db.get_or_404(Servico, servico_id)

    # Suporta ambos os formatos: valor único ou separado
    valor_mao_obra = float(request.form.get('valor_mao_obra', 0) or 0)
    valor_pecas = float(request.form.get('valor_pecas', 0) or 0)
    valor = float(request.form.get('valor', 0) or 0)

    # Se valor não foi enviado, calcula a partir dos componentes
    if valor == 0 and (valor_mao_obra > 0 or valor_pecas > 0):
        valor = valor_mao_obra + valor_pecas

    if valor <= 0:
        flash('O valor do orçamento deve ser maior que zero', 'danger')
        return redirect(url_for('views.servico_detail', id=servico.id))

    descricao = request.form.get('descricao', '').strip()
    if not descricao:
        flash('A descrição do orçamento é obrigatória', 'danger')
        return redirect(url_for('views.servico_detail', id=servico.id))

    orcamento = Orcamento(
        servico_id=servico.id,
        descricao=descricao,
        valor=valor
    )

    # Se mecânico está criando o orçamento, atribuir ele ao serviço
    if session.get('tipo_usuario') == 'mecanico' and not servico.mecanico_id:
        servico.mecanico_id = session.get('user_id')

    db.session.add(orcamento)
    db.session.commit()

    flash('Orçamento criado com sucesso!', 'success')
    return redirect(url_for('views.servico_detail', id=servico.id))


@bp.route('/orcamentos/<int:id>/aprovar', methods=['POST'])
@login_required
@tipo_usuario_required('cliente')
def orcamento_approve(id):
    orcamento = db.get_or_404(Orcamento, id)
    servico = orcamento.servico

    # Verificar se é o dono do veículo
    if servico.veiculo.usuario_id != session.get('user_id'):
        flash('Você não tem permissão para aprovar este orçamento', 'danger')
        return redirect(url_for('views.servicos_list'))

    servico.status = StatusServico.ORCAMENTO_APROVADO
    servico.valor = orcamento.valor

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
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefone = request.form.get('telefone', '').strip()
        tipo_usuario = request.form.get('tipo_usuario')
        senha = request.form.get('senha')

        # Validação de nome
        if not nome or len(nome) < 3:
            flash('O nome deve ter pelo menos 3 caracteres', 'danger')
            return render_template('usuario_form.html', usuario=None)

        # Validação de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email or not re.match(email_regex, email):
            flash('Digite um email válido', 'danger')
            return render_template('usuario_form.html', usuario=None)

        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'danger')
            return render_template('usuario_form.html', usuario=None)

        # Validação de telefone (11 dígitos)
        telefone_digits = re.sub(r'\D', '', telefone)
        if telefone and len(telefone_digits) != 11:
            flash('O telefone deve ter 11 dígitos', 'danger')
            return render_template('usuario_form.html', usuario=None)

        # Validação de tipo de usuário
        if tipo_usuario not in ['cliente', 'mecanico', 'gerente']:
            flash('Tipo de usuário inválido', 'danger')
            return render_template('usuario_form.html', usuario=None)

        # Validação de senha
        if not senha or len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres', 'danger')
            return render_template('usuario_form.html', usuario=None)

        usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone_digits if telefone_digits else None,
            tipo=tipo_usuario
        )
        usuario.set_senha(senha)

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
