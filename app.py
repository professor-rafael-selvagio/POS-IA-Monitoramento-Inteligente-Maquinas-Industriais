"""Ponto de entrada raiz para execução do Streamlit.

Executa a aplicação de Monitoramento e Análise Inteligente da Célula de Usinagem.
Uso:
    streamlit run app.py
"""

from __future__ import annotations

import os
import sys

# Adiciona o diretório da célula de usinagem ao caminho de módulos
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_CELULA = os.path.join(DIRETORIO_ATUAL, "celula_usinagem_inteligente")

if DIRETORIO_CELULA not in sys.path:
    sys.path.insert(0, DIRETORIO_CELULA)

# Carrega e executa a aplicação oficial Streamlit
caminho_app_oficial = os.path.join(DIRETORIO_CELULA, "app.py")
with open(caminho_app_oficial, "r", encoding="utf-8") as f:
    codigo_app = compile(f.read(), caminho_app_oficial, "exec")
    exec(codigo_app, globals())
