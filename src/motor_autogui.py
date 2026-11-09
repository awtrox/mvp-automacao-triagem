import keyboard
import threading
import time

def executar_fluxo():
    #Placeholder
    time.sleep(1)

def iniciar_escuta_atalhos():
    keyboard.add_hotkey("ctrl+shift+u", executar_fluxo)
    keyboard.wait()

def rodar_motor_em_background():
    """Roda a escuta de atalhos em uma Thread separada da GUI"""
    thread = threading.Thread(target=iniciar_escuta_atalhos, daemon=True)
    thread.start()