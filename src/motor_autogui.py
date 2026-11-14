import pyautogui
import pyperclip
import time
import os
import sys
import json
from PySide6.QtCore import QThread, Signal

class Config:
    DELAY_BUSCA = 0.2
    DELAY_CURTO = 0.3
    DELAY_PADRAO = 0.5
PASTA_DATA = os.path.join(os.path.dirname(__file__), 'data')    
ARQUIVO_CONFIG = os.path.join(PASTA_DATA, 'config.json')
class MotorRPAThread(QThread):
    """
    Thread dedicada à execução de fluxos de automação RPA em segundo plano,
    garantindo que a interface gráfica (PySide6) permaneça responsiva.
    
    Attributes:
        status_atualizado (Signal): Emite mensagens de texto com o passo atual do robô.
        finalizado (Signal): Emitido quando o fluxo é concluído com sucesso.
        erro (Signal): Emitido caso ocorra alguma falha ou interrupção inesperada.
    """
    status_atualizado = Signal(str)
    finalizado = Signal()
    erro = Signal(str)

    def __init__(self, nome_fluxo, parent=None):
        """
        Inicializa a thread do motor RPA.

        Args:
            nome_fluxo (str): O nome do fluxo configurado no JSON a ser executado.
            parent (QObject, optional): Objeto pai da thread no Qt. Padrão é None.
        """
        super().__init__(parent)
        self.nome_fluxo = nome_fluxo
        self.rodando = True

    def run(self):
        """
        Método principal executado em background ao iniciar a thread.
        Carrega o arquivo de configuração JSON e executa os passos sequencialmente,
        respeitando as travas de segurança e o sinal de interrupção do usuário.
        """
        pyautogui.FAILSAFE = True
        try:
            caminho_config = ARQUIVO_CONFIG
            if not os.path.exists(caminho_config):
                self.erro.emit("Arquivo de configuração não encontrado.")
                return
            with open(caminho_config, 'r', encoding='utf-8') as f:
                dados_completos = json.load(f)

            passos_do_fluxo = dados_completos.get(self.nome_fluxo, [])
            if not passos_do_fluxo:
                self.erro.emit(f"O fluxo '{self.nome_fluxo}' está vazio.")
                return
            for passo in passos_do_fluxo:
                if not self.rodando:
                    self.status_atualizado.emit(f"Automação interrompida pelo usuário.")
                    break

                identificacao = passo.get("campo", "Passo Desconhecido")
                caminho_img = passo.get("caminho", "")
                acao = passo.get("acao", "Procurar e Clicar")
                parametro = passo.get("parametro", "")
        
                self.status_atualizado.emit(f"Executando: {identificacao}")
                time.sleep(Config.DELAY_PADRAO)
                match acao:
                    case "Procurar e Clicar":
                        self.move_and_click(self.localizar(caminho_img))
                        time.sleep(Config.DELAY_CURTO)
                    case "Procurar e Pressionar Teclas":
                        self.localizar_popup(caminho_img)
                        if parametro:
                            teclas = [t.strip() for t in parametro.split(',')]
                        pyautogui.press(teclas)
                        time.sleep(Config.DELAY_CURTO)
                    case "Procurar e Digitar texto":
                        self.localizar_popup(caminho_img)
                        self.inserir_texto(parametro)
                        time.sleep(Config.DELAY_CURTO)
                    case "Digitar texto":
                        self.inserir_texto(parametro)
                        time.sleep(Config.DELAY_CURTO)
                    case "Pressionar Teclas":
                        if parametro:
                            teclas = [t.strip() for t in parametro.split(',')]
                        pyautogui.press(teclas)
                        time.sleep(Config.DELAY_CURTO)
                    case "Aguardar (Segundos)":
                        time.sleep(int(parametro))
                time.sleep(Config.DELAY_CURTO)
            if self.rodando:
                self.finalizado.emit()
        except Exception as e:
            self.erro.emit(str(e))

    def parar(self):
        """Interrompe a execução do motor de forma segura alterando a flag de controle."""
        self.rodando = False

    def move_and_click(self, botao):
        """
        Move o cursor do mouse até as coordenadas indicadas e realiza um clique esquerdo.
        
        Args:
            botao (tuple/Point): Coordenadas (x, y) do centro da imagem encontrada.
        """
        if not self.rodando: return
        pyautogui.moveTo(botao, duration=0.1)
        pyautogui.click()

    def motor_de_busca(self, endereco_imagem, region_image=None, limite_tentativas=67, retornar_centro=True):
        """
        Realiza a varredura na tela em busca de uma imagem de referência de forma tolerante a falhas.
        
        Args:
            endereco_imagem (str or list): Caminho relativo ou lista de caminhos para a imagem do elemento.
            region_image (tuple, optional): Região (x, y, largura, altura) para limitar a busca. Padrão é None.
            limite_tentativas (int): Número máximo de tentativas antes de abortar o passo. Padrão é 67.
            retornar_centro (bool): Se True, retorna o centro do elemento; se False, retorna a caixa delimitadora.
            
        Returns:
            tuple: Coordenadas do elemento encontrado na tela.
            
        Raises:
            Exception: Se o elemento não for encontrado após o limite de tentativas ou se a thread for abortada.
        """
        coordenada = None
        tentativas = limite_tentativas
        if isinstance(endereco_imagem, str):
            endereco_imagem = [endereco_imagem]
        while tentativas > 0:
            if not self.rodando:
                raise Exception("Automação interrompida pelo usuário.")
            for img in endereco_imagem:
                try:
                    if retornar_centro:
                        coordenada = pyautogui.locateCenterOnScreen(img, confidence=0.8, grayscale=True, region=region_image)
                    else:
                        coordenada = pyautogui.locateOnScreen(img, confidence=0.8, grayscale=True, region=region_image)
                    if coordenada is not None:
                        return coordenada
                except pyautogui.ImageNotFoundException:
                    pass
            time.sleep(Config.DELAY_CURTO)
            tentativas -= 1
        raise Exception(f"Interrompido: imagem não encontrada.")

    def localizar(self, endereco_imagem, region_image=None):
        """Atalho para buscar o elemento retornando o ponto central (para cliques)."""
        return self.motor_de_busca(endereco_imagem, region_image, retornar_centro=True)

    def localizar_popup(self, endereco_pop_up, region_pop_up=None):
        """Atalho para buscar o elemento retornando a caixa de delimitação (para pop-ups)."""
        return self.motor_de_busca(endereco_pop_up, region_pop_up, retornar_centro=False)

    def inserir_texto(self, texto):
        """
        Insere texto de forma segura utilizando a área de transferência (Clipboard) 
        para evitar perdas de caracteres em campos de digitação rápida.
        
        Args:
            texto (str): O conteúdo textual que deve ser enviado ao campo focado.
        """
        if not self.rodando: return
        pyperclip.copy(texto)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")