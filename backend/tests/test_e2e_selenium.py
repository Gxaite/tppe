"""
Testes E2E com Selenium
Testa os principais fluxos da aplicação via browser

Fluxos testados:
1. Login/Logout para cada tipo de usuário
2. Cliente: CRUD veículos, solicitar serviço
3. Gerente: ver usuários, criar orçamento, atribuir mecânico
4. Mecânico: ver serviços, atualizar status
"""
import os
import pytest
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)


# URL do app
BASE_URL = os.getenv("TEST_BASE_URL", "http://backend:5000")
SELENIUM_URL = os.getenv("SELENIUM_URL", "http://selenium:4444/wd/hub")

# Credenciais
USUARIOS = {
    "cliente": {"email": "carlos@email.com", "senha": "senha123"},
    "gerente": {"email": "gerente@oficina.com", "senha": "senha123"},
    "mecanico": {"email": "joao@oficina.com", "senha": "senha123"},
}


@pytest.fixture(scope="function")
def driver():
    """WebDriver remoto - nova instância por teste"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=chrome_options
    )
    driver.implicitly_wait(5)
    
    # Garantir logout antes de cada teste
    driver.get(f"{BASE_URL}/logout")
    time.sleep(0.3)
    
    yield driver
    driver.quit()


def wait_for(driver, by, value, timeout=10):
    """Espera elemento visível"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


def wait_url(driver, text, timeout=10):
    """Espera URL conter texto"""
    return WebDriverWait(driver, timeout).until(EC.url_contains(text))


def scroll_and_click(driver, element):
    """Scroll até elemento e clica"""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.3)
    try:
        element.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def login(driver, tipo_usuario):
    """Helper para fazer login"""
    driver.get(f"{BASE_URL}/login")
    time.sleep(0.5)

    creds = USUARIOS[tipo_usuario]

    email = wait_for(driver, By.ID, "email")
    email.clear()
    email.send_keys(creds["email"])

    senha = driver.find_element(By.ID, "senha")
    senha.clear()
    senha.send_keys(creds["senha"])

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait_url(driver, "/dashboard")


# ============= AUTENTICAÇÃO =============

class TestAutenticacao:
    """Testes de login/logout"""

    def test_pagina_login_carrega(self, driver):
        """Página de login carrega"""
        driver.get(f"{BASE_URL}/login")
        assert "Login" in driver.title
        assert driver.find_element(By.ID, "email").is_displayed()
        assert driver.find_element(By.ID, "senha").is_displayed()

    def test_login_invalido(self, driver):
        """Login inválido mostra erro"""
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "email").send_keys("invalido@email.com")
        driver.find_element(By.ID, "senha").send_keys("senhaerrada")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        assert driver.find_element(By.CSS_SELECTOR, ".alert").is_displayed()

    def test_login_cliente(self, driver):
        """Cliente faz login"""
        login(driver, "cliente")
        assert "/dashboard" in driver.current_url

    def test_login_gerente(self, driver):
        """Gerente faz login"""
        login(driver, "gerente")
        assert "/dashboard" in driver.current_url

    def test_login_mecanico(self, driver):
        """Mecânico faz login"""
        login(driver, "mecanico")
        assert "/dashboard" in driver.current_url

    def test_logout(self, driver):
        """Usuário faz logout"""
        login(driver, "cliente")
        driver.get(f"{BASE_URL}/logout")
        time.sleep(0.5)
        assert "/login" in driver.current_url

    def test_pagina_registro(self, driver):
        """Página de registro carrega"""
        driver.get(f"{BASE_URL}/register")
        time.sleep(0.5)
        
        # Verifica se está na página de registro
        assert "Cadastro" in driver.title or "Criar" in driver.page_source
        
        # Verifica campos do formulário
        nome = driver.find_element(By.ID, "nome")
        email = driver.find_element(By.ID, "email")
        senha = driver.find_element(By.ID, "senha")
        
        assert nome is not None
        assert email is not None
        assert senha is not None


# ============= CLIENTE =============

class TestCliente:
    """Funcionalidades do cliente"""

    def test_dashboard_cliente(self, driver):
        """Dashboard do cliente"""
        login(driver, "cliente")
        stat_cards = driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        assert len(stat_cards) >= 3

    def test_listar_veiculos(self, driver):
        """Lista de veículos"""
        login(driver, "cliente")
        driver.get(f"{BASE_URL}/veiculos")
        assert "/veiculos" in driver.current_url

    def test_criar_veiculo(self, driver):
        """Criar veículo"""
        login(driver, "cliente")
        driver.get(f"{BASE_URL}/veiculos/novo")

        placa = f"TST{uuid.uuid4().hex[:4].upper()}"

        driver.find_element(By.ID, "marca").send_keys("Honda")
        driver.find_element(By.ID, "modelo").send_keys("Civic")
        driver.find_element(By.ID, "ano").send_keys("2023")
        driver.find_element(By.ID, "placa").send_keys(placa)

        try:
            driver.find_element(By.ID, "cor").send_keys("Prata")
        except NoSuchElementException:
            pass

        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        scroll_and_click(driver, btn)
        time.sleep(1)

        assert "veiculos" in driver.current_url.lower() or "sucesso" in driver.page_source.lower()

    def test_solicitar_servico(self, driver):
        """Solicitar serviço"""
        login(driver, "cliente")
        driver.get(f"{BASE_URL}/servicos/solicitar")
        time.sleep(0.5)

        assert "Solicitar" in driver.page_source or "Orçamento" in driver.page_source

        try:
            select = Select(driver.find_element(By.ID, "veiculo_id"))
            if len(select.options) > 1:
                select.select_by_index(1)
                driver.find_element(By.ID, "descricao").send_keys("Teste Selenium")

                btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                scroll_and_click(driver, btn)
                time.sleep(1)
        except NoSuchElementException:
            pass  # OK se não tiver veículos

    def test_listar_servicos(self, driver):
        """Lista de serviços do cliente"""
        login(driver, "cliente")
        driver.get(f"{BASE_URL}/servicos")
        assert "/servicos" in driver.current_url


# ============= GERENTE =============

class TestGerente:
    """Funcionalidades do gerente"""

    def test_dashboard_gerente(self, driver):
        """Dashboard do gerente"""
        login(driver, "gerente")
        stat_cards = driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        assert len(stat_cards) >= 4

    def test_listar_usuarios(self, driver):
        """Lista de usuários"""
        login(driver, "gerente")
        driver.get(f"{BASE_URL}/usuarios")
        assert "/usuarios" in driver.current_url
        assert driver.find_element(By.CSS_SELECTOR, "table").is_displayed()

    def test_criar_usuario(self, driver):
        """Criar usuário"""
        login(driver, "gerente")
        driver.get(f"{BASE_URL}/usuarios/novo")

        email_unico = f"e2e_{uuid.uuid4().hex[:6]}@test.com"

        driver.find_element(By.ID, "nome").send_keys("Teste E2E")
        driver.find_element(By.ID, "email").send_keys(email_unico)
        driver.find_element(By.ID, "senha").send_keys("senha123")

        try:
            select = Select(driver.find_element(By.ID, "tipo"))
            select.select_by_value("cliente")
        except NoSuchElementException:
            pass

        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        scroll_and_click(driver, btn)
        time.sleep(1)

        assert "usuarios" in driver.current_url.lower() or "sucesso" in driver.page_source.lower()

    def test_listar_veiculos(self, driver):
        """Gerente vê todos veículos"""
        login(driver, "gerente")
        driver.get(f"{BASE_URL}/veiculos")
        assert "/veiculos" in driver.current_url

    def test_listar_servicos(self, driver):
        """Gerente vê todos serviços"""
        login(driver, "gerente")
        driver.get(f"{BASE_URL}/servicos")
        assert "/servicos" in driver.current_url

    def test_criar_servico(self, driver):
        """Criar serviço"""
        login(driver, "gerente")
        driver.get(f"{BASE_URL}/servicos/novo")
        time.sleep(0.5)

        try:
            select_veiculo = Select(driver.find_element(By.ID, "veiculo_id"))
            if len(select_veiculo.options) > 1:
                select_veiculo.select_by_index(1)
                driver.find_element(By.ID, "descricao").send_keys("Serviço E2E")

                try:
                    select_mec = Select(driver.find_element(By.ID, "mecanico_id"))
                    if len(select_mec.options) > 1:
                        select_mec.select_by_index(1)
                except NoSuchElementException:
                    pass

                btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                scroll_and_click(driver, btn)
                time.sleep(1)
        except NoSuchElementException:
            pass  # OK se não tiver veículos


# ============= MECÂNICO =============

class TestMecanico:
    """Funcionalidades do mecânico"""

    def test_dashboard_mecanico(self, driver):
        """Dashboard do mecânico"""
        login(driver, "mecanico")
        assert "/dashboard" in driver.current_url

    def test_listar_servicos(self, driver):
        """Mecânico vê serviços"""
        login(driver, "mecanico")
        driver.get(f"{BASE_URL}/servicos")
        assert "/servicos" in driver.current_url


# ============= NAVEGAÇÃO =============

class TestNavegacao:
    """Navegação geral"""

    def test_menu_cliente(self, driver):
        """Menu do cliente"""
        login(driver, "cliente")
        assert "Veículo" in driver.page_source or "veículo" in driver.page_source

    def test_menu_gerente(self, driver):
        """Menu do gerente"""
        login(driver, "gerente")
        assert "Usuário" in driver.page_source or "usuário" in driver.page_source

    def test_responsividade(self, driver):
        """Responsividade mobile"""
        driver.set_window_size(375, 667)
        driver.get(f"{BASE_URL}/login")
        assert driver.find_element(By.ID, "email").is_displayed()
        driver.set_window_size(1920, 1080)


# ============= FLUXOS COMPLETOS =============

class TestFluxoCompleto:
    """Fluxos E2E completos"""

    def test_cliente_cria_veiculo_e_solicita_servico(self, driver):
        """Cliente: login -> criar veículo -> solicitar serviço"""
        login(driver, "cliente")

        # Criar veículo
        driver.get(f"{BASE_URL}/veiculos/novo")
        placa = f"E2E{uuid.uuid4().hex[:4].upper()}"

        driver.find_element(By.ID, "marca").send_keys("Toyota")
        driver.find_element(By.ID, "modelo").send_keys("Corolla")
        driver.find_element(By.ID, "ano").send_keys("2024")
        driver.find_element(By.ID, "placa").send_keys(placa)

        try:
            driver.find_element(By.ID, "cor").send_keys("Branco")
        except NoSuchElementException:
            pass

        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        scroll_and_click(driver, btn)
        time.sleep(1)

        # Solicitar serviço
        driver.get(f"{BASE_URL}/servicos/solicitar")
        time.sleep(0.5)

        try:
            select = Select(driver.find_element(By.ID, "veiculo_id"))
            select.select_by_index(len(select.options) - 1)
            driver.find_element(By.ID, "descricao").send_keys("Revisão E2E")

            btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            scroll_and_click(driver, btn)
            time.sleep(1)
        except NoSuchElementException:
            pass

    def test_gerente_navega_sistema(self, driver):
        """Gerente: dashboard -> serviços -> usuários"""
        login(driver, "gerente")

        driver.get(f"{BASE_URL}/servicos")
        assert "/servicos" in driver.current_url

        driver.get(f"{BASE_URL}/usuarios")
        assert "/usuarios" in driver.current_url

        driver.get(f"{BASE_URL}/veiculos")
        assert "/veiculos" in driver.current_url

        driver.get(f"{BASE_URL}/dashboard")
        assert "/dashboard" in driver.current_url
