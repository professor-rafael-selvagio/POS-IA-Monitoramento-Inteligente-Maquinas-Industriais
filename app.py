"""
Aula 04 – Painel Web: AI DataLab Explorer + Gemini Function Calling.
Suporte completo às 11 rotas do AI DataLab.
"""

from __future__ import annotations

import inspect
import logging
import os
import threading
from dataclasses import dataclass

import requests
from flask import Blueprint, Flask, jsonify, render_template, request
from google import genai

# ─────────────────────────────────────────────
# 1. CONFIGURAÇÃO CENTRALIZADA
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class Config:
    """Parâmetros de configuração lidos do ambiente (ou valores padrão)."""

    servidor: str   = os.getenv("SERVIDOR_API", "http://10.110.18.12:10999")
    maquina: str    = os.getenv("MAQUINA", "BOMBA-01")
    modelo: str     = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    porta: int      = int(os.getenv("PORT", "5500"))
    timeout: int    = 10


CFG = Config()

# ─────────────────────────────────────────────
# 2. LOGGING
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("aidatalab")

# ─────────────────────────────────────────────
# 3. CLIENTE HTTP PARA AS 11 ROTAS DO AI DATALAB
# ─────────────────────────────────────────────

class APIClient:
    """Encapsula todas as chamadas HTTP ao servidor do AI DataLab."""

    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self._base = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        self._timeout = timeout

    def _get(self, path: str, params: dict | None = None) -> dict | list:
        url = f"{self._base}{path}"
        log.info("GET %s  params=%s", url, params or {})
        resp = self._session.get(url, params=params, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()

    # 1. Saúde do serviço
    def health(self) -> dict:
        return self._get("/api/v1/health")

    # 2. Lista de máquinas e seus códigos
    def machines(self) -> list | dict:
        return self._get("/api/v1/machines")

    # 3. Últimas leituras da máquina selecionada
    def latest_readings(self, maquina: str = "BOMBA-01") -> dict:
        return self._get(f"/api/v1/machines/{maquina}/latest")

    # 4. Histórico da máquina selecionada
    def readings_history(self, maquina: str = "BOMBA-01", limit: int = 100) -> list | dict:
        return self._get(f"/api/v1/machines/{maquina}/readings", {"limit": limit})

    # 5. Variáveis
    def variables(self) -> list | dict:
        return self._get("/api/v1/variables")

    # 6. Registros de produção
    def production(self, limit: int = 100) -> list | dict:
        return self._get("/api/v1/production", {"limit": limit})

    # 7. Produtos
    def products(self) -> list | dict:
        return self._get("/api/v1/products")

    # 8. Turnos
    def shifts(self) -> list | dict:
        return self._get("/api/v1/shifts")

    # 9. Datasets
    def datasets(self) -> list | dict:
        return self._get("/api/v1/datasets")

    # 10. Cenários
    def scenarios(self) -> list | dict:
        return self._get("/api/v1/scenarios")

    # 11. Eventos
    def events(self) -> list | dict:
        return self._get("/api/v1/events")


api = APIClient(CFG.servidor, CFG.timeout)

# ─────────────────────────────────────────────
# 4. RASTREIO THREAD-SAFE DE FERRAMENTAS
# ─────────────────────────────────────────────

_tls = threading.local()


def _registrar(nome: str) -> None:
    """Registra o nome da ferramenta executada na thread atual."""
    if not hasattr(_tls, "chamadas"):
        _tls.chamadas = []
    _tls.chamadas.append(nome)


def _coletar_chamadas() -> list[str]:
    """Retorna e limpa a lista de ferramentas da thread atual."""
    chamadas = getattr(_tls, "chamadas", [])
    _tls.chamadas = []
    return chamadas


# ─────────────────────────────────────────────
# 5. FUNÇÕES-FERRAMENTA (expostas ao Gemini)
# ─────────────────────────────────────────────

def consultar_health() -> dict:
    """Consulta a saude e status operacional do servico da API."""
    _registrar("consultar_health")
    return api.health()


def consultar_maquinas() -> list | dict:
    """Consulta a lista de todas as maquinas industriais e seus respectivos codigos (ex: BOMBA-01, COMPRESSOR-01)."""
    _registrar("consultar_maquinas")
    return api.machines()


def consultar_ultimas_leituras(codigo_maquina: str = CFG.maquina) -> dict:
    """Consulta as ultimas leituras de sensores da maquina selecionada (por padrao 'BOMBA-01')."""
    _registrar(f"consultar_ultimas_leituras(codigo_maquina='{codigo_maquina}')")
    return api.latest_readings(codigo_maquina)


def consultar_historico(codigo_maquina: str = CFG.maquina, limit: int = 100) -> list | dict:
    """Consulta o historico de telemetria da maquina selecionada (limite padrao 100 registros)."""
    _registrar(f"consultar_historico(codigo_maquina='{codigo_maquina}', limit={limit})")
    return api.readings_history(codigo_maquina, limit=limit)


def consultar_variaveis() -> list | dict:
    """Consulta as variaveis industriais monitoradas no sistema (pressao, temperatura, vazao, vibracao, etc)."""
    _registrar("consultar_variaveis")
    return api.variables()


def consultar_producao(limit: int = 100) -> list | dict:
    """Consulta os registros de producao da fabrica (limite padrao de 100 itens)."""
    _registrar(f"consultar_producao(limit={limit})")
    return api.production(limit)


def consultar_produtos() -> list | dict:
    """Consulta a lista de produtos cadastrados no catalogo do sistema."""
    _registrar("consultar_produtos")
    return api.products()


def consultar_turnos() -> list | dict:
    """Consulta as escalas e informacoes dos turnos de trabalho na fabrica."""
    _registrar("consultar_turnos")
    return api.shifts()


def consultar_datasets() -> list | dict:
    """Consulta os conjuntos de dados (datasets) disponiveis no sistema para analise."""
    _registrar("consultar_datasets")
    return api.datasets()


def consultar_cenarios() -> list | dict:
    """Consulta os cenarios de operacao ou simulacao configurados no sistema."""
    _registrar("consultar_cenarios")
    return api.scenarios()


def consultar_eventos() -> list | dict:
    """Consulta o historico de eventos, ocorrencias e alertas industriais gerados no sistema."""
    _registrar("consultar_eventos")
    return api.events()


# Lista com todas as 11 ferramentas expostas ao Gemini
FERRAMENTAS = [
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

# Mapa nome → função para o teste direto no painel web
MAPA_ENDPOINTS: dict[str, callable] = {
    "health":     consultar_health,
    "machines":   consultar_maquinas,
    "latest":     consultar_ultimas_leituras,
    "readings":   consultar_historico,
    "variables":  consultar_variaveis,
    "production": consultar_producao,
    "products":   consultar_produtos,
    "shifts":     consultar_turnos,
    "datasets":   consultar_datasets,
    "scenarios":  consultar_cenarios,
    "events":     consultar_eventos,
}

# ─────────────────────────────────────────────
# 6. INSTRUÇÃO DE SISTEMA DO GEMINI
# ─────────────────────────────────────────────

SYSTEM_INSTRUCTION = (
    "Voce e um assistente especialista no monitoramento industrial do AI DataLab. "
    "Voce tem acesso a 11 ferramentas para consultar: saude do servico (/health), "
    "lista de maquinas (/machines), ultimas leituras e historico por maquina (/latest e /readings), "
    "variaveis monitoradas (/variables), registros de producao (/production), catalogo de produtos (/products), "
    "turnos (/shifts), datasets (/datasets), cenarios (/scenarios) e eventos/alertas (/events). "
    "Para perguntas sobre esses dados, use SEMPRE a ferramenta adequada. "
    "Ao consultar telemetrias de maquinas, voce pode passar o codigo da maquina informado pelo usuario (ex: BOMBA-01). "
    "Nao invente valores. Informe quando nao houver dados ou a consulta falhar. "
    "Resuma resultados extensos e mencione unidades, horarios e identificadores quando disponiveis. "
    "As ferramentas sao somente de leitura."
)

# ─────────────────────────────────────────────
# 7. BLUEPRINT DE ROTAS
# ─────────────────────────────────────────────

bp = Blueprint("painel", __name__)


@bp.route("/")
def index():
    """Renderiza o painel principal com os 11 endpoints."""
    return render_template(
        "index.html",
        servidor=CFG.servidor,
        modelo=CFG.modelo,
        maquina=CFG.maquina,
    )


@bp.route("/api/test-endpoint", methods=["POST"])
def test_endpoint():
    """Executa uma chamada direta a um dos 11 endpoints da API industrial."""
    dados = request.get_json(silent=True) or {}
    nome = dados.get("endpoint", "")

    funcao = MAPA_ENDPOINTS.get(nome)
    if funcao is None:
        return jsonify(sucesso=False, erro=f"Endpoint '{nome}' não reconhecido."), 400

    try:
        # Permite passagem opcional de parâmetros customizados (maquina, limit)
        sig = inspect.signature(funcao)
        kwargs = {}
        if "codigo_maquina" in sig.parameters and "maquina" in dados:
            kwargs["codigo_maquina"] = dados["maquina"]
        if "limit" in sig.parameters and "limit" in dados:
            try:
                kwargs["limit"] = int(dados["limit"])
            except (ValueError, TypeError):
                pass

        resultado = funcao(**kwargs) if kwargs else funcao()
        return jsonify(sucesso=True, dados=resultado, status_code=200)

    except requests.RequestException as exc:
        log.warning("Falha ao chamar endpoint '%s': %s", nome, exc)
        return jsonify(sucesso=False, erro=str(exc), servidor=CFG.servidor), 502
    except Exception as exc:
        log.exception("Erro ao executar endpoint '%s'", nome)
        return jsonify(sucesso=False, erro=str(exc)), 500


@bp.route("/api/chat", methods=["POST"])
def chat():
    """Recebe uma pergunta e aciona o Gemini com Function Calling automático."""
    dados = request.get_json(silent=True) or {}
    mensagem = dados.get("mensagem", "").strip()

    if not mensagem:
        return jsonify(erro="A mensagem não pode estar vazia."), 400

    if not CFG.gemini_key:
        return jsonify(
            resposta=(
                "⚠️ A variável de ambiente GEMINI_API_KEY não foi configurada. "
                "Defina-a com: export GEMINI_API_KEY='sua-chave'"
            ),
            funcoes_chamadas=[],
        )

    _coletar_chamadas()

    try:
        cliente = genai.Client(api_key=CFG.gemini_key)
        sessao = cliente.chats.create(
            model=CFG.modelo,
            config={
                "tools": FERRAMENTAS,
                "system_instruction": SYSTEM_INSTRUCTION,
            },
        )

        resposta = sessao.send_message(mensagem)
        texto = resposta.text or "O modelo processou a requisição, mas não retornou texto."

        return jsonify(resposta=texto, funcoes_chamadas=_coletar_chamadas())

    except requests.RequestException as exc:
        log.error("Erro HTTP durante Function Calling: %s", exc)
        return jsonify(
            resposta=f"Erro de comunicação com a API industrial ({CFG.servidor}): {exc}",
            funcoes_chamadas=_coletar_chamadas(),
        )
    except Exception as exc:
        log.exception("Erro inesperado no chat")
        return jsonify(
            resposta=f"Erro ao processar consulta: {exc}",
            funcoes_chamadas=_coletar_chamadas(),
        )


# ─────────────────────────────────────────────
# 8. FACTORY DO APP + ERROR HANDLERS
# ─────────────────────────────────────────────

def create_app() -> Flask:
    """Cria e configura a aplicação Flask (factory pattern)."""
    application = Flask(__name__)
    application.register_blueprint(bp)

    @application.errorhandler(404)
    def not_found(_):
        return jsonify(erro="Recurso não encontrado."), 404

    @application.errorhandler(500)
    def internal_error(_):
        return jsonify(erro="Erro interno do servidor."), 500

    return application


# ─────────────────────────────────────────────
# 9. ENTRYPOINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()

    log.info("🚀  Servidor Flask em http://127.0.0.1:%s", CFG.porta)
    log.info("📡  API Industrial: %s", CFG.servidor)
    log.info("🤖  Modelo Gemini:  %s", CFG.modelo)
    log.info("⚙️   Total de rotas integradas: %s", len(FERRAMENTAS))

    app.run(host="0.0.0.0", port=CFG.porta, debug=True)
