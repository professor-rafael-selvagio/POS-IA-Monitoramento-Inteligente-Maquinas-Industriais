"""Aplicação Web de Monitoramento e Análise Inteligente de Célula de Usinagem.

Desenvolvida com Streamlit, AI DataLab, Google Gemini e Function Calling.
Atende integralmente aos Requisitos Funcionais RF01 a RF20 e aos Desafios A a F.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

# Módulos internos do projeto
from analise import (
    calcular_comportamento_habitual,
    calcular_regularidade,
    calcular_tendencia_temporal,
    comparar_maquinas,
    detectar_registros_incomuns,
    gerar_relatorio_completo_variavel,
)
from api_client import (
    APIClientError,
    obter_historico,
    obter_ultima_leitura,
    testar_conexao,
)
from assistente import AssistenteGemini
from config import (
    DECLARACAO_DADOS_DIDATICOS,
    GRANDEZAS_COMPARAVEIS,
    MAQUINAS_VALIDAS,
    METADADOS_VARIAVEIS,
    MODELO_GEMINI_PADRAO,
    SERVIDOR_PADRAO,
    TIMEOUT_PADRAO,
    validar_maquina,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Célula de Usinagem Inteligente | AI DataLab",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS refinada para visual industrial moderno
st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 6px 0;
    }
    .metric-unit {
        color: #38bdf8;
        font-size: 1.1rem;
        font-weight: 500;
        margin-left: 4px;
    }
    .stAlert {
        border-radius: 10px;
    }
    .tool-pill {
        display: inline-block;
        background-color: #0284c7;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# GESTÃO DE ESTADO DA SESSÃO (SESSION STATE)
# ─────────────────────────────────────────────────────────────────────────────

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Olá! Sou o Assistente Técnico Especialista da Célula de Usinagem. "
                "Posso consultar as leituras atuais, analisar históricos e verificar tendências "
                "ou anomalias no **Centro de Usinagem CNC** e na **Furadeira Industrial** via Function Calling. "
                "Como posso auxiliar a manutenção hoje?"
            ),
            "tools": [],
        }
    ]

if "dados_atualizados_em" not in st.session_state:
    st.session_state.dados_atualizados_em = datetime.now()

# ─────────────────────────────────────────────────────────────────────────────
# BARRA LATERAL (SIDEBAR) - CONFIGURAÇÕES E SELEÇÃO
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/feathericons/feather/master/icons/cpu.svg",
        width=48,
    )
    st.title("Célula de Usinagem")
    st.caption("Monitoramento & Análise Inteligente 4.0")
    st.divider()

    st.subheader("⚙️ Configurações da API")
    # RF02: Configuração do endereço do servidor
    servidor_input = st.text_input(
        "Servidor AI DataLab:",
        value=os.getenv("SERVIDOR_API", SERVIDOR_PADRAO),
        help="Endereço HTTP do backend didático AI DataLab.",
    )

    # Verificação de status de conexão com servidor
    servidor_online = testar_conexao(servidor_input, timeout=2)
    if servidor_online:
        st.success("🟢 Servidor AI DataLab Online", icon="✅")
    else:
        st.warning("🟡 Servidor Lab Offline (Modo Contingência Didática Ativo)", icon="⚠️")

    st.divider()

    st.subheader("🏭 Seleção de Equipamento")
    # RF03: Seleção estrita entre as máquinas autorizadas
    maquina_selecionada = st.selectbox(
        "Selecione a Máquina:",
        options=MAQUINAS_VALIDAS,
        index=0,
        help="Selecione qual equipamento monitorar nesta sessão.",
    )

    st.divider()

    st.subheader("🤖 Assistente Gemini")
    gemini_key_env = os.getenv("GEMINI_API_KEY", "")
    gemini_key_input = st.text_input(
        "Gemini API Key:",
        value=gemini_key_env,
        type="password",
        help="Chave de API do Google Gemini. Pode ser configurada via variável de ambiente GEMINI_API_KEY.",
    )

    modelo_selecionado = st.selectbox(
        "Modelo Gemini:",
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"],
        index=0,
    )

    st.divider()

    # RF06: Botão de atualização sob demanda
    if st.button("🔄 Atualizar Dados Agora", use_container_width=True, type="primary"):
        st.session_state.dados_atualizados_em = datetime.now()
        st.toast("Dados da telemetria atualizados com sucesso!", icon="🔄")
        st.rerun()

    st.caption(f"Última checagem: {st.session_state.dados_atualizados_em.strftime('%H:%M:%S')}")

    # RF19: Declaração de limites e dados didáticos
    with st.expander("ℹ️ Declaração de Dados Didáticos"):
        st.info(DECLARACAO_DADOS_DIDATICOS)


# ─────────────────────────────────────────────────────────────────────────────
# CORPO PRINCIPAL: CABEÇALHO E NAVEGAÇÃO POR ABAS
# ─────────────────────────────────────────────────────────────────────────────

st.title(f"🏭 {maquina_selecionada}")
st.markdown(
    f"Painel integrado de telemetria, análise estatística e IA para o **{maquina_selecionada}**."
)

# Abas principais da aplicação
tab_atual, tab_historico, tab_analise, tab_assistente = st.tabs([
    "📊 Telemetria Atual",
    "📈 Histórico & Gráficos",
    "🔬 Investigação Estatística",
    "🤖 Assistente IA (Function Calling)",
])


# ─────────────────────────────────────────────────────────────────────────────
# ABA 1: TELEMETRIA ATUAL (RF04, RF05, RF17, RF18)
# ─────────────────────────────────────────────────────────────────────────────

with tab_atual:
    st.subheader(f"Última Leitura de Sensores: {maquina_selecionada}")

    try:
        dados_latest = obter_ultima_leitura(
            servidor=servidor_input,
            maquina=maquina_selecionada,
            timeout=TIMEOUT_PADRAO,
            usar_fallback_se_offline=True,
        )

        ts_leitura = dados_latest.get("timestamp", "Desconhecido")
        is_simulado = dados_latest.get("simulado", False)

        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.caption(f"🕒 **Horário do Registro:** `{ts_leitura}`")
        with col_header2:
            if is_simulado:
                st.markdown("<span class='tool-pill' style='background:#f59e0b;'>⚠️ Dado Didático Simulado</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='tool-pill' style='background:#10b981;'>🟢 Telemetria Real AI DataLab</span>", unsafe_allow_html=True)

        medicoes = dados_latest.get("medicoes", {})

        if medicoes:
            # Organiza os cards de métricas em colunas dinâmicas (RF04, RF05)
            cols = st.columns(len(medicoes))
            for i, (chave, item) in enumerate(medicoes.items()):
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-title">{item['nome']}</div>
                            <div class="metric-value">{item['valor']}<span class="metric-unit">{item['unidade']}</span></div>
                            <div style="color: #64748b; font-size: 0.8rem;">Grandeza: {item['grandeza']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("Nenhuma variável de medição retornada na última leitura.")

        with st.expander("🔍 Inspecionar Payload JSON Bruto da API"):
            st.json(dados_latest)

    except APIClientError as err:
        st.error(f"Erro de comunicação com a API (RF18): {err}")
    except ValueError as err:
        st.error(f"Erro de validação (RF17): {err}")


# ─────────────────────────────────────────────────────────────────────────────
# ABA 2: HISTÓRICO & GRÁFICOS (RF07, RF08, RF09)
# ─────────────────────────────────────────────────────────────────────────────

with tab_historico:
    st.subheader("Série Histórica de Telemetria")

    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        # RF07: Quantidade de registros a consultar
        limite_hist = st.select_slider(
            "Quantidade de Registros (Limit):",
            options=[20, 50, 100, 150, 200],
            value=50,
            help="Parâmetro 'limit' enviado na requisição HTTP GET à API.",
        )

    df_hist = obter_historico(
        servidor=servidor_input,
        maquina=maquina_selecionada,
        limit=limite_hist,
        timeout=TIMEOUT_PADRAO,
        usar_fallback_se_offline=True,
    )

    if df_hist.empty:
        st.warning("Histórico não disponível para a máquina e limite selecionados.")
    else:
        variaveis_disponiveis = [
            c for c in df_hist.columns
            if c not in ("timestamp", "machine_id") and pd.api.types.is_numeric_dtype(df_hist[c])
        ]

        if not variaveis_disponiveis:
            st.warning("Nenhuma variável numérica disponível no histórico para visualização.")
        else:
            with col_ctrl2:
                # RF09: Seleção da variável para investigação gráfica
                var_grafico = st.selectbox(
                    "Variável para Visualização Gráfica:",
                    options=variaveis_disponiveis,
                    index=0,
                )

            if var_grafico and var_grafico in df_hist.columns:
                meta_var = METADADOS_VARIAVEIS.get(maquina_selecionada, {}).get(var_grafico, {})
                unidade_var = meta_var.get("unidade", "")
                nome_var = meta_var.get("nome_exibicao", var_grafico)

                st.markdown(f"#### Evolução Temporal: **{nome_var}** ({unidade_var})")

                # Gráfico interativo com marcação temporal seguro (RF08)
                colunas_plot = [c for c in ["timestamp", var_grafico] if c in df_hist.columns]
                if "timestamp" in colunas_plot and len(colunas_plot) == 2:
                    chart_data = df_hist[colunas_plot].set_index("timestamp")
                    st.line_chart(chart_data, color="#38bdf8")
                else:
                    st.line_chart(df_hist[[var_grafico]], color="#38bdf8")

                # Tabela com histórico completo (RF08)
                with st.expander(f"📋 Ver Tabela de Dados Históricos ({len(df_hist)} registros)"):
                    st.dataframe(df_hist, use_container_width=True)
                    csv_data = df_hist.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Baixar Dados em CSV",
                        data=csv_data,
                        file_name=f"historico_{maquina_selecionada}_{var_grafico}.csv",
                        mime="text/csv",
                    )


# ─────────────────────────────────────────────────────────────────────────────
# ABA 3: INVESTIGAÇÃO ESTATÍSTICA (DESAFIOS A a F)
# ─────────────────────────────────────────────────────────────────────────────

with tab_analise:
    st.subheader("Motor de Análise Estatística Industrial")
    st.caption("Cálculos matemáticos puros para fundamentar intervenções de manutenção.")

    variaveis_analise = (
        [c for c in df_hist.columns if c not in ("timestamp", "machine_id") and pd.api.types.is_numeric_dtype(df_hist[c])]
        if not df_hist.empty
        else []
    )

    if df_hist.empty or not variaveis_analise:
        st.warning("Carregue o histórico com variáveis numéricas válidas para habilitar as ferramentas analíticas.")
    else:
        var_analise = st.selectbox(
            "Selecione a Grandeza para Diagnóstico:",
            options=variaveis_analise,
            key="sb_var_analise",
        )

        meta_analise = METADADOS_VARIAVEIS.get(maquina_selecionada, {}).get(var_analise, {})
        unidade_analise = meta_analise.get("unidade", "")
        serie_analise = df_hist[var_analise].dropna()

        subtab_a, subtab_b, subtab_c, subtab_d, subtab_e, subtab_f = st.tabs([
            "Desafio A: Comportamento Habitual",
            "Desafio B: Regularidade & Dispersão",
            "Desafio C: Registros Incomuns (IQR)",
            "Desafio D: Mudança Temporal",
            "Desafio E: Comparação de Máquinas",
            "Desafio F: Limites & Confiabilidade",
        ])

        # ---------------------------------------------------------------------
        # DESAFIO A: COMPORTAMENTO HABITUAL (RF10)
        # ---------------------------------------------------------------------
        with subtab_a:
            st.markdown("### 🎯 Desafio A — Comportamento Habitual")
            st.markdown(
                "Avalia qual medida central representa com fidelidade o processo operacional."
            )
            res_a = calcular_comportamento_habitual(serie_analise)

            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            col_a1.metric("Média Aritmética", f"{res_a['media']} {unidade_analise}")
            col_a2.metric("Mediana (P50)", f"{res_a['mediana']} {unidade_analise}")
            col_a3.metric("Amplitude Interquartil (IQR)", f"{res_a['iqr']} {unidade_analise}")
            col_a4.metric("Desvio Absoluto Mediano (MAD)", f"{res_a['mad']} {unidade_analise}")

            st.info(f"**Interpretação Estatística:** {res_a['interpretacao']}")

        # ---------------------------------------------------------------------
        # DESAFIO B: REGULARIDADE & OSCILAÇÃO (RF11)
        # ---------------------------------------------------------------------
        with subtab_b:
            st.markdown("### 🌊 Desafio B — Regularidade & Estabilidade Operacional")
            st.markdown("Determina se as medições permanecem estáveis ou oscilam com intensidade.")
            res_b = calcular_regularidade(serie_analise)

            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            col_b1.metric("Desvio Padrão", f"{res_b['desvio_padrao']} {unidade_analise}")
            col_b2.metric("Variância", f"{res_b['variancia']}")
            col_b3.metric("Amplitude Total (Max - Min)", f"{res_b['amplitude_total']} {unidade_analise}")
            col_b4.metric("Coeficiente de Variação (CV)", f"{res_b['coeficiente_variacao_pct']}%")

            st.success(f"**Diagnóstico de Regularidade:** {res_b['classificacao_regularidade']}")

        # ---------------------------------------------------------------------
        # DESAFIO C: REGISTROS INCOMUNS (OUTLIERS) (RF12)
        # ---------------------------------------------------------------------
        with subtab_c:
            st.markdown("### 🚨 Desafio C — Registros Incomuns (Critério IQR)")
            st.markdown(
                "Identifica medições que se afastam do comportamento típico usando o "
                "critério formal de **Tukey (1.5 × IQR)**."
            )
            res_c = detectar_registros_incomuns(df_hist, var_analise)

            col_c1, col_c2, col_c3 = st.columns(3)
            col_c1.metric("Limite Inferior de Tukey", f"{res_c['limite_inferior']} {unidade_analise}")
            col_c2.metric("Limite Superior de Tukey", f"{res_c['limite_superior']} {unidade_analise}")
            col_c3.metric(
                "Anomalias Detectadas",
                f"{res_c['quantidade_anomalias']} ({res_c['percentual_anomalias_pct']}%)",
            )

            anomalias_lista = res_c.get("registros_anomalos", [])
            if anomalias_lista:
                st.warning(
                    f"⚠️ Foram identificados **{len(anomalias_lista)} registros incomuns** "
                    f"que merecem averiguação técnica."
                )
                df_anom = pd.DataFrame(anomalias_lista)
                st.dataframe(df_anom, use_container_width=True)
            else:
                st.success("✅ Nenhuma leitura incomum encontrada fora dos limites de IQR no período.")

            st.caption(f"Critério adotado: {res_c['criterio_adotado']}. {res_c['ressalva_tecnica']}")

        # ---------------------------------------------------------------------
        # DESAFIO D: MUDANÇA TEMPORAL / TENDÊNCIA (RF13)
        # ---------------------------------------------------------------------
        with subtab_d:
            st.markdown("### 📈 Desafio D — Mudança ao Longo do Tempo (Tendência)")
            st.markdown(
                "Ajusta uma reta de regressão linear para separar oscilações transitórias "
                "de tendências contínuas de elevação ou queda."
            )
            res_d = calcular_tendencia_temporal(df_hist, var_analise)

            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.metric("Inclinação da Reta (Slope)", f"{res_d['inclinacao_slope']}")
            col_d2.metric("Coeficiente de Ajuste (R²)", f"{res_d['coeficiente_determinacao_r2']}")
            col_d3.metric("Variação Extremos", f"{res_d['variacao_extremos']} {unidade_analise}")

            st.info(f"**Análise de Tendência:** {res_d['direcao_tendencia']}")

            # Gráfico com série real e reta ajustada seguro contra KeyError
            colunas_d = [c for c in ["timestamp", var_analise] if c in df_hist.columns]
            df_plot_d = df_hist[colunas_d].copy()
            df_plot_d["Reta de Tendência (OLS)"] = res_d.get("valores_ajustados", [])
            if "timestamp" in df_plot_d.columns:
                st.line_chart(df_plot_d.set_index("timestamp"))
            else:
                st.line_chart(df_plot_d)

        # ---------------------------------------------------------------------
        # DESAFIO E: COMPARAÇÃO ENTRE MÁQUINAS (RF14)
        # ---------------------------------------------------------------------
        with subtab_e:
            st.markdown("### ⚖️ Desafio E — Comparação Segura entre Máquinas")
            st.markdown(
                "Permite comparar CENTRO-USINAGEM-01 e FURADEIRA-01 **estritamente quando as grandezas "
                "e unidades forem compatíveis**."
            )

            outra_maquina = "FURADEIRA-01" if maquina_selecionada == "CENTRO-USINAGEM-01" else "CENTRO-USINAGEM-01"
            var_comp = st.selectbox(
                "Selecione a Grandeza para Comparação:",
                options=["temperatura", "vibracao", "rotacao", "corrente", "pressao"],
                index=0,
            )

            df_outra = obter_historico(
                servidor=servidor_input,
                maquina=outra_maquina,
                limit=limite_hist,
                timeout=TIMEOUT_PADRAO,
                usar_fallback_se_offline=True,
            )

            try:
                res_e = comparar_maquinas(
                    df_a=df_hist,
                    df_b=df_outra,
                    maquina_a=maquina_selecionada,
                    maquina_b=outra_maquina,
                    variavel=var_comp,
                )

                st.success(
                    f"✅ **Compatibilidade Aprovada (RF14):** Ambas as máquinas monitoram '{var_comp}' em '{res_e['unidade']}'."
                )

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.markdown(f"**{res_e['maquina_a']['nome']}**")
                    st.write(f"- Média: **{res_e['maquina_a']['media']} {res_e['unidade']}**")
                    st.write(f"- Desvio Padrão: **{res_e['maquina_a']['desvio_padrao']}**")
                    st.write(f"- Faixa: [{res_e['maquina_a']['min']} a {res_e['maquina_a']['max']}]")

                with col_e2:
                    st.markdown(f"**{res_e['maquina_b']['nome']}**")
                    st.write(f"- Média: **{res_e['maquina_b']['media']} {res_e['unidade']}**")
                    st.write(f"- Desvio Padrão: **{res_e['maquina_b']['desvio_padrao']}**")
                    st.write(f"- Faixa: [{res_e['maquina_b']['min']} a {res_e['maquina_b']['max']}]")

                st.caption(f"Nota Técnica: {res_e['ressalva_operacional']}")

            except ValueError as err:
                st.error(f"⛔ {err}")

        # ---------------------------------------------------------------------
        # DESAFIO F: LIMITES DA INTERPRETAÇÃO & SUFICIÊNCIA (RF19, RF20)
        # ---------------------------------------------------------------------
        with subtab_f:
            st.markdown("### 🛡️ Desafio F — Limites de Interpretação & Confiabilidade")
            st.markdown(
                "Apresenta os metadados de amostragem e a declaração explícita de suficiência técnica."
            )

            dossie = gerar_relatorio_completo_variavel(df_hist, maquina_selecionada, var_analise)
            st.json(dossie["desafio_f_limites_e_responsabilidade"])
            st.warning(
                f"**Suficiência Amostral:** {dossie['suficiencia_amostral']} ({dossie['total_amostras']} amostras). "
                f"Intervalo coberto: {dossie['periodo_registros']['inicio']} até {dossie['periodo_registros']['fim']}."
            )


# ─────────────────────────────────────────────────────────────────────────────
# ABA 4: ASSISTENTE IA COM GEMINI & FUNCTION CALLING (RF15, RF16, RF18)
# ─────────────────────────────────────────────────────────────────────────────

with tab_assistente:
    st.subheader("💬 Assistente Especialista com Gemini e Function Calling")
    st.caption(
        "Faça perguntas técnicas em linguagem natural. O Gemini consulta e executa as funções Python "
        "reais sem calcular números mentalmente nem alucinar dados."
    )

    # Exibição de sugestões rápidas de perguntas (Seção 10 do documento)
    st.markdown("**Perguntas sugeridas:**")
    col_p1, col_p2, col_p3 = st.columns(3)
    p_clicada = None
    if col_p1.button("Quais as últimas leituras do Centro de Usinagem?"):
        p_clicada = "Quais as últimas leituras do Centro de Usinagem CNC?"
    if col_p2.button("Como a temperatura da furadeira se comportou?"):
        p_clicada = "Como a temperatura da furadeira industrial se comportou nos últimos registros?"
    if col_p3.button("Qual máquina vai falhar primeiro?"):
        p_clicada = "Qual das máquinas vai falhar primeiro? O que é possível concluir?"

    # Container de mensagens anteriores
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tools"):
                with st.expander(f"⚙️ Ferramentas Python Acionadas ({len(msg['tools'])})"):
                    for t in msg["tools"]:
                        st.markdown(f"- `<code style='color:#38bdf8;'>{t['ferramenta']}</code>` com argumentos `{t.get('argumentos', {})}`", unsafe_allow_html=True)

    # Entrada de texto do usuário (RF15)
    prompt_usuario = st.chat_input("Digite sua pergunta sobre a célula de usinagem...")
    if p_clicada:
        prompt_usuario = p_clicada

    if prompt_usuario:
        st.session_state.chat_messages.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Consultando ferramentas e analisando dados..."):
                chave_final = gemini_key_input or gemini_key_env
                assistente = AssistenteGemini(api_key=chave_final, modelo=modelo_selecionado)
                resultado = assistente.enviar_mensagem(prompt_usuario)

                st.markdown(resultado["resposta"])
                if resultado.get("ferramentas_chamadas"):
                    with st.expander(f"⚙️ Ferramentas Python Acionadas ({len(resultado['ferramentas_chamadas'])})"):
                        for t in resultado["ferramentas_chamadas"]:
                            st.markdown(f"- `<code style='color:#38bdf8;'>{t['ferramenta']}</code>` com argumentos `{t.get('argumentos', {})}`", unsafe_allow_html=True)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": resultado["resposta"],
            "tools": resultado.get("ferramentas_chamadas", []),
        })
