import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PySide6.QtCore import Qt, QTimer

STYLE_SHEET = """
    QWidget {
        background-color: #1E1E2E;
        color: #FFFFFF;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    }
    QLabel#Titulo {
        font-size: 22px;
        font-weight: bold;
    }
    QLabel#StatusMotor  {
        font-size: 16px;
        font-weight: bold;
        color: #4CAF50;
    }
    QFrame#CardFluxos {
        background-color: #2A2A3C;
        border-radius: 8px;
    }
    QPushButton#BtnPrimario {
        background-color: #007BFF;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
        color: white;
    }
    QPushButton#BtnPrimario:hover { background-color: #0056B3; }

    QPushButton#BtnCancelar {
        border: 1px solid #B4B4C8; 
        border-radius: 6px; 
        font-weight: bold;
    }
    /* Foco visível para navegação no teclado */
    QPushButton:focus, QLineEdit:focus, QTableWidget:focus, 
    #BtnPrimario:focus, #BtnCancelar:focus {
        border: 2px solid #00E5FF;
    }
    QLineEdit {
        background-color: #2A2A3C;
        border: 1px solid #3A3A50;
        border-radius: 4px;
        padding: 8px;
        font-size: 14px;
    }
    QTableWidget {
        background-color: #2A2A3C;
        border: 1px solid #3A3A50;
        border-radius: 4px;
        gridline-color: #3A3A50;
    }
    QHeaderView::section {
        background-color: #1E1E2E;
        color: #B4B4C8;
        border: none;
        padding-left: 4px;
        font-weight: bold;
    }

"""

class TelaInicial(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        #Título e status
        titulo = QLabel("Automação de Triagem")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)
        status = QLabel("Motor de automação: ATIVO")
        status.setObjectName("StatusMotor")
        status.setAlignment(Qt.AlignCenter)
        #Card de fluxos
        card_fluxos = QFrame()
        card_fluxos.setObjectName("CardFluxos")
        card_layout = QVBoxLayout(card_fluxos)
        card_layout.setSpacing(15)
        #Fluxos ficticios
        fluxo1 = QLabel("Fluxo 1: Urgência\t\t Ctrl + Shift + U")
        fluxo2 = QLabel("Fluxo 2: Enfermagem \t Ctrl + SHift + E")
        card_layout.addWidget(fluxo1)
        card_layout.addWidget(fluxo2)
        #Botão de configuração
        self.btn_config = QPushButton("Acessar Configurações")
        self.btn_config.setObjectName("BtnPrimario")
        self.btn_config.setFixedHeight(48)
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.clicked.connect(self.main_window.tentar_acessar_config)
        #Implementação de layout
        layout.addWidget(titulo)
        layout.addWidget(status)
        layout.addSpacing(20)
        layout.addWidget(card_fluxos)
        layout.addStretch()
        layout.addWidget(self.btn_config)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.btn_config.hasFocus():
                self.main_window.tentar_acessar_config()
        else:
            super().keyPressEvent(event)

class TelaAuth(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        #Titulo
        titulo = QLabel("Autenticação Necessária")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)
        #Instrução, campo de digitação da senha e status de erro
        instrucao = QLabel("Insira a senha do administrador:")
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("*************")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.returnPressed.connect(self.verificar_senha)
        self.lbl_erro = QLabel("")
        self.lbl_erro.setAlignment(Qt.AlignCenter)
        #Botões de confirmação/cancelamento
        botoes_layout = QHBoxLayout()
        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setObjectName("BtnCancelar")
        self.btn_voltar.setCursor(Qt.PointingHandCursor)
        self.btn_voltar.setFixedHeight(40)
        self.btn_voltar.clicked.connect(self.voltar)

        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setObjectName("BtnPrimario")
        self.btn_entrar.setCursor(Qt.PointingHandCursor)
        self.btn_entrar.setFixedHeight(40)
        self.btn_entrar.clicked.connect(self.verificar_senha)

        botoes_layout.addWidget(self.btn_voltar)
        botoes_layout.addWidget(self.btn_entrar)
        #Implementação de layout
        layout.addStretch()
        layout.addWidget(titulo)
        layout.addSpacing(20)   
        layout.addWidget(instrucao)
        layout.addWidget(self.input_senha)
        layout.addWidget(self.lbl_erro)
        layout.addStretch()
        layout.addLayout(botoes_layout)
        self.setLayout(layout)

    def verificar_senha(self):
        #Lógica de validação ficticia
        if self.input_senha.text() == "admin":
            self.input_senha.clear()
            self.lbl_erro.setText("")
            self.main_window.is_logged_in = True
            # self.main_window.ultimo_login = time.time()
            self.main_window.mudar_tela(2)
        else:
            self.lbl_erro.setText("Senha Incorreta!")
            self.input_senha.clear()
            self.input_senha.setFocus()

    def voltar(self):
        self.input_senha.clear()
        self.lbl_erro.setText("")
        self.main_window.mudar_tela(0)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.btn_voltar.hasFocus():
                self.voltar()
            else:
                self.verificar_senha()
        else:
            super().keyPressEvent(event)


class TelaConfig(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        #Título
        titulo = QLabel("Configuração de Fluxos")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)

        #Tabela de âncoras
        tabela_label = QLabel("Mapeamento de âncoras visuais")
        tabela_label.setStyleSheet("font-size: 16px; margin-top: 20px;")
        tabela_label.setAlignment(Qt.AlignCenter)

        self.tabela = QTableWidget(1, 3)
        self.tabela.setTabKeyNavigation(False)
        self.tabela.setHorizontalHeaderLabels(["Ordem", "Nome do campo", "Caminho da imagem"])
        self.tabela.verticalHeader().setVisible(False)
        header = self.tabela.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.tabela.setItem(0,0, QTableWidgetItem("1"))
        self.tabela.setItem(0,1, QTableWidgetItem("campo_procedimento"))
        self.tabela.setItem(0,2, QTableWidgetItem("C:\\img\\proced...png"))

        #Rodapé
        rodape_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("BtnCancelar")
        self.btn_cancelar.setFixedHeight(48)
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.clicked.connect(lambda: self.main_window.mudar_tela(0))

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setObjectName("BtnPrimario")
        self.btn_salvar.setFixedHeight(48)
        self.btn_salvar.setCursor(Qt.PointingHandCursor)
        self.btn_salvar.clicked.connect(self.salvar_e_notificar)
    

        rodape_layout.addWidget(self.btn_cancelar)
        rodape_layout.addWidget(self.btn_salvar)
        
        layout.addWidget(titulo)
        layout.addSpacing(10)
        layout.addWidget(tabela_label)
        layout.addWidget(self.tabela)
        layout.addStretch()
        layout.addLayout(rodape_layout)
        self.setLayout(layout)

    def salvar_e_notificar(self):
        """Simula o salvamento e exibe a Tela 3 (Toast)"""
        self.main_window.mudar_tela(0)
        self.main_window.mostrar_toast()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.btn_cancelar.hasFocus():
                self.btn_cancelar.click()
            else:
                self.salvar_e_notificar()
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MVP - Hospital São João Batista do Glória")
        #Configuração de estilo
        self.setFixedSize(450, 600)
        self.setStyleSheet(STYLE_SHEET)
        #Variáveis de sessão
        self.is_logged_in = False
        self.ultimo_login = None
        #Gerenciamento de stacks
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        #Mapemento de stacks
        self.tela_inicial = TelaInicial(self)
        self.tela_auth = TelaAuth(self)
        self.tela_config = TelaConfig(self)
        #Stack de telas
        self.stack.addWidget(self.tela_inicial)
        self.stack.addWidget(self.tela_auth)
        self.stack.addWidget(self.tela_config)
        #Toast de notificação
        self.toast = QLabel("Configurações salvas com sucesso!", self)
        self.toast.setStyleSheet("background-color: #2A2A3C; color: #FFFFFF; font-weight: bold; padding: 15px; border-left: 5px solid #4CAF50; border-radius: 4px;")
        self.toast.setFixedSize(380, 50)
        self.toast.move(35, 460)
        self.toast.hide()

    def tentar_acessar_config(self):
        """Verfica a sessão antes de mudar de tela"""
        #Molde para timeout futuro
        #if self.ultimo_login and (time.time() - self.ultimo_login > 300):
        #   self.is_logged_in = False

        if self.is_logged_in:
            self.mudar_tela(2)
        else:
            self.mudar_tela(1)

    def mudar_tela(self, indice):
        """Alterna entre as janelas"""
        self.stack.setCurrentIndex(indice)
        self.setFocus()

    def mostrar_toast(self):
        """Exibe o alerta de sucesso e esconde após 3 segundos"""
        self.toast.show()
        QTimer.singleShot(3000, self.toast.hide)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setFocus()
    sys.exit(app.exec())