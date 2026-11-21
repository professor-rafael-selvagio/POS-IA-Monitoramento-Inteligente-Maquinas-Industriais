"""Módulo de Configuração Centralizada da Célula de Usinagem Inteligente.

Define parâmetros de rede, lista de equipamentos autorizados, validação de segurança
e metadados das variáveis de telemetria industrial do AI DataLab.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Final

# Servidor padrão do AI DataLab conforme ambiente didático
SERVIDOR_PADRAO: Final[str] = os.getenv("SERVIDOR_API", "http://10.110.18.12:10999")

# Máquinas autorizadas na Célula de Usinagem (RF03, RF17)
MAQUINAS_VALIDAS: Final[tuple[str, ...]] = (
    "CENTRO-USINAGEM-01",
    "FURADEIRA-01",
)

# Timeout para requisições HTTP em segundos (RF18)
TIMEOUT_PADRAO: Final[int] = int(os.getenv("API_TIMEOUT", "10"))

# Modelo Gemini padrão para Function Calling
MODELO_GEMINI_PADRAO: Final[str] = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Declaração obrigatória sobre a natureza dos dados (RF19, Desafio F)
DECLARACAO_DADOS_DIDATICOS: Final[str] = (
    "AVISO TÉCNICO DE ENGENHARIA: Os dados de telemetria apresentados são originários da "
    "plataforma educacional AI DataLab com dados industriais didáticos e simulados. Comportamentos "
    "incomuns e oscilações constituem evidências para investigação técnica pela equipe de manutenção, "
    "não correspondendo a diagnósticos definitivos de falha de equipamentos industriais reais."
)

# Metadados de variáveis e grandezas monitoradas por equipamento
METADADOS_VARIAVEIS: Final[dict[str, dict[str, dict[str, str]]]] = {
    "CENTRO-USINAGEM-01": {
        "temperatura": {
            "nome_exibicao": "Temperatura Mancal Spindle",
            "unidade": "°C",
            "grandeza": "temperatura",
        },
        "vibracao": {
            "nome_exibicao": "Vibração Eixo Principal",
            "unidade": "mm/s",
            "grandeza": "vibracao",
        },
        "rotacao": {
            "nome_exibicao": "Rotação Spindle",
            "unidade": "RPM",
            "grandeza": "rotacao",
        },
        "corrente": {
            "nome_exibicao": "Corrente Motor Principal",
            "unidade": "A",
            "grandeza": "corrente",
        },
    },
    "FURADEIRA-01": {
        "temperatura": {
            "nome_exibicao": "Temperatura Motor",
            "unidade": "°C",
            "grandeza": "temperatura",
        },
        "vibracao": {
            "nome_exibicao": "Vibração Cabeçote",
            "unidade": "mm/s",
            "grandeza": "vibracao",
        },
        "rotacao": {
            "nome_exibicao": "Rotação Eixo Árvore",
            "unidade": "RPM",
            "grandeza": "rotacao",
        },
        "pressao": {
            "nome_exibicao": "Pressão Hidráulica de Avanço",
            "unidade": "bar",
            "grandeza": "pressao",
        },
    },
}

# Grandezas comparáveis entre as duas máquinas (RF14, Desafio E)
GRANDEZAS_COMPARAVEIS: Final[dict[str, str]] = {
    "temperatura": "°C",
    "vibracao": "mm/s",
    "rotacao": "RPM",
}


def validar_maquina(identificador: str) -> str:
    """Valida se o identificador da máquina pertence à célula de usinagem autorizada.

    Atende ao Requisito Funcional RF17.

    Args:
        identificador: Nome da máquina a ser validada.

    Returns:
        O identificador normalizado em caixa alta se válido.

    Raises:
        ValueError: Caso a máquina não pertença à lista de autorizadas.
    """
    if not identificador or not isinstance(identificador, str):
        raise ValueError(
            "Identificador de máquina inválido. Forneça CENTRO-USINAGEM-01 ou FURADEIRA-01."
        )

    maquina_limpa = identificador.strip().upper()
    if maquina_limpa not in MAQUINAS_VALIDAS:
        raise ValueError(
            f"Máquina '{identificador}' não autorizada. "
            f"Esta aplicação monitora exclusivamente: {', '.join(MAQUINAS_VALIDAS)}."
        )
    return maquina_limpa


@dataclass(frozen=True)
class AppConfig:
    """Configuração em tempo de execução da aplicação."""

    servidor_api: str = SERVIDOR_PADRAO
    maquinas_validas: tuple[str, ...] = MAQUINAS_VALIDAS
    timeout: int = TIMEOUT_PADRAO
    modelo_gemini: str = MODELO_GEMINI_PADRAO
    declaracao_dados: str = DECLARACAO_DADOS_DIDATICOS
    metadados: dict = field(default_factory=lambda: METADADOS_VARIAVEIS)
