import sys
import pytest
from unittest.mock import patch, mock_open
from PySide6.QtCore import QCoreApplication
import pyautogui
from src.motor_autogui import MotorRPAThread

@pytest.fixture(scope="session", autouse=True)
def qt_app():
    """Garante uma instância ativa do Qt para o funcionamento dos Signals."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    return app

def test_parar_thread():
    motor = MotorRPAThread("Fluxo Teste")
    assert motor.rodando is True
    motor.parar()
    assert motor.rodando is False

@patch("src.motor_autogui.pyautogui")
def test_move_and_click(mock_pyautogui):
    motor = MotorRPAThread("Fluxo Teste")
    motor.move_and_click((100, 200))
    mock_pyautogui.moveTo.assert_called_once_with((100, 200), duration=0.1)
    mock_pyautogui.click.assert_called_once()

@patch("src.motor_autogui.pyperclip")
@patch("src.motor_autogui.pyautogui")
def test_inserir_texto(mock_pyautogui, mock_pyperclip):
    motor = MotorRPAThread("Fluxo Teste")
    motor.inserir_texto("12345678900")
    mock_pyperclip.copy.assert_called_once_with("12345678900")
    mock_pyautogui.hotkey.assert_called_once_with("ctrl", "v")
    mock_pyautogui.press.assert_called_once_with("enter")

@patch("src.motor_autogui.time.sleep")
@patch("src.motor_autogui.pyautogui.locateCenterOnScreen")
def test_localizar_sucesso(mock_locate, mock_sleep):
    mock_locate.return_value = (500, 300)
    motor = MotorRPAThread("Fluxo Teste")
    resultado = motor.localizar("img.png")
    assert resultado == (500, 300)

@patch("src.motor_autogui.time.sleep")
@patch("src.motor_autogui.pyautogui.locateOnScreen")
def test_localizar_popup_falha_limite(mock_locate, mock_sleep):
    mock_locate.side_effect = pyautogui.ImageNotFoundException
    motor = MotorRPAThread("Fluxo Teste")
    with pytest.raises(Exception, match="Interrompido: imagem não encontrada"):
        motor.motor_de_busca("img.png", limite_tentativas=2, retornar_centro=False)

def test_motor_de_busca_interrompido():
    motor = MotorRPAThread("Fluxo Teste")
    motor.parar()
    with pytest.raises(Exception, match="interrompida pelo usuário"):
        motor.motor_de_busca("img.png", limite_tentativas=2)

#
#
@patch("src.motor_autogui.os.path.exists", return_value=False)
def test_integracao_arquivo_inexistente(mock_exists):
    motor = MotorRPAThread("Urgência")
    erros = []
    motor.erro.connect(erros.append)
    motor.run()
    assert erros == ["Arquivo de configuração não encontrado."]

@patch("src.motor_autogui.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"Urgência": []}')
def test_integracao_fluxo_vazio(mock_file, mock_exists):
    motor = MotorRPAThread("Urgência")
    erros = []
    motor.erro.connect(erros.append)
    motor.run()
    assert erros == ["O fluxo 'Urgência' está vazio."]

@patch("src.motor_autogui.time.sleep")
@patch("src.motor_autogui.pyperclip")
@patch("src.motor_autogui.pyautogui")
@patch("src.motor_autogui.os.path.exists", return_value=True)
def test_integracao_execucao_completa_acoes(mock_exists, mock_pyautogui, mock_pyperclip, mock_sleep):
    json_simulado = '''
    {
        "Fluxo Completo": [
            {"campo": "Botão Iniciar", "caminho": "btn.png", "acao": "Procurar e Clicar", "parametro": ""},
            {"campo": "Atalho Tela", "caminho": "pop.png", "acao": "Procurar e Pressionar Teclas", "parametro": "tab, enter"},
            {"campo": "Campo CPF", "caminho": "cpf.png", "acao": "Procurar e Digitar texto", "parametro": "00011122233"},
            {"campo": "Campo Nome", "caminho": "", "acao": "Digitar texto", "parametro": "Paciente Teste"},
            {"campo": "Confirmar", "caminho": "", "acao": "Pressionar Teclas", "parametro": "enter"},
            {"campo": "Espera Sistema", "caminho": "", "acao": "Aguardar (Segundos)", "parametro": "1"}
        ]
    }
    '''
    mock_pyautogui.locateCenterOnScreen.return_value = (150, 150)
    mock_pyautogui.locateOnScreen.return_value = (10, 10, 50, 50)

    motor = MotorRPAThread("Fluxo Completo")
    status_recebidos = []
    concluido = []
    
    motor.status_atualizado.connect(status_recebidos.append)
    motor.finalizado.connect(lambda: concluido.append(True))

    with patch("builtins.open", mock_open(read_data=json_simulado)):
        motor.run()

    assert len(status_recebidos) == 6
    assert concluido == [True]