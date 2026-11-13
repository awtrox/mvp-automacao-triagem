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
#Motores de funções
def caminho_recurso(caminho_relativo):
    try:
        caminhho_base = sys._MEIPASS
    except Exception:
        caminhho_base = os.path.abspath(".")
    
    return os.path.join(caminhho_base, caminho_relativo)

class MotorRPAThread(QThread):
    status_atualizado = Signal(str)
    finalizado = Signal()
    erro = Signal(str)

    def __init__(self, nome_fluxo, parent=None):
        super().__init__(parent)
        self.nome_fluxo = nome_fluxo
        self.rodando = True

    def run(self):
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
        """Função chamada pelo botão 'Parar' na interface"""
        self.rodando = False

    def move_and_click(self, botao):
        if not self.rodando: return
        pyautogui.moveTo(botao, duration=0.1)
        pyautogui.click()

    def motor_de_busca(self, endereco_imagem, region_image=None, limite_tentativas=67, retornar_centro=True):
        coordenada = None
        tentativas = limite_tentativas
        if isinstance(endereco_imagem, str):
            endereco_imagem = [endereco_imagem]
        while tentativas > 0:
            if not self.rodando:
                raise Exception("Automação interrompida pelo usuário.")
            for img in endereco_imagem:
                try:
                    caminho_absoluto = caminho_recurso(img)
                    if retornar_centro:
                        coordenada = pyautogui.locateCenterOnScreen(caminho_absoluto, confidence=0.8, grayscale=True, region=region_image)
                    else:
                        coordenada = pyautogui.locateOnScreen(caminho_absoluto, confidence=0.8, grayscale=True, region=region_image)
                    if coordenada is not None:
                        return coordenada
                except pyautogui.ImageNotFoundException:
                    pass
            time.sleep(Config.DELAY_CURTO)
            tentativas -= 1
        raise Exception(f"Interrompido: imagem não encontrada.")

    def localizar(self, endereco_imagem, region_image=None):
        return self.motor_de_busca(endereco_imagem, region_image, retornar_centro=True)

    def localizar_popup(self, endereco_pop_up, region_pop_up=None):
        return self.motor_de_busca(endereco_pop_up, region_pop_up, retornar_centro=False)

    def inserir_texto(self, texto):
        if not self.rodando: return
        pyperclip.copy(texto)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")