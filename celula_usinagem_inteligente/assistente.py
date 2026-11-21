"""Módulo do Assistente Inteligente com Google Gemini e Function Calling.

Configura o cliente oficial da biblioteca google-genai, define as instruções de
sistema (System Instruction) com rigor técnico industrial e gerencia a comunicação
conversacional com acionamento automático de ferramentas Python.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from google import genai

from config import DECLARACAO_DADOS_DIDATICOS, MODELO_GEMINI_PADRAO
from tools import FERRAMENTAS_GEMINI, coletar_ferramentas_executadas

logger = logging.getLogger(__name__)

# Instrução de Sistema Industrial com diretrizes estritas de cautela e veracidade
SYSTEM_INSTRUCTION_INDUSTRIAL = f"""
Você é o Assistente Especialista da Célula de Usinagem Inteligente (SENAI / AI DataLab).
Sua missão é auxiliar a equipe de manutenção mecânica e operadores a monitorar e interpretar
a telemetria dos dois únicos equipamentos da célula:
1. CENTRO-USINAGEM-01 (Centro de Usinagem CNC)
2. FURADEIRA-01 (Furadeira Industrial)

DIRETRIZES TÉCNICAS E REGRAS MANDATÓRIAS:
1. REGRA DE OURO (SEM ALUCINAÇÃO): NUNCA invente medições, horários ou grandezas. NUNCA calcule
   médias, tendências ou anomalias mentalmente. Para QUALQUER pergunta numérica ou investigativa,
   você DEVE acionar a ferramenta Python correspondente.
2. OPERAÇÃO SOMENTE LEITURA: Todas as ferramentas operam estritamente em leitura. Você não envia
   comandos nem altera parâmetros de máquinas.
3. RESTRIÇÃO DE EQUIPAMENTOS: Esta célula monitora exclusivamente 'CENTRO-USINAGEM-01' e 'FURADEIRA-01'.
   Se o usuário solicitar informações de outras máquinas, recuse educadamente explicando o escopo.
4. CAUTELA DE ENGENHARIA E INTERPRETAÇÃO:
   - Um registro incomum (outlier) indica apenas um valor estatisticamente atípico que merece
     inspeção da equipe de manutenção; NUNCA afirme categoricamente que o equipamento 'quebrou' ou 'tem defeito'.
   - Ao comparar grandezas, mencione sempre as unidades e lembre que Centro de Usinagem e Furadeira
     possuem regimes de corte e potências distintas.
5. RESPOSTA A PERGUNTAS ESPECULATIVAS (RF19, Teste T10):
   - Se o usuário perguntar 'Qual máquina vai falhar primeiro?' ou fizer previsões sem base, seja
     prudente e declare explicitamente: os dados são de ambiente simulado educacional; os registros
     disponíveis mostram o comportamento recente e oscilações, mas não sustentam cientificamente
     uma previsão de falha catastrófica sem ordens de serviço e modelagem de confiabilidade (MTBF).
6. COMUNICAÇÃO: Responda em português claro, técnico, estruturado com tópicos e destaque os
   números exatos retornados pelas funções Python.

Declaração obrigatória de contexto:
{DECLARACAO_DADOS_DIDATICOS}
"""


class AssistenteGemini:
    """Encapsula a sessão de chat e execução de ferramentas com a API do Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        modelo: str = MODELO_GEMINI_PADRAO,
        system_instruction: str = SYSTEM_INSTRUCTION_INDUSTRIAL,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.modelo = modelo
        self.system_instruction = system_instruction
        self._cliente: genai.Client | None = None
        self._chat: Any = None

        if self.api_key:
            self._inicializar_chat()

    def _inicializar_chat(self) -> None:
        """Cria a instância do cliente e a sessão de chat com Function Calling."""
        try:
            self._cliente = genai.Client(api_key=self.api_key)
            self._chat = self._cliente.chats.create(
                model=self.modelo,
                config={
                    "tools": FERRAMENTAS_GEMINI,
                    "system_instruction": self.system_instruction,
                },
            )
            logger.info("Chat do Gemini inicializado com sucesso (modelo: %s)", self.modelo)
        except Exception as err:
            logger.error("Falha ao inicializar o cliente Gemini: %s", err)
            self._chat = None
            raise

    def enviar_mensagem(self, pergunta: str) -> dict[str, Any]:
        """Envia a pergunta do usuário ao Gemini e retorna a resposta com ferramentas acionadas.

        Atende aos Requisitos Funcionais RF15, RF16 e RF18.

        Args:
            pergunta: Pergunta do usuário em linguagem natural.

        Returns:
            Dicionário contendo o texto da resposta e a lista de ferramentas Python chamadas.
        """
        if not self.api_key:
            return {
                "resposta": (
                    "⚠️ Chave de API do Google Gemini não configurada. "
                    "Por favor, configure a variável de ambiente `GEMINI_API_KEY` ou insira sua chave "
                    "no campo apropriado na barra lateral da aplicação."
                ),
                "ferramentas_chamadas": [],
                "status": "sem_chave",
            }

        if self._chat is None:
            try:
                self._inicializar_chat()
            except Exception as err:
                return {
                    "resposta": f"❌ Falha de autenticação ou inicialização do Gemini: {err}",
                    "ferramentas_chamadas": [],
                    "status": "erro_inicializacao",
                }

        # Limpa o rastreamento anterior
        coletar_ferramentas_executadas()

        try:
            # Envia a mensagem ao chat; o SDK gerencia chamadas de função automaticamente
            resposta = self._chat.send_message(pergunta)
            texto_resposta = resposta.text if resposta and resposta.text else "O assistente não retornou texto."

            # Coleta as ferramentas que foram executadas pelo SDK
            ferramentas_chamadas = coletar_ferramentas_executadas()

            return {
                "resposta": texto_resposta,
                "ferramentas_chamadas": ferramentas_chamadas,
                "status": "sucesso",
            }

        except Exception as err:
            logger.exception("Erro ao processar mensagem no Gemini: %s", err)
            ferramentas_chamadas = coletar_ferramentas_executadas()
            return {
                "resposta": (
                    f"⚠️ Ocorreu uma falha na consulta ao Gemini ou na execução da ferramenta: {err}. "
                    "Verifique sua conexão e tente novamente."
                ),
                "ferramentas_chamadas": ferramentas_chamadas,
                "status": "erro_execucao",
            }
