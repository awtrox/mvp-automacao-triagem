import sys
import time
import json
import os
import bcrypt
from motor_autogui import MotorRPAThread
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
                               QFrame, QFileDialog, QComboBox, QDialog, QFormLayout, QDialogButtonBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence

SENHA_ADMIN_HASH = b'$2b$12$nCn0OOpj3PrX6.jE2TULwOXKRzDXu6N1gvVBDLwOL0MQAvf8U6Mje'
PASTA_DATA = os.path.join(os.path.dirname(__file__), 'data')
ARQUIVO_CONFIG = os.path.join(PASTA_DATA, 'config.json')

if not os.path.exists(PASTA_DATA):
    os.makedirs(PASTA_DATA)

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
    QPushButton#BtnPrimario:hover { 
        background-color: #0056B3; 
    }

    QPushButton#BtnPrimario:pressed {
        background-color: #004085; 
    }

    QPushButton#BtnCancelar {
        background-color: #2A2A3C;
        color: #B4B4C8;
        border: 1px solid #B4B4C8; 
        border-radius: 6px; 
        font-weight: bold;
    }

    QPushButton#BtnCancelar:hover {
        background-color: #3F3F5A;
        color: #FFFFFF;
    }    
    QPushButton#BtnCancelar:pressed {
        background-color: #1E1E2E;
    }
    QPushButton#BtnAddAncora {
        background-color: #2E7D32;
        color: #FFFFFF;
        border-radius: 2px
    }
    QPushButton#BtnAddAncora:hover {
        background-color: #388E3C;
    }
    QPushButton#BtnAddAncora:pressed {
        background-color: #1B5E20;
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
    QTableWidget::item {
        padding-left: 5px;
        padding-right: 5px;
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
 
        #Listagem de keybinds de fluxos.
        fluxo1 = QLabel("Fluxo 1: Urgência\t\t Shift + F1")
        fluxo2 = QLabel("Fluxo 2: Medicamento\t Shift + F2")
        fluxo3 = QLabel("Fluxo 3: Pressão\t\t Shift + F4")
        fluxo4 = QLabel("Fluxo 4: Glicemia\t\t Shift + F8")
        fluxo5 = QLabel("Fluxo 5: Curativo\t\t Shift + F11")
        fluxo6 = QLabel("Fluxo 6: Exames\t\t Shift + T")
        fluxo7 = QLabel("Fluxo 7: Retirada de pontos\t Shift + R")
        card_layout.addWidget(fluxo1)
        card_layout.addWidget(fluxo2)
        card_layout.addWidget(fluxo3)
        card_layout.addWidget(fluxo4)
        card_layout.addWidget(fluxo5) 
        card_layout.addWidget(fluxo6)
        card_layout.addWidget(fluxo7)

        #Combo para seleção manual de fluxos e execução com 'Enter'
        self.combo_fluxo_tela_inicial = QComboBox()
        self.combo_fluxo_tela_inicial.addItems(["Urgência", "Medicamento", "Pressão", "Glicemia", "Curativo", "Exames", "Retirada de pontos", "Fluxo padrão"])
        self.combo_fluxo_tela_inicial.setMinimumHeight(35)
        self.combo_fluxo_tela_inicial.setStyleSheet("""
            QComboBox {
                background-color: #2A2A3C;
                color: #FFFFFF;
                font-size: 15px;
                padding: 10px 15px;
                border: 2px solid #3F3F5A;
                border-radius: 6px;
            }
            QComboBox:hover {
                border: 2px solid #5C5C7A;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50; 
            }
            QComboBox::drop-down {
                border-left: 1px solid #3F3F5A;
                width: 35px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E2E;
                color: #FFFFFF;
                border: 1px solid #3F3F5A;
                selection-background-color: #4CAF50; /* Verde ao selecionar item */
                selection-color: white;
            }
        """)
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.clicked.connect(self.iniciar_automacao)
        self.label_status = QLabel("Aguardando comando...")
        self.label_status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.estilo_base_status = """
            QLabel {
                background-color: #1E1E2E;
                color: #E0E0E0;
                font-size: 14px;
                font-family: Consolas, monospace; /* Fonte com estilo de terminal de código */
                padding: 12px 15px;
                border: 1px solid #3F3F5A;
                border-left: 5px solid #2196F3; /* Azul - Status Neutro */
                border-radius: 6px;
            }
        """
        self.label_status.setStyleSheet(self.estilo_base_status)
        self.btn_iniciar.setCursor(Qt.PointingHandCursor)
        self.label_status.setAlignment(Qt.AlignCenter)
        self.btn_iniciar.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32; 
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #388E3C; 
            }
            QPushButton:pressed {
                background-color: #1B5E20; 
            }
            QPushButton:disabled {
                background-color: #555555; 
                color: #AAAAAA;
            }
        """)

        self.btn_parar = QPushButton("Interromper")
        self.btn_parar.clicked.connect(self.parar_automacao)
        self.btn_parar.setCursor(Qt.PointingHandCursor)
        self.btn_parar.setEnabled(False)
        self.btn_parar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F; 
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
            QPushButton:pressed {
                background-color: #7F0000;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #AAAAAA;
            }
        """)
        linha_botoes = QHBoxLayout()
        linha_botoes.addWidget(self.btn_iniciar)
        linha_botoes.addWidget(self.btn_parar)
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
        layout.addWidget(self.combo_fluxo_tela_inicial)
        layout.addLayout(linha_botoes)
        layout.addWidget(self.label_status)
        layout.addStretch()
        layout.addWidget(self.btn_config)
        self.setLayout(layout)

        atalho_f1 = QShortcut(QKeySequence("Shift+F1"), self)
        atalho_f1.activated.connect(lambda: self.iniciar_por_atalho("Urgência"))
        atalho_f2 = QShortcut(QKeySequence("Shift+F2"), self)
        atalho_f2.activated.connect(lambda: self.iniciar_por_atalho("Medicamento"))
        atalho_f4 = QShortcut(QKeySequence("Shift+F4"), self)
        atalho_f4.activated.connect(lambda: self.iniciar_por_atalho("Pressão"))
        atalho_f8 = QShortcut(QKeySequence("Shift+F8"), self)
        atalho_f8.activated.connect(lambda: self.iniciar_por_atalho("Glicemia"))
        atalho_f11 = QShortcut(QKeySequence("Shift+F11"), self)
        atalho_f11.activated.connect(lambda: self.iniciar_por_atalho("Curativo"))
        atalho_t = QShortcut(QKeySequence("Shift+FT"), self)
        atalho_t.activated.connect(lambda: self.iniciar_por_atalho("Exames"))
        atalho_r = QShortcut(QKeySequence("Shift+R"), self)
        atalho_r.activated.connect(lambda: self.iniciar_por_atalho("Retirada de pontos"))
 

        atalho_enter = QShortcut(QKeySequence("Shift+Return"), self)
        atalho_enter.activated.connect(self.iniciar_automacao)

    def iniciar_automacao(self):
        if not self.btn_iniciar.isEnabled():
            return
        
        fluxo_escolhido = self.combo_fluxo_tela_inicial.currentText()

        self.btn_iniciar.setEnabled(False)
        self.btn_parar.setEnabled(True)
        self.atualizar_painel_status(f"Iniciando fluxo: {fluxo_escolhido}...", "info")
        
        self.thread_rpa = MotorRPAThread(fluxo_escolhido)
        self.thread_rpa.status_atualizado.connect(self.atualizar_status)
        self.thread_rpa.finalizado.connect(self.finalizar_sucesso)
        self.thread_rpa.erro.connect(self.mostrar_erro)
        self.thread_rpa.start()

    def iniciar_por_atalho(self, nome_fluxo):
        """Muda o ComboBox para o fluxo do atalho e roda o fluxo"""
        index = self.combo_fluxo_tela_inicial.findText(nome_fluxo)
        if index >= 0:
            self.combo_fluxo_tela_inicial.setCurrentIndex(index)
            self.iniciar_automacao()
        else:
            self.mostrar_erro(f"Fluxo '{nome_fluxo}' não encontrado configurado.")

    def parar_automacao(self):
        if hasattr(self, 'thread_rpa') and self.thread_rpa.isRunning():
            self.thread_rpa.parar()
            self.label_status.setText("Interrompendo automação... Aguarde.")

            self.btn_parar.setEnabled(False)

    def atualizar_status(self, mensagem):
        self.atualizar_painel_status(mensagem, "rodando")

    def finalizar_sucesso(self):
        self.atualizar_painel_status("Fluxo concluido.", "sucesso")
        self.btn_iniciar.setEnabled(True)
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)

    def mostrar_erro(self, msg_erro):
        self.atualizar_painel_status(f"Erro: {msg_erro}", "erro")
        self.btn_iniciar.setEnabled(True)
        self.btn_parar.setEnabled(False)

    def atualizar_painel_status(self, mensagem, tipo="info"):
        """
        Atualiza o texto e a cor da borda do label_status.
        Tipos: 'info' (Azul), 'rodando' (Amarelo), 'sucesso' (Verde), 'erro' (Vermelho)
        """
        cores = {
            "info": "#2196F3",      # Azul
            "rodando": "#FFC107",   # Amarelo/Laranja
            "sucesso": "#4CAF50",   # Verde
            "erro": "#F44336"       # Vermelho
        }
        
        cor_borda = cores.get(tipo, "#2196F3")
        
        # Injeta a cor correta na borda esquerda
        novo_estilo = self.estilo_base_status.replace(
            "border-left: 5px solid #2196F3;", 
            f"border-left: 5px solid {cor_borda};"
        )
        
        self.label_status.setStyleSheet(novo_estilo)
        self.label_status.setText(mensagem)
    
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
        senha_digitada = self.input_senha.text()
        senha_bytes = senha_digitada.encode('utf-8')

        if bcrypt.checkpw(senha_bytes, SENHA_ADMIN_HASH):
            self.input_senha.clear()
            self.lbl_erro.setText("")
            self.main_window.is_logged_in = True
            # self.main_window.ultimo_login = time.time()
            self.main_window.mudar_tela(2)
        else:
            self.input_senha.setStyleSheet("""
                border: 2px solid #D32F2F; 
                background-color: #2A2A3C; 
                color: white; 
                border-radius: 6px; 
                padding: 10px;
            """)
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
            if event.text() and not self.input_senha.hasFocus():
                self.input_senha.setFocus()
                self.input_senha.keyPressEvent(event)
            else:
                super().keyPressEvent(event)

class DialogAcoes(QDialog):
    def __init__(self, parent=None, dados_existentes=None):
        super().__init__(parent)
        self.setWindowTitle("COnfigurar ações")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: #1E1E2E; color: white;")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.combo_acao = QComboBox()
        self.combo_acao.addItems(["", "Procurar e Clicar", "Procurar e Pressionar Teclas", "Procurar e Digitar texto", "Digitar texto", "Pressionar Teclas", "Aguardar (Segundos)"])

        self.input_parametro = QLineEdit()
        self.input_parametro.setPlaceholderText("Ex: tab, enter, texto a digitar...")

        form_layout.addRow("Ação:", self.combo_acao)
        form_layout.addRow("Parâmetro:", self.input_parametro)
        layout.addLayout(form_layout)

        botoes = QDialogButtonBox(QDialogButtonBox.Save |QDialogButtonBox.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

        self.dados_salvos = dados_existentes or {}
        if self.dados_salvos:
            self.combo_acao.setCurrentText(self.dados_salvos.get("acao", "Procurar e Clicar"))
            self.input_parametro.setText(self.dados_salvos.get("parametro", ""))

    def get_dados(self):
        """Retorna as configurações escolhidas no pop-up"""
        return {
            "acao": self.combo_acao.currentText(),
            "parametro": self.input_parametro.text()
        }

class TelaConfig(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pasta_padrao = os.path.join(os.path.expanduser("~"), "Pictures")
        self.ultimo_diretorio = self.pasta_padrao
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 30, 10, 30)

        #Título
        titulo = QLabel("Configuração de Fluxos")
        titulo.setObjectName("Titulo")
        titulo.setAlignment(Qt.AlignCenter)

        #Tabela de âncoras
        tabela_label = QLabel("Mapeamento de âncoras visuais")
        tabela_label.setStyleSheet("font-size: 16px; margin-top: 20px;")
        tabela_label.setAlignment(Qt.AlignCenter)

        combo_layout = QHBoxLayout()
        label_combo = QLabel("Selecione o Fluxo")
        label_combo.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.combo_fluxos = QComboBox()
        self.combo_fluxos.addItems(["Urgência", "Medicamento", "Pressão", "Glicemia", "Curativo", "Exames", "Retirada de pontos", "Fluxo padrão"])
        self.combo_fluxos.setMinimumHeight(35)
        self.combo_fluxos.setStyleSheet("""
            QComboBox {
                background-color: #2A2A3C;
                color: #FFFFFF;
                font-size: 15px;
                padding: 10px 15px;
                border: 2px solid #3F3F5A;
                border-radius: 6px;
            }
            QComboBox:hover {
                border: 2px solid #5C5C7A;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50; /* Borda verde ao focar */
            }
            QComboBox::drop-down {
                border-left: 1px solid #3F3F5A;
                width: 35px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E2E;
                color: #FFFFFF;
                border: 1px solid #3F3F5A;
                selection-background-color: #4CAF50; /* Verde ao selecionar item */
                selection-color: white;
            }
        """)
        self.combo_fluxos.currentTextChanged.connect(self.carregar_dados)
        
        combo_layout.addWidget(label_combo)
        combo_layout.addWidget(self.combo_fluxos)
        combo_layout.addStretch()

        self.tabela = QTableWidget(0, 6)
        self.tabela.setTextElideMode(Qt.ElideMiddle)
        self.tabela.setWordWrap(False)
        self.tabela.setTabKeyNavigation(False)
        self.tabela.setHorizontalHeaderLabels(["Ordem", "Identificação", "Caminho da imagem", "Ação", "Mover", ""])
        self.tabela.verticalHeader().setVisible(False)
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tabela.cellDoubleClicked.connect(self.escolher_imagem)

        self.btn_add_linha = QPushButton("+ Adicionar Âncora")
        self.btn_add_linha.setObjectName("BtnAddAncora")
        self.btn_add_linha.setMinimumWidth(140)
        self.btn_add_linha.setMinimumHeight(44)
        self.btn_add_linha.setCursor(Qt.PointingHandCursor)
        self.btn_add_linha.clicked.connect(self.adicionar_linha_vazia)

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
        layout.addLayout(combo_layout)
        layout.addWidget(tabela_label)
        layout.addWidget(self.tabela)
        layout.addWidget(self.btn_add_linha, alignment=Qt.AlignLeft)
        layout.addStretch()
        layout.addLayout(rodape_layout)
        self.setLayout(layout)

        self.carregar_dados()

    def adicionar_linha_vazia(self):
        """Adiciona uma nova linha em branco no final da tabela"""
        linha_atual = self.tabela.rowCount()   
        self.tabela.insertRow(linha_atual)

        self.tabela.setItem(linha_atual, 0, QTableWidgetItem(str(linha_atual + 1)))
        self.tabela.setItem(linha_atual, 1, QTableWidgetItem(""))
        self.tabela.setItem(linha_atual, 2, QTableWidgetItem(""))
        
        btn_acoes = QPushButton("Configurar")
        btn_acoes.setCursor(Qt.PointingHandCursor)
        btn_acoes.setStyleSheet("background-color: #2A2A3C; color: white; border-radius: 4px; padding: 4px;")
        btn_acoes.clicked.connect(lambda _, b=btn_acoes: self.abrir_menu_config(b))
        self.tabela.setCellWidget(linha_atual, 3, btn_acoes)

        container_mover = QWidget()
        layout_mover = QHBoxLayout(container_mover)
        layout_mover.setContentsMargins(0, 0, 0, 0)
        layout_mover.setSpacing(4)

        btn_subir = QPushButton("⬆️")
        btn_subir.setStyleSheet("color: white; border-radius: 4px; padding: 2px;")
        btn_subir.setCursor(Qt.PointingHandCursor)

        btn_descer = QPushButton("⬇️")
        btn_descer.setStyleSheet("color: white; border-radius: 4px; padding: 2px;")
        btn_descer.setCursor(Qt.PointingHandCursor)


        btn_subir.clicked.connect(lambda _, b=btn_subir: self.mover_linha(b, -1))
        btn_descer.clicked.connect(lambda _, b=btn_descer: self.mover_linha(b, 1))
        layout_mover.addWidget(btn_subir)
        layout_mover.addWidget(btn_descer)
        self.tabela.setCellWidget(linha_atual, 4, container_mover)

        btn_remover = QPushButton("🗑️")
        btn_remover.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 4px; font-weight: bold;")
        btn_remover.setCursor(Qt.PointingHandCursor)
        btn_remover.clicked.connect(lambda _, b=btn_remover: self.remover_linha(b))
        self.tabela.setCellWidget(linha_atual, 5, btn_remover)

    def carregar_dados(self):
        """Lê o arquivo config.json e popula a tabela"""
        fluxo_atual = self.combo_fluxos.currentText()
        self.tabela.setRowCount(0)

        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                try:
                    dados_completos = json.load(f)

                    dados_fluxo = dados_completos.get(fluxo_atual, [])

                    self.tabela.setRowCount(len(dados_fluxo))
                    for i, ancora in enumerate(dados_fluxo):
                        self.tabela.setItem(i, 0, QTableWidgetItem(ancora.get('ordem', '')))
                        item_campo = QTableWidgetItem(ancora.get('campo', ''))
                        dados_config = {
                            "acao": ancora.get('acao', 'Procurar e Clicar'),
                            "parametro": ancora.get('parametro', '')
                        }
                        item_campo.setData(Qt.UserRole, dados_config)
                        self.tabela.setItem(i, 1, item_campo)

                        caminhos_salvos = ancora.get('caminho', [])
                        if isinstance(caminhos_salvos, str):
                            caminhos_salvos = [caminhos_salvos] if caminhos_salvos else []
                        texto_exibicao = " ; ".join(caminhos_salvos)
                        item_caminho = QTableWidgetItem(texto_exibicao)
                        item_caminho.setToolTip("\n".join(caminhos_salvos))
                        self.tabela.setItem(i, 2, item_caminho) 

                        btn_acoes = QPushButton("Configurar")
                        btn_acoes.setCursor(Qt.PointingHandCursor)

                        if ancora.get('parametro') or ancora.get('acao', 'Procurar e Clicar') != '':
                            btn_acoes.setText("Configurado")
                            btn_acoes.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 4px; padding: 4px; font-weight: bold;")
                        else:
                            btn_acoes.setStyleSheet("background-color: #2A2A3C; color: white; border-radius: 4px; padding: 4px;")
                        btn_acoes.clicked.connect(lambda _, b=btn_acoes: self.abrir_menu_config(b))
                        self.tabela.setCellWidget(i, 3, btn_acoes)

                        container_mover = QWidget()
                        layout_mover = QHBoxLayout(container_mover)
                        layout_mover.setContentsMargins(0, 0, 0, 0)
                        layout_mover.setSpacing(4)
                        
                        btn_subir = QPushButton("⬆️")
                        btn_subir.setStyleSheet("color: white; border-radius: 4px; padding: 2px;")
                        btn_subir.setCursor(Qt.PointingHandCursor)
                        btn_descer = QPushButton("⬇️")
                        btn_descer.setStyleSheet("color: white; border-radius: 4px; padding: 2px;")
                        btn_descer.setCursor(Qt.PointingHandCursor)

                        
                        btn_subir.clicked.connect(lambda _, b=btn_subir: self.mover_linha(b, -1))
                        btn_descer.clicked.connect(lambda _, b=btn_descer: self.mover_linha(b, 1))
                        
                        layout_mover.addWidget(btn_subir)
                        layout_mover.addWidget(btn_descer)
                        self.tabela.setCellWidget(i, 4, container_mover)

                        btn_remover = QPushButton("🗑️")
                        btn_remover.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 4px; font-weight: bold;")
                        btn_remover.setCursor(Qt.PointingHandCursor)
                        btn_remover.clicked.connect(lambda _, b=btn_remover: self.remover_linha(b))
                        self.tabela.setCellWidget(i, 5, btn_remover)
                except json.JSONDecodeError:
                    pass
        if self.tabela.rowCount() == 0:
            self.adicionar_linha_vazia()

    def salvar_e_notificar(self):
        """Lê a tabela linha por linha e salva no config.json"""
        fluxo_atual = self.combo_fluxos.currentText()
        dados_completos = {}
        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                try:
                    dados_completos = json.load(f)
                    if isinstance(dados_completos, list):
                        dados_completos = {"Fluxo padrão": dados_completos}
                except json.JSONDecodeError:
                    pass

        dados_fluxo_atual = []
        for linha in range(self.tabela.rowCount()):
            item_ordem = self.tabela.item(linha, 0)
            item_campo = self.tabela.item(linha, 1)
            item_caminho = self.tabela.item(linha, 2)

            if item_campo and item_campo.text().strip():
                dados_config = item_campo.data(Qt.UserRole)

                texto_caminho = item_caminho.text() if item_caminho else ""
                lista_caminhos = [c.strip() for c in texto_caminho.split(";")] if texto_caminho else []
                ancora = {
                    "ordem": item_ordem.text() if item_ordem else "",
                    "campo": item_campo.text(),
                    "caminho": lista_caminhos,
                    "acao": dados_config.get("acao", "Procurar e Clicar") if dados_config else "Procurar e Clicar",
                    "parametro": dados_config.get("parametro", "") if dados_config else ""
                }
                dados_fluxo_atual.append(ancora)

        dados_completos[fluxo_atual] = dados_fluxo_atual
        with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(dados_completos, f, indent=4, ensure_ascii=False)

        self.main_window.mudar_tela(0)
        self.main_window.mostrar_toast()

    def escolher_imagem(self, linha, coluna):
        if coluna == 2:
            dir_inicial = self.ultimo_diretorio if os.path.exists(self.ultimo_diretorio) else self.pasta_padrao
            caminho_arquivos, _ = QFileDialog.getOpenFileNames(
                self,
                "Selecione a(s) Imagem(ns) da Âncora",
                dir_inicial,
                "Imagens (*.png *.jpg *.jpeg *.bmp)"
            )
            if isinstance(caminho_arquivos, str):
                caminho_arquivos = [caminho_arquivos] if caminho_arquivos else []

            if caminho_arquivos:
                self.ultimo_diretorio = os.path.dirname(caminho_arquivos[0])
            caminhos_formatados = [os.path.normpath(c) for c in caminho_arquivos]

            texto_exibicao = " ; ".join(caminhos_formatados)
            item_caminho = QTableWidgetItem(texto_exibicao)
            item_caminho.setToolTip("\n".join(caminhos_formatados))
            self.tabela.setItem(linha, 2, item_caminho) 

    def abrir_menu_config(self, botao):
        linha = -1
        for r in range(self.tabela.rowCount()):
            if self.tabela.cellWidget(r, 3) == botao:
                linha = r
                break
        if linha == -1: return
        item_campo = self.tabela.item(linha, 1)
        if not item_campo:
            return

        dados_salvos = item_campo.data(Qt.UserRole)
        dialog = DialogAcoes(self, dados_existentes=dados_salvos)

        if dialog.exec() == QDialog.Accepted:
            novos_dados = dialog.get_dados()

            item_campo.setData(Qt.UserRole, novos_dados)

            btn = self.tabela.cellWidget(linha, 3)
            if btn:
                btn.setText("Configurado")
                btn.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 4px; padding: 4px; font-weight: bold;")

    def atualizar_botao(self, linha):
        item_campo = self.tabela.item(linha, 1)
        btn_acoes = self.tabela.cellWidget(linha, 3)
        if not item_campo or not btn_acoes: return

        dados_config = item_campo.data(Qt.UserRole)
        if dados_config and (dados_config.get('parametro') or dados_config.get('acao') != ''):
            btn_acoes.setText("Configurado")
            btn_acoes.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 4px; padding: 4px; font-weight: bold;")
        else:
            btn_acoes.setText("Configurar")
            btn_acoes.setStyleSheet("background-color: #2A2A3C; color: white; border-radius: 4px; padding: 4px;")
    
    def mover_linha(self, botao, direcao):
        container = botao.parent()
        linha_atual = -1

        for r in range(self.tabela.rowCount()):
            if self.tabela.cellWidget(r, 4) == container:
                linha_atual = r
                break

        if linha_atual == -1: return
        linha_alvo = linha_atual + direcao

        if linha_alvo < 0 or linha_alvo >= self.tabela.rowCount():
            return

        item_campo_atual = self.tabela.item(linha_atual, 1)
        item_campo_alvo = self.tabela.item(linha_alvo, 1)

        texto_campo_temp = item_campo_atual.text()
        dados_config_temp = item_campo_atual.data(Qt.UserRole)

        item_campo_atual.setText(item_campo_alvo.text())
        item_campo_atual.setData(Qt.UserRole, item_campo_alvo.data(Qt.UserRole))

        item_campo_alvo.setText(texto_campo_temp)
        item_campo_alvo.setData(Qt.UserRole, dados_config_temp)

        item_caminho_atual = self.tabela.item(linha_atual, 2)
        item_caminho_alvo = self.tabela.item(linha_alvo, 2)
        
        texto_caminho_temp = item_caminho_atual.text()
        tooltip_temp = item_caminho_atual.toolTip()
        
        item_caminho_atual.setText(item_caminho_alvo.text())
        item_caminho_atual.setToolTip(item_caminho_alvo.toolTip())
        
        item_caminho_alvo.setText(texto_caminho_temp)
        item_caminho_alvo.setToolTip(tooltip_temp)
        
        self.atualizar_botao(linha_atual)
        self.atualizar_botao(linha_alvo)

    def remover_linha(self, botao):
        for linha in range(self.tabela.rowCount()):
            if self.tabela.cellWidget(linha, 5) == botao:
                self.tabela.removeRow(linha)
                self.reorganizar_ordem()
                break

    def reorganizar_ordem(self):
        for linha in range(self.tabela.rowCount()):
            item_ordem = self.tabela.item(linha, 0)
            if item_ordem:
                item_ordem.setText(str(linha + 1))

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
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(500, 600)
        self.setStyleSheet(STYLE_SHEET)
        tela = QApplication.primaryScreen().availableGeometry()
        tamanho_janela = self.frameGeometry()
        margem = 15
        pos_x = tela.left() + margem
        pos_y = tela.height() - tamanho_janela.height() - (margem * 3)
        self.move(pos_x, pos_y)
        #Configuração de estilo
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
        if indice == 1:
            self.tela_auth.input_senha.setFocus()
        else:
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