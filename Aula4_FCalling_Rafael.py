import os
import requests
from google import genai

SERVIDOR = os.getenv("SERVIDOR_API", "http://10.110.18.12:10999")
MAQUINA_PADRAO = os.getenv("MAQUINA", "BOMBA-01")
MODELO = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


# 1. Health check do serviço
def consultar_health() -> dict:
    """Consulta o status de saude (health check) e operacao do servico da API."""
    url = f"{SERVIDOR}/api/v1/health"
    print("\n[Python] Executando consultar_health()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 2. Lista de máquinas e seus códigos
def consultar_maquinas() -> list | dict:
    """Consulta a lista de todas as maquinas industriais e seus respectivos codigos (ex: BOMBA-01, COMPRESSOR-01)."""
    url = f"{SERVIDOR}/api/v1/machines"
    print("\n[Python] Executando consultar_maquinas()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 3. Últimas leituras da máquina selecionada
def consultar_ultimas_leituras(codigo_maquina: str = MAQUINA_PADRAO) -> dict:
    """Consulta as ultimas leituras de sensores da maquina selecionada (ex: BOMBA-01)."""
    url = f"{SERVIDOR}/api/v1/machines/{codigo_maquina}/latest"
    print(f"\n[Python] Executando consultar_ultimas_leituras(codigo_maquina='{codigo_maquina}')")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 4. Histórico da máquina selecionada (limite padrão 100)
def consultar_historico(codigo_maquina: str = MAQUINA_PADRAO, limit: int = 100) -> list | dict:
    """Consulta o historico de leituras de telemetria da maquina selecionada. Aceita o codigo da maquina e quantidade de registros (limite padrao 100)."""
    url = f"{SERVIDOR}/api/v1/machines/{codigo_maquina}/readings"
    print(f"\n[Python] Executando consultar_historico(codigo_maquina='{codigo_maquina}', limit={limit})")
    resposta = requests.get(url, params={"limit": limit}, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 5. Variáveis industriais monitoradas
def consultar_variaveis() -> list | dict:
    """Consulta a lista de variaveis e grandezas monitoradas no sistema industrial (ex: pressao, temperatura, vazao, vibracao)."""
    url = f"{SERVIDOR}/api/v1/variables"
    print("\n[Python] Executando consultar_variaveis()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 6. Registros de produção (limite padrão 100)
def consultar_producao(limit: int = 100) -> list | dict:
    """Consulta os registros de producao da fabrica com limite configuravel (padrao 100)."""
    url = f"{SERVIDOR}/api/v1/production"
    print(f"\n[Python] Executando consultar_producao(limit={limit})")
    resposta = requests.get(url, params={"limit": limit}, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 7. Produtos cadastrados
def consultar_produtos() -> list | dict:
    """Consulta o catalogo de produtos cadastrados no sistema."""
    url = f"{SERVIDOR}/api/v1/products"
    print("\n[Python] Executando consultar_produtos()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 8. Turnos de trabalho
def consultar_turnos() -> list | dict:
    """Consulta as escalas e informacoes dos turnos de trabalho da fabrica."""
    url = f"{SERVIDOR}/api/v1/shifts"
    print("\n[Python] Executando consultar_turnos()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 9. Datasets disponíveis
def consultar_datasets() -> list | dict:
    """Consulta a lista de conjuntos de dados (datasets) disponiveis no sistema para analise."""
    url = f"{SERVIDOR}/api/v1/datasets"
    print("\n[Python] Executando consultar_datasets()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 10. Cenários
def consultar_cenarios() -> list | dict:
    """Consulta os cenarios de operacao e simulacao cadastrados no sistema."""
    url = f"{SERVIDOR}/api/v1/scenarios"
    print("\n[Python] Executando consultar_cenarios()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# 11. Eventos e alertas
def consultar_eventos() -> list | dict:
    """Consulta o historico de eventos, alertas e ocorrencias registradas no sistema industrial."""
    url = f"{SERVIDOR}/api/v1/events"
    print("\n[Python] Executando consultar_eventos()")
    resposta = requests.get(url, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


# LISTA DE TODAS AS 11 FERRAMENTAS EXPOSTAS AO GEMINI
TODAS_FERRAMENTAS = [
    consultar_health,
    consultar_maquinas,
    consultar_ultimas_leituras,
    consultar_historico,
    consultar_variaveis,
    consultar_producao,
    consultar_produtos,
    consultar_turnos,
    consultar_datasets,
    consultar_cenarios,
    consultar_eventos,
]


def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("Configure a variavel de ambiente GEMINI_API_KEY antes de executar.")
        return

    cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    # FUNCTION CALLING AUTOMATICO COM TODAS AS ROTAS DO AI DATALAB
    chat = cliente.chats.create(
        model=MODELO,
        config={
            "tools": TODAS_FERRAMENTAS,
            "system_instruction": (
                "Voce e um assistente especialista no monitoramento industrial do AI DataLab. "
                "Voce tem acesso a 11 ferramentas para consultar: saude do servico (/health), "
                "lista de maquinas (/machines), ultimas leituras e historico de leituras por maquina (/latest e /readings), "
                "variaveis monitoradas (/variables), registros de producao (/production), catalogo de produtos (/products), "
                "turnos (/shifts), datasets (/datasets), cenarios (/scenarios) e eventos/alertas (/events). "
                "Para perguntas sobre esses dados, use SEMPRE a ferramenta adequada. "
                "Ao consultar telemetrias de maquinas, voce pode passar o codigo da maquina informado pelo usuario (ex: BOMBA-01). "
                "Nao invente valores. Informe quando nao houver dados ou a consulta falhar. "
                "Resuma resultados extensos e mencione unidades, horarios e identificadores quando disponiveis. "
                "As ferramentas sao somente de leitura."
            ),
        },
    )

    print("=" * 60)
    print("ASSISTENTE INDUSTRIAL AI DATALAB - 11 ENDPOINTS INTEGRADOS")
    print("=" * 60)
    print("Exemplos:")
    print(" - Como esta a saude da API?")
    print(" - Quais maquinas temos cadastradas?")
    print(" - Mostre as ultimas leituras da BOMBA-01.")
    print(" - Consulte o historico de 100 leituras da BOMBA-01.")
    print(" - Quais sao as variaveis monitoradas?")
    print(" - Mostre os registros de producao recentes.")
    print(" - Quais sao os produtos e turnos cadastrados?")
    print(" - Existem eventos ou alertas registrados?")
    print(" - Quais datasets e cenarios estao disponiveis?")

    while True:
        pergunta = input("\nPergunta (ou S para sair): ").strip()
        if pergunta.upper() == "S":
            print("Programa encerrado.")
            break
        if not pergunta:
            continue

        try:
            resposta = chat.send_message(pergunta)
            print("\n[Gemini] Resposta:")
            print(resposta.text or "O modelo nao retornou texto.")
        except requests.RequestException as erro:
            print(f"Erro na API do AI DataLab: {erro}")
        except Exception as erro:
            print(f"Falha na consulta ao Gemini ou na ferramenta: {erro}")


if __name__ == "__main__":
    main()
