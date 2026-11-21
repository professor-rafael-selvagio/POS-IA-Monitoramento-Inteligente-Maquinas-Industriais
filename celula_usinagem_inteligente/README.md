# Célula de Usinagem Inteligente: Monitoramento & Análise Preditiva Industrial
**Pós-Graduação em Inteligência Artificial • Módulo 3: Linguagem de Programação (Aula 04)**  
*Prof. Paulo José Rodolpho*

---

## 1. Visão Geral do Projeto

A **Célula de Usinagem Inteligente** é uma aplicação web de telemetria industrial e apoio à tomada de decisão para equipes de manutenção mecânica. O sistema integra a telemetria do **AI DataLab** com um motor estatístico determinístico em Python e um assistente inteligente baseado no **Google Gemini** acionado por **Function Calling** nativo.

O escopo operacional monitora exclusivamente duas máquinas industriais da célula:
1. **CENTRO-USINAGEM-01**: Centro de Usinagem CNC (variáveis: temperatura do mancal, vibração do eixo principal, rotação do spindle e corrente do motor).
2. **FURADEIRA-01**: Furadeira Industrial (variáveis: temperatura do motor, vibração do cabeçote, rotação do eixo árvore e pressão hidráulica de avanço).

---

## 2. Diferenciais Arquiteturais

- 🔒 **Zero Alucinação Numérica:** O modelo de linguagem (Gemini) **não calcula métricas de cabeça** nem inventa medições. Toda informação quantitativa é obrigatoriamente obtida via **Function Calling** chamando funções puras em Python.
- 📐 **Motor Estatístico Robusto (Desafios A a F):** Cálculos de tendência (regressão linear OLS), detecção de outliers não-paramétricos (método de Tukey / IQR 1.5), regularidade operacional (CV%) e comparação validada de grandezas.
- 🛡️ **Postura Técnica Cautelosa:** O sistema segue rigorosamente o princípio da engenharia de manutenção: dados incomuns representam evidências para averiguação presencial, nunca diagnósticos alarmistas automáticos de quebra.
- 🔄 **Resiliência e Continuidade Operacional:** Tratamento integral para quedas de conexão, URLs incorretas e modo contingência didática integrado para demonstração fora da rede do laboratório.

---

## 3. Estrutura do Repositório

```text
celula_usinagem_inteligente/
├── app.py              # Aplicação Web Streamlit com 4 abas integradas
├── config.py           # Configuração centralizada, metadados e validação estrita
├── api_client.py       # Cliente HTTP com endpoints /latest e /readings e resiliência
├── analise.py          # Motor estatístico puro (Desafios A a F / RF10 a RF14)
├── tools.py            # Ferramentas Python estruturadas para o Function Calling do Gemini
├── assistente.py       # Integração com o Google GenAI SDK e System Instruction
├── test_suite.py       # Bateria formal automatizada dos testes T01 a T10
├── requirements.txt    # Dependências mínimas do projeto
├── README.md           # Guia de instalação, configuração e uso
├── REQUISITOS.md       # Matriz de rastreabilidade dos 20 Requisitos Funcionais (RF01 a RF20)
├── ANALISE_DADOS.md    # Dicionário de dados, justificativas estatísticas e limites
├── PROMPTS.md          # Catálogo de system prompt, prompts testados e saídas
├── TESTES.md           # Relatório formal da bateria de testes T01 a T10
└── ARQUITETURA.md      # Diagramas de blocos, componentes e fluxo de dados
```

---

## 4. Pré-Requisitos do Sistema

- **Python:** Versão 3.10 ou superior (testado e validado em Python 3.12).
- **Gerenciador de Pacotes:** `pip` atualizado.
- **Chave de API do Gemini:** Obtida no [Google AI Studio](https://aistudio.google.com/).
- **Conectividade:** Acesso à rede local do laboratório (`http://10.110.18.12:10999`) ou utilização do modo didático integrado.

---

## 5. Instalação e Execução Passo a Passo

### Passo 1: Clonar ou descompactar o projeto
Navegue até a pasta do projeto:
```bash
cd celula_usinagem_inteligente
```

### Passo 2: Criar e ativar um ambiente virtual (Recomendado)
```bash
# No macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# No Windows:
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instalar as dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Configurar a Chave do Gemini em Variável de Ambiente
> ⚠️ **IMPORTANTE:** Por diretriz estrita de segurança, nunca escreva sua chave nos arquivos de código ou documentação.

```bash
# No macOS/Linux:
export GEMINI_API_KEY="sua_chave_gemini_aqui"

# No Windows (PowerShell):
$env:GEMINI_API_KEY="sua_chave_gemini_aqui"

# No Windows (CMD):
set GEMINI_API_KEY=sua_chave_gemini_aqui
```
*Nota: Caso prefira, a chave também pode ser informada diretamente no campo de senha da barra lateral da aplicação web.*

### Passo 5: Executar a Aplicação Streamlit
```bash
streamlit run app.py
```
A interface será aberta automaticamente no seu navegador padrão no endereço `http://localhost:8501`.

---

## 6. Execução da Bateria de Testes (T01 a T10)

Para rodar a suíte de testes unitários automatizados cobrindo os testes `T01` a `T10`:
```bash
python3 test_suite.py
```
Todas as 10 verificações devem retornar status `OK`.

---

## 7. Navegação na Aplicação Web

A interface está organizada em 4 abas funcionais:
1. **📊 Telemetria Atual:** Exibe a última leitura pontual dos sensores da máquina selecionada, com valores formatados, grandezas, unidades e carimbo de data/hora (`RF04`, `RF05`).
2. **📈 Histórico & Gráficos:** Gráficos interativos com séries temporais e tabela de dados com exportação para CSV (`RF07`, `RF08`, `RF09`).
3. **🔬 Investigação Estatística:** Painel dedicado aos **Desafios A a F**, contendo comportamento habitual, estabilidade/dispersão, detecção de outliers pelo método IQR de Tukey, regressão linear com linha de tendência e comparação segura de máquinas.
4. **💬 Assistente IA (Function Calling):** Chat em linguagem natural integrado ao Gemini, exibindo em tempo real quais ferramentas Python foram acionadas para responder a cada pergunta técnica.
