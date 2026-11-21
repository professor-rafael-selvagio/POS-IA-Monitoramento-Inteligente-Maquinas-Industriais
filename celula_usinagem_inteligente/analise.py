"""Motor Estatístico e Análise Industrial da Célula de Usinagem.

Implementa os cálculos matemáticos e estatísticos que atendem aos Desafios A a F
da Situação de Aprendizagem e aos Requisitos Funcionais RF10 a RF14, RF19 e RF20:
- Desafio A (RF10): Comportamento Habitual (média, mediana, IQR, assimetria).
- Desafio B (RF11): Regularidade e Oscilação (desvio padrão, variância, amplitude, CV).
- Desafio C (RF12): Registros Incomuns / Outliers via Intervalo Interquartil (IQR).
- Desafio D (RF13): Mudança Temporal / Tendência via Regressão Linear Simples.
- Desafio E (RF14): Comparação Segura e Validada entre Máquinas.
- Desafio F (RF19/RF20): Declaração de Limites, Amostragem e Caráter Didático.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from config import (
    DECLARACAO_DADOS_DIDATICOS,
    GRANDEZAS_COMPARAVEIS,
    METADADOS_VARIAVEIS,
    validar_maquina,
)

logger = logging.getLogger(__name__)


def calcular_comportamento_habitual(serie: pd.Series | np.ndarray) -> dict[str, Any]:
    """Calcula os indicadores do comportamento habitual de uma variável industrial.

    Atende ao Desafio A e ao Requisito Funcional RF10.

    Args:
        serie: Série numérica contendo as medições temporais.

    Returns:
        Dicionário com média, mediana, quartis, IQR e interpretação de assimetria.
    """
    s = pd.Series(serie).dropna()
    if s.empty:
        return {"erro": "Série de dados vazia para cálculo de comportamento habitual."}

    media = float(s.mean())
    mediana = float(s.median())
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = float(q3 - q1)
    desvio_padrao = float(s.std(ddof=1)) if len(s) > 1 else 0.0

    # Desvio Absoluto Mediano (MAD - Median Absolute Deviation)
    mad = float(np.median(np.abs(s - mediana)))

    # Coeficiente de assimetria não-paramétrico de Pearson
    if desvio_padrao > 0:
        assimetria = (media - mediana) / desvio_padrao
    else:
        assimetria = 0.0

    # Avaliação qualitativa da representatividade
    if abs(assimetria) < 0.15:
        interpretacao = (
            "Comportamento simétrico: a média e a mediana são muito próximas, "
            "sendo a média uma boa representação central do processo."
        )
    elif assimetria > 0:
        interpretacao = (
            f"Assimetria positiva (média {media:.2f} > mediana {mediana:.2f}): "
            "a ocorrência de leituras pontualmente mais altas puxou a média para cima. "
            "A mediana representa melhor o valor típico de operação."
        )
    else:
        interpretacao = (
            f"Assimetria negativa (média {media:.2f} < mediana {mediana:.2f}): "
            "a ocorrência de leituras pontualmente mais baixas puxou a média para baixo. "
            "A mediana representa melhor o valor típico de operação."
        )

    return {
        "amostras": int(len(s)),
        "media": round(media, 3),
        "mediana": round(mediana, 3),
        "q1_25pct": round(q1, 3),
        "q3_75pct": round(q3, 3),
        "iqr": round(iqr, 3),
        "mad": round(mad, 3),
        "assimetria_pearson": round(assimetria, 3),
        "interpretacao": interpretacao,
    }


def calcular_regularidade(serie: pd.Series | np.ndarray) -> dict[str, Any]:
    """Avalia a estabilidade, dispersão e intensidade das oscilações operacionais.

    Atende ao Desafio B e ao Requisito Funcional RF11.

    Args:
        serie: Série numérica das medições.

    Returns:
        Dicionário com desvio padrão, variância, amplitude e classificação.
    """
    s = pd.Series(serie).dropna()
    if s.empty:
        return {"erro": "Série de dados vazia para cálculo de regularidade."}

    n = len(s)
    desvio_padrao = float(s.std(ddof=1)) if n > 1 else 0.0
    variancia = float(s.var(ddof=1)) if n > 1 else 0.0
    minimo = float(s.min())
    maximo = float(s.max())
    amplitude = float(maximo - minimo)
    media = float(s.mean())

    # Coeficiente de Variação (CV %)
    cv_pct = (desvio_padrao / abs(media) * 100.0) if abs(media) > 1e-6 else 0.0

    if cv_pct < 5.0:
        classificacao = "Alta Estabilidade (oscilações insignificantes em regime permanente)"
    elif cv_pct < 15.0:
        classificacao = "Estabilidade Moderada (oscilações normais inerentes ao ciclo de corte)"
    else:
        classificacao = "Alta Dispersão / Oscilação Intensa (ampla variação que merece investigação)"

    return {
        "amostras": int(n),
        "desvio_padrao": round(desvio_padrao, 3),
        "variancia": round(variancia, 3),
        "amplitude_total": round(amplitude, 3),
        "valor_minimo": round(minimo, 3),
        "valor_maximo": round(maximo, 3),
        "coeficiente_variacao_pct": round(cv_pct, 2),
        "classificacao_regularidade": classificacao,
    }


def detectar_registros_incomuns(
    df: pd.DataFrame,
    variavel: str,
    fator_iqr: float = 1.5,
) -> dict[str, Any]:
    """Identifica medições que se afastam substancialmente das demais usando IQR.

    Atende ao Desafio C e ao Requisito Funcional RF12.
    Utiliza o método de Tukey (Boxplot), mundialmente aceito em controle de qualidade
    industrial por não assumir normalidade estrita dos dados e ser imune a distorções
    dos próprios pontos anômalos.

    Critério Explícito:
    - Q1 = 1º Quartil (25%)
    - Q3 = 3º Quartil (75%)
    - IQR = Q3 - Q1
    - Limite Inferior = Q1 - 1.5 * IQR
    - Limite Superior = Q3 + 1.5 * IQR

    Args:
        df: DataFrame contendo a série temporal e coluna da variável.
        variavel: Nome da coluna numérica a analisar.
        fator_iqr: Multiplicador do IQR (padrão 1.5 para outliers moderados).

    Returns:
        Dicionário com limites numéricos, lista de anomalias detectadas e justificativa.
    """
    if df.empty or variavel not in df.columns:
        return {"erro": f"Variável '{variavel}' ausente no conjunto de dados."}

    s = df[variavel].dropna()
    if len(s) < 4:
        return {
            "erro": "Amostragem insuficiente para detecção confiável por IQR (mínimo de 4 registros)."
        }

    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = float(q3 - q1)
    limite_inf = float(q1 - fator_iqr * iqr)
    limite_sup = float(q3 + fator_iqr * iqr)

    # Identifica máscaras booleanas
    mascara_inferior = df[variavel] < limite_inf
    mascara_superior = df[variavel] > limite_sup
    mascara_outliers = mascara_inferior | mascara_superior

    df_anomalias = df[mascara_outliers].copy()
    registros_anomalos = []

    for idx, row in df_anomalias.iterrows():
        val = float(row[variavel])
        tipo = "Acima do Limite Superior" if val > limite_sup else "Abaixo do Limite Inferior"
        dist_iqr = round(abs(val - (q3 if val > limite_sup else q1)) / (iqr if iqr > 0 else 1.0), 2)

        ts_str = str(row["timestamp"]) if "timestamp" in row else str(idx)
        registros_anomalos.append({
            "indice": int(idx),
            "timestamp": ts_str,
            "valor": round(val, 3),
            "tipo": tipo,
            "distancia_iqr": dist_iqr,
        })

    qtd_anomalias = len(registros_anomalos)
    pct_anomalias = round((qtd_anomalias / len(df)) * 100.0, 2)

    return {
        "variavel": variavel,
        "total_registros_analisados": int(len(df)),
        "quantidade_anomalias": qtd_anomalias,
        "percentual_anomalias_pct": pct_anomalias,
        "q1_25pct": round(q1, 3),
        "q3_75pct": round(q3, 3),
        "iqr": round(iqr, 3),
        "limite_inferior": round(limite_inf, 3),
        "limite_superior": round(limite_sup, 3),
        "criterio_adotado": f"Método de Tukey: IQR com fator multiplicador {fator_iqr}",
        "registros_anomalos": registros_anomalos,
        "ressalva_tecnica": (
            "ATENÇÃO: A detecção de registro incomum aponta dados que divergem do "
            "padrão estatístico do intervalo, servindo como ponto de investigação técnica "
            "para a manutenção, e NUNCA como comprovação direta de defeito mecânico."
        ),
    }


def calcular_tendencia_temporal(df: pd.DataFrame, variavel: str) -> dict[str, Any]:
    """Estima a tendência de mudança ao longo do tempo via Regressão Linear Simples.

    Atende ao Desafio D e ao Requisito Funcional RF13.
    Ajusta a reta y = a*x + b sobre os registros ordenados temporalmente.

    Args:
        df: DataFrame ordenado cronologicamente.
        variavel: Nome da variável a analisar.

    Returns:
        Dicionário com inclinação (slope), intercepto, R², variação estimada e direção.
    """
    if df.empty or variavel not in df.columns:
        return {"erro": f"Variável '{variavel}' ausente no conjunto de dados."}

    df_limpo = df.dropna(subset=[variavel]).copy()
    n = len(df_limpo)
    if n < 3:
        return {"erro": "Mínimo de 3 registros temporais para regressão linear."}

    y = df_limpo[variavel].to_numpy(dtype=float)
    x = np.arange(n, dtype=float)

    # Ajuste de Mínimos Quadrados Ordinários (OLS)
    slope, intercept = np.polyfit(x, y, 1)

    # Coeficiente de Determinação R²
    y_pred = slope * x + intercept
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - y_pred) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-9 else 0.0

    variacao_total_estimada = slope * (n - 1)
    val_inicial = float(y[0])
    val_final = float(y[-1])
    variacao_real_extremos = val_final - val_inicial

    # Limiar relativo de significância (0.1% do valor médio por período)
    media_abs = abs(float(np.mean(y)))
    limiar_slope = max(1e-4, 0.001 * media_abs)

    if slope > limiar_slope and r2 >= 0.20:
        direcao = "Tendência de Elevação (Aumento gradual ao longo do período)"
    elif slope < -limiar_slope and r2 >= 0.20:
        direcao = "Tendência de Redução (Declínio gradual ao longo do período)"
    else:
        direcao = "Estabilidade Temporal (Sem tendência de direção definida; processo oscila em torno da média)"

    return {
        "variavel": variavel,
        "amostras": int(n),
        "inclinacao_slope": round(float(slope), 5),
        "intercepto": round(float(intercept), 3),
        "coeficiente_determinacao_r2": round(float(max(0.0, r2)), 4),
        "variacao_estimada_modelo": round(float(variacao_total_estimada), 3),
        "valor_inicial": round(val_inicial, 3),
        "valor_final": round(val_final, 3),
        "variacao_extremos": round(float(variacao_real_extremos), 3),
        "direcao_tendencia": direcao,
        "valores_ajustados": [round(float(v), 3) for v in y_pred],
    }


def comparar_maquinas(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    maquina_a: str,
    maquina_b: str,
    variavel: str,
) -> dict[str, Any]:
    """Compara estatisticamente o comportamento de uma variável entre duas máquinas.

    Atende ao Desafio E e ao Requisito Funcional RF14.
    Valida estritamente se as grandezas e unidades físicas são compatíveis antes
    de executar qualquer comparação.

    Args:
        df_a: Histórico da Máquina A.
        df_b: Histórico da Máquina B.
        maquina_a: Nome da Máquina A (ex: CENTRO-USINAGEM-01).
        maquina_b: Nome da Máquina B (ex: FURADEIRA-01).
        variavel: Variável a ser comparada.

    Returns:
        Dicionário comparativo de médias, dispersão, extremos e ressalvas operacionais.

    Raises:
        ValueError: Se a máquina for inválida ou se as grandezas forem incompatíveis.
    """
    maq_a = validar_maquina(maquina_a)
    maq_b = validar_maquina(maquina_b)

    if maq_a == maq_b:
        raise ValueError("A comparação requer duas máquinas distintas.")

    meta_a = METADADOS_VARIAVEIS.get(maq_a, {}).get(variavel)
    meta_b = METADADOS_VARIAVEIS.get(maq_b, {}).get(variavel)

    if not meta_a:
        raise ValueError(
            f"A máquina '{maq_a}' não monitora a variável '{variavel}'. "
            f"Variáveis disponíveis: {list(METADADOS_VARIAVEIS.get(maq_a, {}).keys())}."
        )

    if not meta_b:
        raise ValueError(
            f"A máquina '{maq_b}' não monitora a variável '{variavel}'. "
            f"Variáveis disponíveis: {list(METADADOS_VARIAVEIS.get(maq_b, {}).keys())}."
        )

    # Validação estrita de grandeza e unidade física (RF14)
    if meta_a["grandeza"] != meta_b["grandeza"] or meta_a["unidade"] != meta_b["unidade"]:
        raise ValueError(
            f"Bloqueio de comparação incompatível (RF14): "
            f"'{maq_a}.{variavel}' ({meta_a['grandeza']} em {meta_a['unidade']}) "
            f"não pode ser comparada com '{maq_b}.{variavel}' ({meta_b['grandeza']} em {meta_b['unidade']})."
        )

    if df_a.empty or variavel not in df_a.columns:
        return {"erro": f"Dados ausentes para '{maq_a}' na variável '{variavel}'."}
    if df_b.empty or variavel not in df_b.columns:
        return {"erro": f"Dados ausentes para '{maq_b}' na variável '{variavel}'."}

    s_a = df_a[variavel].dropna()
    s_b = df_b[variavel].dropna()

    habitual_a = calcular_comportamento_habitual(s_a)
    habitual_b = calcular_comportamento_habitual(s_b)
    regularidade_a = calcular_regularidade(s_a)
    regularidade_b = calcular_regularidade(s_b)

    diff_medias = habitual_a["media"] - habitual_b["media"]
    diff_medianas = habitual_a["mediana"] - habitual_b["mediana"]

    return {
        "variavel": variavel,
        "grandeza": meta_a["grandeza"],
        "unidade": meta_a["unidade"],
        "maquina_a": {
            "nome": maq_a,
            "amostras": len(s_a),
            "media": habitual_a["media"],
            "mediana": habitual_a["mediana"],
            "desvio_padrao": regularidade_a["desvio_padrao"],
            "amplitude": regularidade_a["amplitude_total"],
            "min": regularidade_a["valor_minimo"],
            "max": regularidade_a["valor_maximo"],
        },
        "maquina_b": {
            "nome": maq_b,
            "amostras": len(s_b),
            "media": habitual_b["media"],
            "mediana": habitual_b["mediana"],
            "desvio_padrao": regularidade_b["desvio_padrao"],
            "amplitude": regularidade_b["amplitude_total"],
            "min": regularidade_b["valor_minimo"],
            "max": regularidade_b["valor_maximo"],
        },
        "comparativo": {
            "diferenca_medias_a_menos_b": round(diff_medias, 3),
            "diferenca_medianas_a_menos_b": round(diff_medianas, 3),
            "maior_media": maq_a if diff_medias > 0 else maq_b,
            "maior_dispersao": (
                maq_a
                if regularidade_a["desvio_padrao"] > regularidade_b["desvio_padrao"]
                else maq_b
            ),
        },
        "ressalva_operacional": (
            f"Embora ambas as medições compartilhem a mesma unidade ({meta_a['unidade']}), "
            f"{maq_a} e {maq_b} possuem projetos construtivos, potências de motor e esforços de "
            "corte distintos. A comparação deve contextualizar as condições operacionais de cada máquina."
        ),
    }


def gerar_relatorio_completo_variavel(
    df: pd.DataFrame,
    maquina: str,
    variavel: str,
) -> dict[str, Any]:
    """Gera o dossiê analítico consolidado cobrindo todos os Desafios A a F.

    Atende aos Requisitos Funcionais RF10 a RF14, RF19 e RF20.
    """
    maq = validar_maquina(maquina)
    if df.empty or variavel not in df.columns:
        return {"erro": f"Variável '{variavel}' ausente no histórico da máquina '{maq}'."}

    s = df[variavel].dropna()
    meta = METADADOS_VARIAVEIS.get(maq, {}).get(variavel, {})

    periodo_ini = str(df["timestamp"].iloc[0]) if "timestamp" in df.columns else "N/A"
    periodo_fim = str(df["timestamp"].iloc[-1]) if "timestamp" in df.columns else "N/A"

    habitual = calcular_comportamento_habitual(s)
    regularidade = calcular_regularidade(s)
    anomalias = detectar_registros_incomuns(df, variavel)
    tendencia = calcular_tendencia_temporal(df, variavel)

    # Avaliação de suficiência amostral (RF19)
    suficiencia_amostral = "Adequada" if len(s) >= 30 else "Baixa (interpretar com cautela)"

    return {
        "maquina": maq,
        "variavel": variavel,
        "nome_exibicao": meta.get("nome_exibicao", variavel),
        "unidade": meta.get("unidade", ""),
        "periodo_registros": {"inicio": periodo_ini, "fim": periodo_fim},
        "total_amostras": len(s),
        "suficiencia_amostral": suficiencia_amostral,
        "desafio_a_habitual": habitual,
        "desafio_b_regularidade": regularidade,
        "desafio_c_registros_incomuns": anomalias,
        "desafio_d_tendencia_temporal": tendencia,
        "desafio_f_limites_e_responsabilidade": {
            "declaracao": DECLARACAO_DADOS_DIDATICOS,
            "conclusao_prudente": (
                "Os indicadores evidenciam o comportamento estatístico da série simulada. "
                "Quaisquer decisões de manutenção preventiva requerem inspeção presencial e "
                "medição com instrumentos calibrados in loco."
            ),
        },
    }
