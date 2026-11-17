# MVP - Automação de Triagem Hospitalar

## Descrição
Produto Mínimo Viável (MVP) desenvolvido para o setor de recepção de um Hospital. O sistema utiliza PyAutoGUI e PySide6 para automatizar a digitação de dados em sistemas legados, reduzindo filas e o tempo de atendimento.

## Tecnologias Utilizadas
- Python 3
- PySide6 (GUI)
- PyAutoGUI & OpenCV (Automação visual)
- Pytest (Testes automatizados)

## Como executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute o sistema: `python src/main.py`
3. Execute os testes: `pytest tests/`

### Acesso às Configurações (Ambiente de Avaliação/MVP)
* **Senha padrão de administrador:** `admin123`
* *(Nota: Nesta versão MVP, a validação é realizada via hash Bcrypt pré-configurado; o fluxo de alteração de senha pela interface gráfica está mapeado no backlog para versões futuras).*