"""Módulo de Ferramentas (Function Calling) para o Assistente Gemini.

Define as funções Python com tipagem estrita e docstrings detalhadas prontas
para inspeção e execução pelo Google GenAI SDK. Mantém rastreabilidade de
chamadas de ferramentas para exibição transparente na interface do usuário.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from analise import (
    calcular_comportamento_habitual,
    calcular_regularidade,
    calcular_tendencia_temporal,
    comparar_maquinas,
    detectar_registros_incomuns as motor_detectar_anomalias,
    gerar_relatorio_completo_variavel,
)
from api_client import obter_historico, obter_ultima_leitura
from config import (
    DECLARACAO_DADOS_DIDATICOS,
    SERVIDOR_PADRAO,
    TIMEOUT_PADRAO,
    validar_maquina,
)

logger = logging.getLogger(__name__)

# Rastreamento thread-safe de ferramentas executadas durante uma pergunta
_tls = threading.local()


def _registrar_execucao(nome_ferramenta: str, argumentos: dict[str, Any]) -> None:
    """Registra uma execução de ferramenta na thread corrente para exibição na UI."""
    if not hasattr(_tls, "ferramentas_executadas"):
        _tls.ferramentas_executadas = []
    _tls.ferramentas_executadas.append({
        "ferramenta": nome_ferramenta,
        "argumentos": argumentos,
    })


def coletar_ferramentas_executadas() -> list[dict[str, Any]]:
    """Recupera e limpa a lista de ferramentas chamadas na interação corrente."""
    lista = getattr(_tls, "ferramentas_executadas", [])
    _tls.ferramentas_executadas = []
    return lista


# ─────────────────────────────────────────────────────────────────────────────
# FERRAMENTAS EXPOSTAS AO GEMINI (FUNCTION CALLING)
# ─────────────────────────────────────────────────────────────────────────────

def consultar_ultima_leitura_maquina(
    maquina: str,
    servidor: str = SERVIDOR_PADRAO,
) -> dict[str, Any]:
    """Consulta as medições mais recentes de sensores da máquina especificada.

    Use esta ferramenta sempre que o usuário perguntar sobre o estado atual,
    última leitura ou valores instantâneos de CENTRO-USINAGEM-01 ou FURADEIRA-01.

    Args:
        maquina: Nome da máquina autorizada ('CENTRO-USINAGEM-01' ou 'FURADEIRA-01').
        servidor: Endereço do servidor API (opcional, utiliza o padrão configurado).

    Returns:
        Dicionário com timestamp, valores de cada sensor, unidades e metadados.
    """
    _registrar_execucao("consultar_ultima_leitura_maquina", {"maquina": maquina})
    try:
        maq_valida = validar_maquina(maquina)
        return obter_ultima_leitura(servidor=servidor, maquina=maq_valida)
    except Exception as err:
        return {"erro": f"Falha ao consultar última leitura de {maquina}: {err}"}


def consultar_historico_leituras(
    maquina: str,
    limit: int = 50,
    servidor: str = SERVIDOR_PADRAO,
) -> dict[str, Any]:
    """Consulta os registros históricos mais recentes da máquina informada.

    Use esta ferramenta para responder perguntas sobre o histórico, sequência
    de registros e listagem temporal das medições.

    Args:
        maquina: Nome da máquina ('CENTRO-USINAGEM-01' ou 'FURADEIRA-01').
        limit: Quantidade de registros a retornar (entre 5 e 200, padrão 50).
        servidor: Endereço do servidor API (opcional).

    Returns:
        Dicionário contendo lista de registros ordenados, quantidade e variáveis.
    """
    _registrar_execucao("consultar_historico_leituras", {"maquina": maquina, "limit": limit})
    try:
        maq_valida = validar_maquina(maquina)
        limite_ajustado = max(5, min(200, int(limit)))
        df = obter_historico(servidor=servidor, maquina=maq_valida, limit=limite_ajustado)

        if df.empty:
            return {"erro": f"Nenhum registro histórico retornado para '{maq_valida}'."}

        # Converte o DataFrame para formato JSON serializável
        registros = df.to_dict(orient="records")
        for reg in registros:
            if "timestamp" in reg:
                reg["timestamp"] = str(reg["timestamp"])

        return {
            "maquina": maq_valida,
            "total_registros": len(registros),
            "colunas_disponiveis": [c for c in df.columns if c not in ("machine_id",)],
            "registros_resumo": registros[:10],  # Primeiros 10 para não exceder contexto
        }
    except Exception as err:
        return {"erro": f"Falha ao consultar histórico de {maquina}: {err}"}


def analisar_estatisticas_variavel(
    maquina: str,
    variavel: str,
    limit: int = 50,
    servidor: str = SERVIDOR_PADRAO,
) -> dict[str, Any]:
    """Calcula estatísticas completas de uma variável (comportamento habitual e regularidade).

    Use esta ferramenta para responder:
    - Qual o comportamento habitual (média, mediana, IQR)?
    - As medições são regulares ou oscilam muito (desvio padrão, variância, amplitude)?

    Args:
        maquina: Nome da máquina ('CENTRO-USINAGEM-01' ou 'FURADEIRA-01').
        variavel: Variável a analisar (ex: 'temperatura', 'vibracao', 'rotacao', 'corrente', 'pressao').
        limit: Número de registros do histórico a considerar (padrão 50).
        servidor: Endereço do servidor API (opcional).

    Returns:
        Dicionário com média, mediana, desvio padrão, amplitude, quartis e classificação.
    """
    _registrar_execucao(
        "analisar_estatisticas_variavel",
        {"maquina": maquina, "variavel": variavel, "limit": limit},
    )
    try:
        maq_valida = validar_maquina(maquina)
        df = obter_historico(servidor=servidor, maquina=maq_valida, limit=limit)
        var_limpa = variavel.strip().lower()

        if df.empty or var_limpa not in df.columns:
            return {
                "erro": f"Variável '{var_limpa}' não encontrada no histórico de '{maq_valida}'."
            }

        s = df[var_limpa].dropna()
        habitual = calcular_comportamento_habitual(s)
        regularidade = calcular_regularidade(s)

        return {
            "maquina": maq_valida,
            "variavel": var_limpa,
            "comportamento_habitual": habitual,
            "regularidade_e_oscilacao": regularidade,
        }
    except Exception as err:
        return {"erro": f"Erro no cálculo estatístico: {err}"}


def detectar_anomalias_outliers(
    maquina: str,
    variavel: str,
    limit: int = 50,
    servidor: str = SERVIDOR_PADRAO,
) -> dict[str, Any]:
    """Identifica medições que se afastam do padrão estatístico pelo método IQR de Tukey.

    Use esta ferramenta quando o usuário perguntar se existem registros incomuns,
    leituras suspeitas, picos ou anomalias em uma variável.

    Args:
        maquina: Nome da máquina ('CENTRO-USINAGEM-01' ou 'FURADEIRA-01').
        variavel: Nome da variável (ex: 'temperatura', 'vibracao', etc.).
        limit: Quantidade de registros a analisar (padrão 50).
        servidor: Endereço do servidor API (opcional).

    Returns:
        Limites inferior e superior pelo IQR, total de anomalias encontradas,
        detalhes de cada ponto atípico e ressalva técnica responsável.
    """
    _registrar_execucao(
        "detectar_anomalias_outliers",
        {"maquina": maquina, "variavel": variavel, "limit": limit},
    )
    try:
        maq_valida = validar_maquina(maquina)
        df = obter_historico(servidor=servidor, maquina=maq_valida, limit=limit)
        var_limpa = variavel.strip().lower()

        resultado = motor_detectar_anomalias(df, var_limpa)
        resultado["maquina"] = maq_valida
        return resultado
    except Exception as err:
        return {"erro": f"Erro na detecção de anomalias: {err}"}


def avaliar_tendencia_temporal(
    maquina: str,
    variavel: str,
    limit: int = 50,
    servidor: str = SERVIDOR_PADRAO,
) -> dict[str, Any]:
    """Avalia se uma variável apresenta aumento, redução ou estabilidade ao longo do tempo.

    Use esta ferramenta quando o usuário perguntar sobre evolução temporal,
    aquecimento contínuo, aumento de vibração ou tendência.

    Args:
        maquina: Nome da máquina ('CENTRO-USINAGEM-01' ou 'FURADEIRA-01').
        variavel: Nome da variável numérica a analisar.
        limit: Quantidade de registros históricos a considerar.
        servidor: Endereço do servidor API (opcional).

    Returns:
        Dicionário com inclinação linear (slope), R², variação total e diagnóstico de tendência.
    """
    _registrar_execucao(
        "avaliar_tendencia_temporal",
        {"maquina": maquina, "variavel": variavel, "limit": limit},
    )
    try:
        maq_valida = validar_maquina(maquina)
        df = obter_historico(servidor=servidor, maquina=maq_valida, limit=limit)
        var_limpa = variavel.strip().lower()

        res = calcular_tendencia_temporal(df, var_limpa)
        res["maquina"] = maq_valida
        return res
    except Exception as err:
        return {"erro": f"Erro ao calcular tendência temporal: {err}"}


def comparar_duas_maquinas(
    variavel: str,
    limit: int = 50,
    servidor: str = SERVIDOR_PADRAO,
) -> dict[str, Any]:
    """Compara estatisticamente CENTRO-USINAGEM-01 e FURADEIRA-01 em uma variável compatível.

    Use esta ferramenta quando o usuário pedir para comparar os dois equipamentos.
    A comparação só é permitida para grandezas físicas com unidades compatíveis
    (ex: 'temperatura' em °C ou 'vibracao' em mm/s). Variáveis incompatíveis são bloqueadas.

    Args:
        variavel: Nome da variável a comparar (ex: 'temperatura', 'vibracao').
        limit: Registros históricos a considerar para cada máquina.
        servidor: Endereço do servidor API (opcional).

    Returns:
        Dicionário comparando médias, dispersão, extremos e ressalva de engenharia.
    """
    _registrar_execucao("comparar_duas_maquinas", {"variavel": variavel, "limit": limit})
    try:
        maq_a = "CENTRO-USINAGEM-01"
        maq_b = "FURADEIRA-01"

        df_a = obter_historico(servidor=servidor, maquina=maq_a, limit=limit)
        df_b = obter_historico(servidor=servidor, maquina=maq_b, limit=limit)

        return comparar_maquinas(df_a, df_b, maq_a, maq_b, variavel.strip().lower())
    except Exception as err:
        return {"erro": f"Bloqueio ou erro na comparação: {err}"}


def obter_declaracao_e_limites() -> dict[str, Any]:
    """Retorna as diretrizes éticas, limites de interpretação e aviso de ambiente didático.

    Use quando o usuário fizer perguntas especulativas sobre 'qual máquina vai falhar primeiro'
    ou solicitar garantias de diagnóstico definitivo.

    Returns:
        Declaração oficial sobre natureza didática e limites de interpretação.
    """
    _registrar_execucao("obter_declaracao_e_limites", {})
    return {
        "aviso_didatico": DECLARACAO_DADOS_DIDATICOS,
        "limites_de_interpretacao": (
            "1. Os dados são provenientes de simulação educacional do AI DataLab.\n"
            "2. Leituras anômalas ou tendências indicam apenas necessidade de averiguação técnica.\n"
            "3. É cientificamente impossível prever falha iminente sem modelos de confiabilidade "
            "e histórico de ordens de serviço reais."
        ),
    }


# Lista de todas as ferramentas disponíveis para o cliente Gemini
FERRAMENTAS_GEMINI = [
    consultar_ultima_leitura_maquina,
    consultar_historico_leituras,
    analisar_estatisticas_variavel,
    detectar_anomalias_outliers,
    avaliar_tendencia_temporal,
    comparar_duas_maquinas,
    obter_declaracao_e_limites,
]
