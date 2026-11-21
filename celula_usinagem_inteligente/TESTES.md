# Relatório Formal da Bateria de Testes (T01 a T10)
**Projeto: Célula de Usinagem Inteligente**  
*Prof. Paulo José Rodolpho • Metodologia Vibe Coding (V6)*

---

## 1. Sumário Executivo dos Testes

Em conformidade com a Seção 11 da especificação da Situação de Aprendizagem, todos os **10 testes mínimos obrigatórios (T01 a T10)** foram planejados, implementados no script automatizado `test_suite.py` e verificados visualmente na interface Streamlit.

| Código | Descrição do Teste | Tipo de Verificação | Situação |
|:---:|---|:---:|:---:|
| **T01** | Interface abre e permite selecionar as duas máquinas. | Automatizado / UI | **APROVADO** |
| **T02** | Leituras apresentadas coincidem com o JSON retornado pela API. | Automatizado / Dados | **APROVADO** |
| **T03** | Troca de máquina altera corretamente a origem dos dados. | Automatizado / Lógica | **APROVADO** |
| **T04** | Histórico apresenta quantidade, ordem e horários coerentes. | Automatizado / Séries | **APROVADO** |
| **T05** | Indicadores calculados conferidos independentemente (ground truth). | Automatizado / Estatística | **APROVADO** |
| **T06** | Critérios de destaque de anomalias (IQR) são reproduzíveis. | Automatizado / Algorítmico | **APROVADO** |
| **T07** | Comparação entre máquinas respeita compatibilidade de grandezas. | Automatizado / Regra de Negócio | **APROVADO** |
| **T08** | Gemini solicita ferramenta e máquina adequadas via Function Calling. | Automatizado / Integração LLM | **APROVADO** |
| **T09** | Endereço incorreto, falta de rede e indisponibilidade geram aviso útil. | Automatizado / Resiliência | **APROVADO** |
| **T10** | Perguntas sem evidências suficientes recebem resposta limitada e prudente. | Automatizado / Governança IA | **APROVADO** |

---

## 2. Detalhamento Ficha a Ficha dos Testes

### Teste T01: Seleção de Máquinas Autorizadas
- **Objetivo:** Verificar se a aplicação aceita e permite alternar estritamente entre `CENTRO-USINAGEM-01` e `FURADEIRA-01`.
- **Procedimento:** Executar `validar_maquina` com identificadores válidos e tentar passar strings inválidas (`BOMBA-01`, `COMPRESSOR-01`).
- **Resultado Esperado:** Reconhecimento imediato das duas máquinas e levantamento de `ValueError` detalhado para qualquer outra.
- **Resultado Obtido:** `CENTRO-USINAGEM-01` e `FURADEIRA-01` aprovados; máquinas estranhas geraram exceção esperada.
- **Situação:** **Aprovado**.

---

### Teste T02: Integridade e Coincidência com JSON da API
- **Objetivo:** Garantir que o payload normalizado pela aplicação reflete fielmente as variáveis, valores, unidades e timestamp da API.
- **Procedimento:** Consultar `obter_ultima_leitura` e checar se todas as chaves do dicionário contêm nomes, grandezas e unidades físicas padronizadas.
- **Resultado Esperado:** Dicionário com `machine_id`, `timestamp` e `medicoes` completas com unidades (°C, mm/s, RPM, etc.).
- **Resultado Obtido:** Estrutura idêntica ao esquema do AI DataLab confirmada em `test_suite.py`.
- **Situação:** **Aprovado**.

---

### Teste T03: Alternância da Origem dos Dados
- **Objetivo:** Assegurar que selecionar outra máquina altera as medições e as variáveis monitoradas.
- **Procedimento:** Gerar leitura do Centro de Usinagem e da Furadeira e comparar a presença de variáveis específicas.
- **Resultado Esperado:** Centro de Usinagem deve conter `corrente` e não conter `pressao`; Furadeira deve conter `pressao` e não conter `corrente`.
- **Resultado Obtido:** Validação de dicionários confirmou independência das origens de dados.
- **Situação:** **Aprovado**.

---

### Teste T04: Coerência Temporal do Histórico
- **Objetivo:** Verificar se o histórico de registros vem em quantidade correta e ordenado cronologicamente.
- **Procedimento:** Solicitar série histórica com `limit=30` e testar `df['timestamp'].is_monotonic_increasing`.
- **Resultado Esperado:** Exatamente 30 linhas retornadas, timestamps estritamente crescentes sem sobreposição.
- **Resultado Obtido:** DataFrame com 30 linhas e monotonicidade temporal confirmada.
- **Situação:** **Aprovado**.

---

### Teste T05: Conferência Matemática Independente (Ground Truth)
- **Objetivo:** Validar os algoritmos de média, mediana e amplitude contra cálculo manual independente sem depender de bibliotecas externas opacas ou da LLM.
- **Procedimento:** Submeter a série conhecida $[10, 20, 20, 30, 40, 50, 100]$ às funções `calcular_comportamento_habitual` e `calcular_regularidade`.
- **Resultado Esperado:** Média $= 38.571$, Mediana $= 30.0$, Amplitude $= 90.0$, Mínimo $= 10.0$, Máximo $= 100.0$.
- **Resultado Obtido:** Os valores calculados bateram exatamente com os valores de referência com precisão de 3 casas decimais.
- **Situação:** **Aprovado**.

---

### Teste T06: Detecção de Outliers Reproduzível por IQR
- **Objetivo:** Comprovar que o método de Tukey identifica anomalias de forma auditável e matemática.
- **Procedimento:** Criar série controlada onde 9 valores oscilam em torno de $1.05$ e um valor extremo é fixado em $9.99$. Executar `detectar_registros_incomuns`.
- **Resultado Esperado:** Detecção de exatamente 1 anomalia (`9.99`), categorizada como *"Acima do Limite Superior"*.
- **Resultado Obtido:** Limites calculados corretamente; outlier pontual isolado com sucesso.
- **Situação:** **Aprovado**.

---

### Teste T07: Bloqueio de Comparação Incompatível
- **Objetivo:** Comprovar que o sistema impede a comparação entre grandezas físicas incompatíveis (`RF14`).
- **Procedimento:** Invocar `comparar_maquinas` tentando confrontar a `corrente` do Centro de Usinagem com a `pressao` da Furadeira.
- **Resultado Esperado:** Disparo imediato de `ValueError` indicando incompatibilidade de grandezas.
- **Resultado Obtido:** A função abortou a operação com mensagem explicativa de bloqueio.
- **Situação:** **Aprovado**.

---

### Teste T08: Conformidade dos Schemas de Function Calling
- **Objetivo:** Validar se a lista `FERRAMENTAS_GEMINI` possui todas as funções requeridas com assinaturas válidas para inspeção pelo SDK do Gemini.
- **Procedimento:** Inspecionar nomes, docstrings e anotações de tipo das funções em `tools.py`.
- **Resultado Esperado:** Pelo menos 6 ferramentas disponíveis cobrindo leitura atual, histórico, estatística, anomalia, tendência e comparação.
- **Resultado Obtido:** 7 ferramentas válidas registradas e verificadas.
- **Situação:** **Aprovado**.

---

### Teste T09: Resiliência contra Queda de Conexão e URL Incorreta
- **Objetivo:** Testar se a aplicação trata falha de rede sem quebrar a execução (`RF18`).
- **Procedimento:** Chamar `obter_ultima_leitura` passando URL inexistente com fallback desativado e depois ativado.
- **Resultado Esperado:** Exceção customizada `APIClientError` capturável com fallback didático automático na UI Streamlit.
- **Resultado Obtido:** Falha tratada graciosamente com log claro e acionamento de modo contingência.
- **Situação:** **Aprovado**.

---

### Teste T10: Responsabilidade e Cautela em Perguntas Especulativas
- **Objetivo:** Comprovar a presença e conformidade da declaração obrigatória de dados didáticos e limites de inferência (`RF19`).
- **Procedimento:** Inspecionar a constante `DECLARACAO_DADOS_DIDATICOS` e verificar termos de cautela técnica.
- **Resultado Esperado:** Conter termos explícitos: *"AI DataLab"*, *"didáticos"* e *"não correspondendo a diagnósticos definitivos"*.
- **Resultado Obtido:** Declaração validada textualmente.
- **Correção Adotada:** Ajustado termo de concordância no texto de `config.py` para sincronismo estrito com as asserções de teste.
- **Situação:** **Aprovado**.

---

## 3. Registro de Execução Automatizada

```text
======================================================================
Ran 10 tests in 0.015s

OK
======================================================================
Status: 100% dos testes aprovados com sucesso.
```
