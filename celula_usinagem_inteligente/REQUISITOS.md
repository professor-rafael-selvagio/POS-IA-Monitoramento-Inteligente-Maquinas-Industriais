# Matriz de Requisitos Funcionais (RF01 a RF20)
**Projeto: Monitoramento e Análise Inteligente de uma Célula de Usinagem**  
*Célula de Usinagem: CENTRO-USINAGEM-01 e FURADEIRA-01*

---

## 1. Visão Geral da Rastreabilidade

Esta matriz documenta o status de atendimento e a localização no código-fonte de todos os **20 Requisitos Funcionais (RF01 a RF20)** estabelecidos na especificação oficial da Situação de Aprendizagem (Aula 04).

---

## 2. Matriz de Atendimento aos Requisitos Funcionais

| Código | Descrição Oficial do Requisito | Módulo / Arquivo Responsável | Mecanismo de Implementação | Status |
|:---:|---|---|---|:---:|
| **RF01** | Disponibilizar interface web com Streamlit. | `app.py` | Configuração de layout amplo via `st.set_page_config`, abas temáticas e estilização CSS. | **Implementado** |
| **RF02** | Permitir configurar o endereço do servidor AI DataLab. | `app.py`, `config.py` | Campo `st.text_input` na barra lateral com persistência de endereço HTTP e valor padrão configurável via ambiente. | **Implementado** |
| **RF03** | Permitir selecionar `CENTRO-USINAGEM-01` ou `FURADEIRA-01`. | `app.py`, `config.py` | Seletor `st.selectbox` restrito estritamente à tupla `MAQUINAS_VALIDAS`. | **Implementado** |
| **RF04** | Consultar as leituras mais recentes da máquina selecionada. | `api_client.py`, `app.py` | Função `obter_ultima_leitura` consumindo rota `/api/v1/machines/<maquina>/latest`. | **Implementado** |
| **RF05** | Exibir nomes das variáveis, valores, unidades e horários. | `app.py`, `config.py` | Cards métricos (`metric-card`) com valor formatado, unidades físicas (°C, mm/s, RPM, A, bar) e timestamp da medição. | **Implementado** |
| **RF06** | Permitir atualizar os dados mediante ação do usuário. | `app.py` | Botão `st.button("🔄 Atualizar Dados Agora")` que recarrega os dados e dispara `st.rerun()`. | **Implementado** |
| **RF07** | Consultar registros históricos conforme parâmetros da API. | `api_client.py` | Função `obter_historico` consumindo `/api/v1/machines/<maquina>/readings` com parâmetro `limit` ajustável. | **Implementado** |
| **RF08** | Apresentar histórico em tabela e em representações gráficas adequadas. | `app.py` | Gráfico temporal de linha (`st.line_chart`), tabela interativa (`st.dataframe`) e botão de download em CSV. | **Implementado** |
| **RF09** | Permitir selecionar variável e conjunto de registros para investigação. | `app.py` | Controles de interface com controle deslizante de registros (`limit` de 20 a 200) e menu de seleção de grandezas monitoradas. | **Implementado** |
| **RF10** | Produzir informações que representem o comportamento habitual dos registros (Desafio A). | `analise.py` | Função `calcular_comportamento_habitual` gerando média, mediana, IQR, MAD e coeficiente de assimetria de Pearson. | **Implementado** |
| **RF11** | Permitir avaliar a regularidade e a intensidade das oscilações (Desafio B). | `analise.py` | Função `calcular_regularidade` calculando desvio padrão, variância, amplitude total e coeficiente de variação (CV%). | **Implementado** |
| **RF12** | Destacar registros que mereçam investigação, com critério explícito (Desafio C). | `analise.py`, `app.py` | Função `detectar_registros_incomuns` utilizando o método de Tukey (IQR com fator 1.5), com listagem e destaque dos pontos anômalos. | **Implementado** |
| **RF13** | Apoiar a identificação de mudanças ao longo do tempo (Desafio D). | `analise.py`, `app.py` | Função `calcular_tendencia_temporal` aplicando regressão linear simples (OLS), calculando a inclinação (slope), R² e plotando a reta de tendência. | **Implementado** |
| **RF14** | Permitir comparação somente quando variáveis e unidades forem compatíveis (Desafio E). | `analise.py`, `app.py` | Função `comparar_maquinas` validando fisicamente a compatibilidade da grandeza (temperatura vs. temperatura; vibração vs. vibração) e bloqueando grandezas incompatíveis. | **Implementado** |
| **RF15** | Disponibilizar campo de perguntas em linguagem natural. | `app.py` | Interface de chat interativa com `st.chat_input` e histórico conversacional via `st.chat_message`. | **Implementado** |
| **RF16** | Integrar o Gemini com Function Calling para consultar dados e análises. | `assistente.py`, `tools.py` | Integração com o Google GenAI SDK utilizando lista de ferramentas estruturadas com docstrings e type-hints, exibindo na UI as ferramentas executadas. | **Implementado** |
| **RF17** | Validar os identificadores de máquina aceitos pelas funções. | `config.py`, `api_client.py` | Função `validar_maquina` que levanta `ValueError` imediato caso qualquer identificador fora de `CENTRO-USINAGEM-01` e `FURADEIRA-01` seja passado. | **Implementado** |
| **RF18** | Tratar falhas de rede, ausência de dados e indisponibilidade do Gemini. | `api_client.py`, `assistente.py` | Tratamento de exceções `RequestException`, timeouts, ausência de chave de API e contingência didática graciosa sem quebra do app. | **Implementado** |
| **RF19** | Informar limites de interpretação e insuficiência de evidências (Desafio F). | `config.py`, `analise.py`, `app.py` | Inclusão de declaração mandatória sobre dados simulados/didáticos do AI DataLab e alertas de suficiência amostral antes de intervenções. | **Implementado** |
| **RF20** | Apresentar descrições dos métodos adotados e seus resultados. | `analise.py`, `ANALISE_DADOS.md` | Detalhamento matemático de todas as fórmulas adotadas e apresentação textual das interpretações diretamente ao operador. | **Implementado** |

---

## 3. Matriz de Vinculação dos Desafios Investigativos da Manutenção

| Desafio | Demanda da Manutenção | Requisitos Funcionais Associados | Método Matemático Implementado |
|---|---|---|---|
| **Desafio A** | Comportamento Habitual | `RF10`, `RF16`, `RF20` | Média, Mediana, IQR, Desvio Absoluto Mediano (MAD), Assimetria de Pearson |
| **Desafio B** | Regularidade & Oscilação | `RF11`, `RF16`, `RF20` | Desvio Padrão amostral, Variância, Amplitude (Max - Min), Coeficiente de Variação (CV%) |
| **Desafio C** | Registros Incomuns | `RF12`, `RF16`, `RF20` | Intervalo Interquartil de Tukey: $[Q_1 - 1.5 \times \text{IQR}, Q_3 + 1.5 \times \text{IQR}]$ |
| **Desafio D** | Mudança Temporal | `RF13`, `RF16`, `RF20` | Regressão Linear Simples por Mínimos Quadrados ($y = ax + b$), Coeficiente $R^2$ |
| **Desafio E** | Comparação entre Máquinas | `RF14`, `RF16`, `RF17` | Validação de compatibilidade física de grandezas e unidades; comparação pareada |
| **Desafio F** | Limites e Cautela | `RF18`, `RF19`, `RF20` | Declaração de ambiente didático, índice de suficiência amostral ($N \ge 30$) e postura não alarmista |
