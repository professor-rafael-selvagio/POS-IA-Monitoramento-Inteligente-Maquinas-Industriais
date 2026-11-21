"""Módulo de Conexão HTTP com a API do AI DataLab.

Implementa os endpoints de consulta de última leitura e histórico de leituras
para as máquinas CENTRO-USINAGEM-01 e FURADEIRA-01, com validação estrita,
tratamento robusto de falhas e suporte a dados didáticos de contingência.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
import random
from typing import Any

import numpy as np
import pandas as pd
import requests

from config import (
    DECLARACAO_DADOS_DIDATICOS,
    METADADOS_VARIAVEIS,
    TIMEOUT_PADRAO,
    validar_maquina,
)

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """Exceção levantada para erros de comunicação com a API do AI DataLab."""


def testar_conexao(servidor: str, timeout: int = 3) -> bool:
    """Verifica se o servidor do AI DataLab está acessível via HTTP.

    Args:
        servidor: Endereço base da API (ex: http://10.110.18.12:10999).
        timeout: Tempo limite de espera em segundos.

    Returns:
        True se o servidor responder com status < 500, False caso contrário.
    """
    url = f"{servidor.rstrip('/')}/api/v1/health"
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code < 500
    except requests.RequestException:
        # Tenta endpoint alternativo de máquinas se /health não existir
        try:
            url_alt = f"{servidor.rstrip('/')}/api/v1/machines"
            resp_alt = requests.get(url_alt, timeout=timeout)
            return resp_alt.status_code < 500
        except requests.RequestException:
            return False


def obter_ultima_leitura(
    servidor: str,
    maquina: str,
    timeout: int = TIMEOUT_PADRAO,
    usar_fallback_se_offline: bool = True,
) -> dict[str, Any]:
    """Consulta as medições mais recentes da máquina selecionada.

    Atende aos Requisitos Funcionais RF04, RF05, RF17 e RF18.

    Args:
        servidor: URL base da API do AI DataLab.
        maquina: Identificador da máquina (CENTRO-USINAGEM-01 ou FURADEIRA-01).
        timeout: Tempo limite em segundos para a requisição.
        usar_fallback_se_offline: Se True, retorna dados didáticos simulados caso o
            servidor do laboratório esteja inacessível fora da rede física.

    Returns:
        Dicionário contendo machine_id, timestamp, medições e metadados.

    Raises:
        ValueError: Se a máquina informada não for autorizada.
        APIClientError: Se houver erro de rede e o fallback estiver desativado.
    """
    maquina_valida = validar_maquina(maquina)
    url = f"{servidor.rstrip('/')}/api/v1/machines/{maquina_valida}/latest"

    try:
        logger.info("Consultando última leitura: %s", url)
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        dados = resp.json()

        # Garante normalização do formato de saída
        return _normalizar_ultima_leitura(dados, maquina_valida, simulado=False)

    except requests.RequestException as err:
        msg_erro = (
            f"Falha de conexão com a API do AI DataLab em '{url}': {err}. "
            "Verifique se o endereço do servidor está correto e acessível na rede."
        )
        logger.warning(msg_erro)

        if usar_fallback_se_offline:
            logger.info("Acionando gerador de contingência didática para %s", maquina_valida)
            return gerar_dados_didaticos_ultima_leitura(maquina_valida)

        raise APIClientError(msg_erro) from err


def obter_historico(
    servidor: str,
    maquina: str,
    limit: int = 100,
    timeout: int = TIMEOUT_PADRAO,
    usar_fallback_se_offline: bool = True,
) -> pd.DataFrame:
    """Consulta os registros históricos de telemetria da máquina especificada.

    Atende aos Requisitos Funcionais RF07, RF08, RF17 e RF18.

    Args:
        servidor: URL base da API do AI DataLab.
        maquina: Identificador da máquina (CENTRO-USINAGEM-01 ou FURADEIRA-01).
        limit: Quantidade de registros solicitados à API.
        timeout: Tempo limite em segundos para a requisição.
        usar_fallback_se_offline: Se True, retorna série histórica simulada caso a
            API esteja indisponível.

    Returns:
        pd.DataFrame ordenado cronologicamente com colunas de timestamp e variáveis.

    Raises:
        ValueError: Se a máquina informada não for autorizada.
        APIClientError: Se houver erro de rede e o fallback estiver desativado.
    """
    maquina_valida = validar_maquina(maquina)
    url = f"{servidor.rstrip('/')}/api/v1/machines/{maquina_valida}/readings"

    try:
        logger.info("Consultando histórico: %s (limit=%d)", url, limit)
        resp = requests.get(url, params={"limit": limit}, timeout=timeout)
        resp.raise_for_status()
        dados = resp.json()

        df = _normalizar_historico_para_df(dados, maquina_valida)
        if df.empty and usar_fallback_se_offline:
            return gerar_dados_didaticos_historico(maquina_valida, limit=limit)
        return df

    except requests.RequestException as err:
        msg_erro = (
            f"Não foi possível obter o histórico de '{maquina_valida}' em '{url}': {err}."
        )
        logger.warning(msg_erro)

        if usar_fallback_se_offline:
            logger.info("Acionando histórico de contingência didática para %s", maquina_valida)
            return gerar_dados_didaticos_historico(maquina_valida, limit=limit)

        raise APIClientError(msg_erro) from err


def _normalizar_ultima_leitura(dados: dict | list, maquina: str, simulado: bool = False) -> dict[str, Any]:
    """Padroniza o dicionário de última leitura com medições, unidades e metadados."""
    if isinstance(dados, list):
        dados = dados[0] if dados else {}

    timestamp = dados.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    machine_id = dados.get("machine_id") or dados.get("machine") or maquina

    medicoes: dict[str, dict[str, Any]] = {}
    metas = METADADOS_VARIAVEIS.get(maquina, {})

    # Se a API retornou no padrão nested {'readings': {'temperatura': ...}}
    conteudo = dados.get("readings") or dados.get("data") or dados

    for var, meta in metas.items():
        valor = None
        if var in conteudo:
            item = conteudo[var]
            if isinstance(item, dict) and "value" in item:
                valor = item["value"]
            elif isinstance(item, (int, float)):
                valor = item
        elif var in dados:
            valor = dados[var]

        if valor is not None:
            medicoes[var] = {
                "nome": meta["nome_exibicao"],
                "valor": round(float(valor), 2),
                "unidade": meta["unidade"],
                "grandeza": meta["grandeza"],
            }

    return {
        "machine_id": machine_id,
        "timestamp": str(timestamp),
        "medicoes": medicoes,
        "simulado": simulado,
        "aviso_didatico": DECLARACAO_DADOS_DIDATICOS,
    }


def _normalizar_historico_para_df(dados: Any, maquina: str) -> pd.DataFrame:
    """Converte o retorno de histórico da API para um DataFrame Pandas limpo e ordenado."""
    lista_registros: list[dict[str, Any]] = []

    if isinstance(dados, dict):
        for chave in ("readings", "data", "results", "records", "history", "items"):
            if chave in dados and isinstance(dados[chave], list):
                lista_registros = dados[chave]
                break
        if not lista_registros and any(k in dados for k in ("timestamp", "readings", "data")):
            lista_registros = [dados]
    elif isinstance(dados, list):
        lista_registros = dados

    if not lista_registros:
        return pd.DataFrame()

    linhas_limpas = []
    metas = METADADOS_VARIAVEIS.get(maquina, {})
    mapa_metas = {v.lower(): v for v in metas}

    for idx, item in enumerate(lista_registros):
        if not isinstance(item, dict):
            continue
        ts = (
            item.get("timestamp")
            or item.get("horario")
            or item.get("created_at")
            or item.get("time")
            or item.get("data")
            or item.get("datetime")
            or item.get("data_hora")
            or item.get("date")
        )
        if not ts:
            ts = datetime.now() - timedelta(minutes=(len(lista_registros) - idx) * 2)

        linha: dict[str, Any] = {"timestamp": ts, "machine_id": maquina}
        conteudo = item.get("readings") or item.get("data") or item

        if isinstance(conteudo, dict):
            for k, val_raw in conteudo.items():
                k_clean = str(k).lower().strip()
                var_alvo = mapa_metas.get(k_clean, k_clean)

                if var_alvo in ("timestamp", "machine_id", "machine", "id", "created_at", "simulado"):
                    continue

                val = None
                if isinstance(val_raw, dict) and "value" in val_raw:
                    val = val_raw["value"]
                elif isinstance(val_raw, (int, float, str)):
                    try:
                        val = float(val_raw)
                    except (ValueError, TypeError):
                        pass

                if val is not None:
                    linha[var_alvo] = round(float(val), 3)

        linhas_limpas.append(linha)

    if not linhas_limpas:
        return pd.DataFrame()

    df = pd.DataFrame(linhas_limpas)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["timestamp"] = df["timestamp"].fillna(pd.Timestamp.now())
        df = df.sort_values("timestamp").reset_index(drop=True)

    colunas_numericas = [
        c for c in df.columns
        if c not in ("timestamp", "machine_id") and pd.api.types.is_numeric_dtype(df[c])
    ]
    if not colunas_numericas:
        return pd.DataFrame()

    return df


# ─────────────────────────────────────────────────────────────────────────────
# GERADORES DE CONTINGÊNCIA DIDÁTICA (AI DataLab Sandbox Offline Fallback)
# ─────────────────────────────────────────────────────────────────────────────

def gerar_dados_didaticos_ultima_leitura(maquina: str) -> dict[str, Any]:
    """Gera uma leitura instantânea coerente para permitir teste sem conexão física à rede."""
    validar_maquina(maquina)
    agora = datetime.now()

    if maquina == "CENTRO-USINAGEM-01":
        dados = {
            "temperatura": 58.4 + random.uniform(-0.5, 0.5),
            "vibracao": 2.15 + random.uniform(-0.1, 0.1),
            "rotacao": 4200.0 + random.uniform(-20, 20),
            "corrente": 16.8 + random.uniform(-0.3, 0.3),
        }
    else:  # FURADEIRA-01
        dados = {
            "temperatura": 44.2 + random.uniform(-0.4, 0.4),
            "vibracao": 1.62 + random.uniform(-0.08, 0.08),
            "rotacao": 1450.0 + random.uniform(-15, 15),
            "pressao": 6.2 + random.uniform(-0.1, 0.1),
        }

    return _normalizar_ultima_leitura(
        {
            "machine_id": maquina,
            "timestamp": agora.strftime("%Y-%m-%d %H:%M:%S"),
            "readings": dados,
        },
        maquina,
        simulado=True,
    )


def gerar_dados_didaticos_historico(maquina: str, limit: int = 100) -> pd.DataFrame:
    """Gera uma série temporal realista com cenários da Situação de Aprendizagem.

    - CENTRO-USINAGEM-01: Apresenta leve tendência linear de elevação térmica (Desafio D).
    - FURADEIRA-01: Apresenta regime estável com 2 outliers claros de vibração (Desafio C).
    """
    validar_maquina(maquina)
    np.random.seed(42 if maquina == "CENTRO-USINAGEM-01" else 101)

    inicio = datetime.now() - timedelta(minutes=limit * 2)
    timestamps = [inicio + timedelta(minutes=i * 2) for i in range(limit)]

    t = np.linspace(0, 1, limit)

    if maquina == "CENTRO-USINAGEM-01":
        # Desafio D: Tendência gradual de aumento de temperatura ao longo do tempo (+7°C)
        temp_base = 52.0 + 7.5 * t + np.random.normal(0, 0.6, limit)
        # Vibração moderada com oscilações normais de corte
        vib_base = 1.9 + 0.3 * np.sin(2 * np.pi * t * 3) + np.random.normal(0, 0.12, limit)
        # Rotação em regime de usinagem com pequenas variações de carga
        rot_base = 4200.0 + np.random.normal(0, 25.0, limit)
        # Corrente oscila com a força de corte
        corr_base = 15.5 + 1.2 * np.sin(2 * np.pi * t * 2) + np.random.normal(0, 0.4, limit)

        df = pd.DataFrame({
            "timestamp": timestamps,
            "machine_id": maquina,
            "temperatura": np.round(temp_base, 2),
            "vibracao": np.round(np.maximum(0.1, vib_base), 3),
            "rotacao": np.round(rot_base, 1),
            "corrente": np.round(corr_base, 2),
        })

    else:  # FURADEIRA-01
        # Desafio C: Série estável com registro incomum / anomalia destacável
        temp_base = 42.0 + np.random.normal(0, 0.5, limit)
        vib_base = 1.4 + np.random.normal(0, 0.1, limit)
        rot_base = 1450.0 + np.random.normal(0, 12.0, limit)
        press_base = 6.2 + np.random.normal(0, 0.15, limit)

        # Inserção didática intencional de 2 outliers claros de vibração (Desafio C)
        if limit > 25:
            vib_base[int(limit * 0.4)] = 3.95  # Ponto atípico evidente
        if limit > 70:
            vib_base[int(limit * 0.75)] = 4.20  # Segundo pico atípico

        df = pd.DataFrame({
            "timestamp": timestamps,
            "machine_id": maquina,
            "temperatura": np.round(temp_base, 2),
            "vibracao": np.round(np.maximum(0.1, vib_base), 3),
            "rotacao": np.round(rot_base, 1),
            "pressao": np.round(press_base, 2),
        })

    return df
