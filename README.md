# Monitoramento e Análise Inteligente de Máquinas Industriais (AI DataLab + Gemini Function Calling)
**Pós-Graduação em Inteligência Artificial • Módulo 3: Linguagem de Programação**  
*Prof. Paulo José Rodolpho*

[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Online-22c55e?style=for-the-badge&logo=github)](https://professor-rafael-selvagio.github.io/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/)
[![Python](https://img.shields.io/badge/Python-3.11+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Flask](https://img.shields.io/badge/Flask-3.1+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-Function_Calling-8e75ff?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

---

## 🌐 Demonstração Online no GitHub Pages

Acesse a interface interativa diretamente no seu navegador:  
👉 **[https://professor-rafael-selvagio.github.io/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/](https://professor-rafael-selvagio.github.io/POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/)**

> **Destaques da Página:**
> - Alternância dinâmica de **Tema Claro e Escuro** com persistência no `localStorage`.
> - Catálogo completo das **11 rotas da API Industrial** com teste direto e visualizador de JSON.
> - **Assistente IA Conversacional** demonstrando o funcionamento de **Function Calling** em tempo real sem alucinação numérica.

---

## 🏭 Visão Geral do Projeto

Este repositório reúne duas soluções complementares desenvolvidas para o monitoramento da célula de usinagem industrial integrada ao **AI DataLab**:

1. **Dashboard Web & API Explorer (Flask):** Interface moderna para catálogo e inspeção das 11 rotas industriais, testes diretos e chat com Gemini Function Calling.
2. **Aplicação Industrial Completa (Streamlit):** Painel analítico com telemetria em tempo real, séries temporais, motor estatístico determinístico (Desafios A a F) e assistente inteligente.

---

## 📡 As 11 Rotas Integradas da API Industrial

| # | Método | Endpoint | Descrição |
|:---:|:---:|---|---|
| **1** | `GET` | `/api/v1/health` | Status de saúde e integridade da API |
| **2** | `GET` | `/api/v1/machines` | Lista de máquinas e seus identificadores |
| **3** | `GET` | `/api/v1/machines/BOMBA-01/latest` | Últimas leituras da máquina ativa |
| **4** | `GET` | `/api/v1/machines/BOMBA-01/readings?limit=100` | Histórico de telemetria da máquina |
| **5** | `GET` | `/api/v1/variables` | Variáveis e grandezas físicas monitoradas |
| **6** | `GET` | `/api/v1/production?limit=100` | Registros das ordens de produção |
| **7** | `GET` | `/api/v1/products` | Catálogo de produtos cadastrados |
| **8** | `GET` | `/api/v1/shifts` | Escalas e turnos de trabalho da fábrica |
| **9** | `GET` | `/api/v1/datasets` | Datasets analíticos para análise histórica |
| **10** | `GET` | `/api/v1/scenarios` | Cenários de simulação e regime de carga |
| **11** | `GET` | `/api/v1/events` | Histórico de eventos e alertas operacionais |

---

## 🛠️ Estrutura do Repositório

```text
POS-IA-Monitoramento-Inteligente-Maquinas-Industriais/
├── index.html                   # Página principal estática do GitHub Pages
├── app.py                       # Servidor Flask com Blueprint e APIClient
├── templates/
│   └── index.html               # Template dinâmico para a aplicação Flask
├── Aula4_FCalling_Rafael.py     # Script CLI demonstrando 11 tools com Gemini
├── celula_usinagem_inteligente/ # Aplicação Streamlit e Situação de Aprendizagem
│   ├── app.py                   # Dashboard industrial em Streamlit
│   ├── analise.py               # Motor estatístico puro (Desafios A a F)
│   ├── api_client.py            # Cliente HTTP com fallback e normalização
│   ├── tools.py                 # Ferramentas Python para Function Calling
│   ├── assistente.py            # Orquestração do chat com Google GenAI SDK
│   ├── config.py                # Configurações centralizadas e validações
│   ├── test_suite.py            # Bateria formal dos testes T01 a T10
│   ├── requirements.txt         # Dependências do projeto
│   ├── README.md                # Documentação técnica do Streamlit
│   ├── REQUISITOS.md            # Rastreabilidade dos 20 Requisitos (RF01-RF20)
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

### 2. Criar e Ativar o Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# ou: venv\Scripts\activate # Windows
```

### 3. Instalar Dependências
```bash
pip install -r celula_usinagem_inteligente/requirements.txt
```

### 4. Configurar a Chave do Gemini
```bash
export GEMINI_API_KEY="sua-chave-aqui"   # Linux/macOS
# ou: set GEMINI_API_KEY=sua-chave-aqui # Windows
```

### 5. Executar as Aplicações

#### Opção A: Dashboard Streamlit (Célula de Usinagem)
```bash
cd celula_usinagem_inteligente
streamlit run app.py
```
Acesse: `http://localhost:8501`

#### Opção B: Servidor Flask (API Explorer das 11 Rotas)
```bash
python3 app.py
```
Acesse: `http://localhost:5500`

#### Opção C: Script CLI no Terminal
```bash
python3 Aula4_FCalling_Rafael.py
```

---

## 🧪 Bateria de Testes Automatizados (T01 a T10)

Para executar a suíte formal de testes:
```bash
cd celula_usinagem_inteligente
python3 test_suite.py -v
```

Status da Auditoria: **10/10 Testes Aprovados (100% de Conformidade).**

---

## 📄 Licença e Uso Didático

Projeto desenvolvido para fins educacionais no curso de **Pós-Graduação em Inteligência Artificial**, demonstrando a integração responsável entre **sistemas industriais simulados (AI DataLab)** e **Grandes Modelos de Linguagem (LLMs)** através de chamadas estritas a funções determinísticas (**Function Calling**).
