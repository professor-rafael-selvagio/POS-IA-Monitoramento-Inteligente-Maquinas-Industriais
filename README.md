# Monitoramento e Análise Inteligente de uma Célula de Usinagem
**Pós-Graduação em Inteligência Artificial • Módulo 3: Linguagem de Programação (Aula 04)**  
*Prof. Paulo José Rodolpho*

[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Online-22c55e?style=for-the-badge&logo=github)](https://professor-rafael-selvagio.github.io/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/)
[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-Function_Calling-8e75ff?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Auditoria QA](https://img.shields.io/badge/Auditoria_QA-100%25_Aprovado-success?style=for-the-badge)](celula_usinagem_inteligente/TESTES.md)

---

## 🌐 Demonstração Online no GitHub Pages

Acesse a página do projeto com documentação interativa e showcase da célula:  
👉 **[https://professor-rafael-selvagio.github.io/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/](https://professor-rafael-selvagio.github.io/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/)**

---

## 🏭 Visão Geral da Situação de Aprendizagem

Aplicação em **Streamlit** integrada à API industrial didática do **AI DataLab** e ao **Google Gemini com Function Calling**, desenvolvida para a equipe de manutenção de uma empresa metalmecânica monitorar e analisar o comportamento de dois equipamentos:

1. **Centro de Usinagem CNC** (`CENTRO-USINAGEM-01`)
2. **Furadeira Industrial** (`FURADEIRA-01`)

### 🎯 Problema Resolvido
A consulta isolada da última leitura não atende às necessidades técnicas: medições podem parecer normais pontualmente, mas a sequência temporal revela oscilações, tendências térmicas e registros incomuns (outliers). A aplicação centraliza os dados, calcula indicadores estatísticos comprovados e fornece um assistente de IA que nunca alucina números.

---

## 🧭 Desafios Investigativos da Manutenção (Desafios A a F)

| Desafio | Foco Técnico | Implementação em Python |
|:---:|---|---|
| **A** | **Comportamento Habitual** | Média aritmética, mediana, amplitude interquartil (IQR) e desvio absoluto mediano (MAD). |
| **B** | **Regularidade & Oscilação** | Desvio padrão, variância, amplitude total e coeficiente de variação (CV%). |
| **C** | **Registros Incomuns (Outliers)** | Critério explícito de Tukey ($Q_1 - 1.5 \times \text{IQR}$ e $Q_3 + 1.5 \times \text{IQR}$). |
| **D** | **Mudança Temporal / Tendência** | Regressão linear simples (OLS) avaliando inclinação e direção do processo ao longo do tempo. |
| **E** | **Comparação entre Máquinas** | Validação estrita de compatibilidade física de grandezas e unidades antes de comparar. |
| **F** | **Limites & Confiabilidade** | Declaração explícita de suficiência amostral, período temporal e natureza didática dos dados. |

---

## 🤖 Assistente IA com Function Calling (Google Gemini)

O assistente utiliza o SDK oficial `google-genai` com **Function Calling automático**:
- **Zero Alucinação:** A IA é proibida via System Instruction de calcular valores de cabeça ou inventar medições.
- **Ferramentas Especializadas:** Cada cálculo e consulta é executado por uma função determinística em Python (`tools.py`).
- **Cautela de Engenharia:** Respostas prudentes em perguntas especulativas (ex.: *"Qual máquina vai falhar primeiro?"*), explicitando os limites das evidências disponíveis.

---

## 🛠️ Estrutura do Repositório (Conforme Seção 12 do Documento)

```text
POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/
├── app.py                       # Ponto de entrada raiz do Streamlit
├── requirements.txt             # Dependências unificadas do projeto
├── index.html                   # Página oficial do GitHub Pages
├── celula_usinagem_inteligente/ # Pacote completo da Situação de Aprendizagem
│   ├── app.py                   # Dashboard industrial em Streamlit (4 abas)
│   ├── analise.py               # Motor estatístico puro (Desafios A a F)
│   ├── api_client.py            # Cliente HTTP com fallback e normalização
│   ├── tools.py                 # 7 ferramentas para Function Calling do Gemini
│   ├── assistente.py            # Orquestração do chat com Google GenAI SDK
│   ├── config.py                # Configurações centralizadas e validações
│   ├── test_suite.py            # Bateria formal dos testes T01 a T10
│   ├── requirements.txt         # Dependências do pacote
│   ├── README.md                # Documentação técnica do Streamlit
│   ├── REQUISITOS.md            # Rastreabilidade dos 20 Requisitos (RF01 a RF20)
│   ├── ANALISE_DADOS.md         # Fundamentação matemática e estatística
│   ├── PROMPTS.md               # Catálogo de prompts e system instruction
│   ├── TESTES.md                # Relatório formal de testes com evidências
│   └── ARQUITETURA.md           # Diagramas arquiteturais C4 e Mermaid
└── README.md                    # Documentação principal deste repositório
```

---

## 🚀 Como Executar Localmente

### 1. Clonar o Repositório
```bash
git clone https://github.com/professor-rafael-selvagio/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais.git
cd POS-IA-Monitoramento-Inteligente-Maquinas-Industriais
```

### 2. Criar e Ativar Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# ou: venv\Scripts\activate # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar a Chave do Gemini (Opcional para a IA)
```bash
export GEMINI_API_KEY="sua-chave-aqui"   # Linux/macOS
# ou: set GEMINI_API_KEY=sua-chave-aqui # Windows
```
> *A chave também pode ser informada diretamente no campo protegido por senha na barra lateral da aplicação.*

### 5. Executar o Streamlit
```bash
streamlit run app.py
```
Acesse no navegador: **`http://localhost:8501`**

---

## 🧪 Bateria Formal de Testes (T01 a T10)

Para rodar os testes automatizados da aplicação:
```bash
cd celula_usinagem_inteligente
python3 test_suite.py -v
```

**Resultado da Auditoria:** `10/10 Testes Aprovados` em 0.026s.

---

## 📄 Licença e Uso Didático

Projeto desenvolvido para fins educacionais na **Pós-Graduação em Inteligência Artificial**, atendendo a 100% dos requisitos estipulados na Situação de Aprendizagem da Aula 04 pelo **Prof. Paulo José Rodolpho**.
