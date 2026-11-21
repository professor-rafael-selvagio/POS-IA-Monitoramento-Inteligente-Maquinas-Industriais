# Análise Estatística de Dados Industriais da Célula de Usinagem
**Documento Técnico de Justificativa Metodológica e Governança de Dados**  
*Célula de Usinagem: CENTRO-USINAGEM-01 e FURADEIRA-01*

---

## 1. Dicionário de Dados e Telemetria

A Célula de Usinagem monitorada é composta por dois equipamentos com características mecânicas e sensores dedicados. A tabela abaixo documenta as variáveis disponibilizadas pelo AI DataLab:

### 1.1. Centro de Usinagem CNC (`CENTRO-USINAGEM-01`)

| Identificador do Campo | Nome de Exibição | Grandeza Física | Unidade | Faixa Típica Operacional | Descrição do Ponto de Sensoriamento |
|---|---|---|:---:|:---:|---|
| `temperatura` | Temperatura Mancal Spindle | Térmica | °C | 40.0 a 70.0 | Termorresistência PT100 acoplada ao alojamento do mancal dianteiro do eixo-árvore de alta rotação. |
| `vibracao` | Vibração Eixo Principal | Mecânica / Dinâmica | mm/s | 0.8 a 3.5 | Acelerômetro piezoelétrico medindo velocidade RMS de vibração global na carcaça do cabeçote. |
| `rotacao` | Rotação Spindle | Cinemática | RPM | 2000 a 6000 | Tacômetro óptico/encoder incremental medindo a velocidade angular de rotação da ferramenta. |
| `corrente` | Corrente Motor Principal | Elétrica | A | 10.0 a 24.0 | Transformador de corrente (TC) no inversor de frequência alimentando o motor de corte do spindle. |

### 1.2. Furadeira Industrial (`FURADEIRA-01`)

| Identificador do Campo | Nome de Exibição | Grandeza Física | Unidade | Faixa Típica Operacional | Descrição do Ponto de Sensoriamento |
|---|---|---|:---:|:---:|---|
| `temperatura` | Temperatura Motor | Térmica | °C | 35.0 a 55.0 | Sensor termopar tipo K instalado nas aletas da carcaça do motor elétrico trifásico de acionamento. |
| `vibracao` | Vibração Cabeçote | Mecânica / Dinâmica | mm/s | 0.5 a 2.5 | Transdutor de vibração uniaxial no cabeçote de furação vertical. |
| `rotacao` | Rotação Eixo Árvore | Cinemática | RPM | 600 a 2000 | Sensor indutivo de rotação monitorando o eixo de furação. |
| `pressao` | Pressão de Avanço | Fluídica / Hidráulica | bar | 4.5 a 7.5 | Transmissor de pressão piezorresistivo no circuito hidráulico do cilindro de avanço da broca. |

---

## 2. Metodologia Estatística e Justificativas Técnicas (Desafios A a F)

### Desafio A — Comportamento Habitual (RF10)
- **Problema Técnico:** Como determinar um valor central que represente realisticamente o regime operacional sem sofrer distorções causadas por picos transitórios de corte ou folgas momentâneas?
- **Métodos Escolhidos:**
  1. **Média Aritmética ($\mu$):**
     $$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$
     *Utilidade:* Representa o centro de gravidade matemático da grandeza no período.
  2. **Mediana ($\text{Md}$ ou $Q_2$):**
     Ponto que divide exatamente 50% dos dados superiores e inferiores.  
     *Justificativa Industrial:* A mediana é um estimador não-paramétrico de alta robustez (breakdown point de 50%). Em operações com trocas bruscas de carga ou furações pesadas, a média pode ser puxada artificialmente para cima, enquanto a mediana preserva o valor de regime estável.
  3. **Coeficiente de Assimetria de Pearson ($S$):**
     $$S = \frac{\mu - \text{Md}}{\sigma}$$
     *Interpretação:* Se $|S| < 0.15$, o processo opera simetricamente em torno da média. Se $S > 0.15$, medições esporádicas de topo estão elevando a média, recomendando a adoção da mediana como parâmetro de referência de engenharia.
  4. **Desvio Absoluto Mediano ($\text{MAD}$):**
     $$\text{MAD} = \text{mediana}(|x_i - \text{Md}|)$$
     Métrica robusta de dispersão complementar ao IQR.

---

### Desafio B — Regularidade e Oscilação das Medições (RF11)
- **Problema Técnico:** Como quantificar se o comportamento da máquina é estável e previsível ou se apresenta oscilações intensas e erráticas?
- **Métodos Escolhidos:**
  1. **Desvio Padrão Amostral ($\sigma$):**
     $$\sigma = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(x_i - \mu)^2}$$
     Mede a variabilidade absoluta em torno da média com a mesma unidade física da grandeza.
  2. **Amplitude Total ($R$):**
     $$R = x_{\max} - x_{\min}$$
     Informa a faixa total percorrida pelo sinal no período observado.
  3. **Coeficiente de Variação ($\text{CV}\%$):**
     $$\text{CV} = \left(\frac{\sigma}{|\mu|}\right) \times 100\%$$
     *Justificativa Crítica de Engenharia:* O desvio padrão não permite comparar estabilidade de grandezas distintas ou escalas diferentes (por exemplo: um desvio de 40 RPM em 4000 RPM representa apenas 1% de variação relativa, enquanto um desvio de 1.0 mm/s em 2.0 mm/s de vibração representa 50% de instabilidade!). A classificação adotada categoriza:
     - $\text{CV} < 5\%$: **Alta Estabilidade** (regime permanente controlado).
     - $5\% \le \text{CV} < 15\%$: **Estabilidade Moderada** (variações operacionais aceitáveis de corte).
     - $\text{CV} \ge 15\%$: **Alta Dispersão / Oscilação Intensa** (comportamento errático que requer investigação).

---

### Desafio C — Detecção de Registros Incomuns / Outliers (RF12)
- **Problema Técnico:** Como evidenciar registros pontuais que se afastam fortemente do padrão geral sem disparar falsos alarmes de quebra da máquina?
- **Método Escolhido: Critério de Tukey (Intervalo Interquartil - IQR)**
  - $Q_1$: 25º percentil (primeiro quartil).
  - $Q_3$: 75º percentil (terceiro quartil).
  - $\text{IQR} = Q_3 - Q_1$ (Amplitude Interquartil).
  - **Limite Inferior:** $L_{\inf} = Q_1 - 1.5 \times \text{IQR}$
  - **Limite Superior:** $L_{\sup} = Q_3 + 1.5 \times \text{IQR}$
- **Justificativa da Escolha do IQR em detrimento do Z-Score:**
  O Z-score clássico ($\mu \pm 3\sigma$) assume distribuição normal teórica e sofre do fenômeno de *mascaramento*, pois o próprio ponto anômalo severamente discrepante inflaciona a média e o desvio padrão, alargando o limite de detecção. O método de Tukey fundamenta-se em quartis de postos ordenados, sendo impermeável a essa distorção.
- **Ressalva de Manutenção:** Toda medição que ultrapassar os limites é classificada como *"Registro Incomum para Averiguação Técnica"*, jamais como *"Defeito Comprovado"*.

---

### Desafio D — Mudança Temporal e Tendência (RF13)
- **Problema Técnico:** Como distinguir uma oscilação momentânea decorrente de um choque de usinagem de uma elevação térmica gradual e perigosa por desgaste de mancal?
- **Método Escolhido: Regressão Linear Simples por Mínimos Quadrados Ordinários (OLS)**
  Ajuste do modelo $y(t) = a \cdot t + b$, onde $t \in [0, 1, \dots, N-1]$:
  $$a = \frac{N \sum (t \cdot y) - \sum t \sum y}{N \sum t^2 - (\sum t)^2}$$
  $$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \mu)^2}$$
- **Critério de Classificação da Tendência:**
  - $a > 0.001 \cdot |\mu|$ e $R^2 \ge 0.20$: **Tendência de Elevação** (ex.: aquecimento progressivo do spindle).
  - $a < -0.001 \cdot |\mu|$ e $R^2 \ge 0.20$: **Tendência de Redução**.
  - Caso contrário: **Estabilidade Temporal** (o processo oscila estacionariamente em torno da linha de base).

---

### Desafio E — Comparação Segura entre Máquinas (RF14)
- **Problema Técnico:** Sob quais condições é metodologicamente válido comparar o Centro de Usinagem e a Furadeira?
- **Regras Estritas de Consistência:**
  1. **Compatibilidade Dimensional Obrigatória:** Apenas grandezas físicas e unidades idênticas podem ser confrontadas:
     - `temperatura` (°C) $\Leftrightarrow$ `temperatura` (°C) $\rightarrow$ **Permitida**.
     - `vibracao` (mm/s) $\Leftrightarrow$ `vibracao` (mm/s) $\rightarrow$ **Permitida**.
     - `rotacao` (RPM) $\Leftrightarrow$ `rotacao` (RPM) $\rightarrow$ **Permitida com ressalva de escala**.
     - `corrente` (A) vs `pressao` (bar) $\rightarrow$ **Bloqueio Total com Exceção Explícita**.
  2. **Contextualização Operacional:** Mesmo na temperatura (°C), a aplicação adverte o operador de que o Centro de Usinagem CNC possui potência superior e opera em ciclos contínuos de desbaste, enquanto a Furadeira atua em regime intermitente com cursos definidos de furação.

---

### Desafio F — Limites de Interpretação e Confiabilidade (RF19, RF20)
- **Governança dos Dados e Responsabilidade:**
  1. **Natureza Didática:** Todos os dados processados derivam de simulação matemática da plataforma AI DataLab.
  2. **Suficiência Amostral:** Conjuntos com menos de 30 amostras recebem alerta de "Suficiência Amostral Baixa", prevenindo generalizações precipitadas.
  3. **Princípio da Prevenção:** A aplicação orienta a equipe técnica a validar anomalias com termografia presencial, análise de óleo ou caneta de vibração calibrada antes de emitir qualquer ordem de parada corretiva de linha.
