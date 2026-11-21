"""Bateria de Testes Automatizados (T01 a T10) para a Célula de Usinagem Inteligente.

Executa validações formais correspondentes aos testes obrigatórios descritos na
Seção 11 da especificação da Situação de Aprendizagem.
"""

from __future__ import annotations

import unittest
from datetime import datetime

import numpy as np
import pandas as pd

from analise import (
    calcular_comportamento_habitual,
    calcular_regularidade,
    calcular_tendencia_temporal,
    comparar_maquinas,
    detectar_registros_incomuns,
)
from api_client import (
    APIClientError,
    gerar_dados_didaticos_historico,
    gerar_dados_didaticos_ultima_leitura,
    obter_historico,
    obter_ultima_leitura,
)
from config import (
    DECLARACAO_DADOS_DIDATICOS,
    MAQUINAS_VALIDAS,
    METADADOS_VARIAVEIS,
    validar_maquina,
)
from tools import FERRAMENTAS_GEMINI, consultar_ultima_leitura_maquina


class TestSuiteCelulaUsinagem(unittest.TestCase):
    """Bateria formal dos testes T01 a T10."""

    def test_t01_maquinas_autorizadas(self):
        """T01: Aplicação valida e aceita exclusivamente as duas máquinas permitidas."""
        self.assertEqual(validar_maquina("CENTRO-USINAGEM-01"), "CENTRO-USINAGEM-01")
        self.assertEqual(validar_maquina("FURADEIRA-01"), "FURADEIRA-01")
        self.assertEqual(validar_maquina(" centro-usinagem-01 "), "CENTRO-USINAGEM-01")

        with self.assertRaises(ValueError):
            validar_maquina("BOMBA-01")

        with self.assertRaises(ValueError):
            validar_maquina("COMPRESSOR-01")

        with self.assertRaises(ValueError):
            validar_maquina("ROBO-KUKA-01")

    def test_t02_estrutura_ultima_leitura(self):
        """T02: Medições retornadas contêm variáveis, unidades, timestamps e grandezas."""
        dados = gerar_dados_didaticos_ultima_leitura("CENTRO-USINAGEM-01")
        self.assertIn("machine_id", dados)
        self.assertIn("timestamp", dados)
        self.assertIn("medicoes", dados)

        meds = dados["medicoes"]
        self.assertIn("temperatura", meds)
        self.assertEqual(meds["temperatura"]["unidade"], "°C")
        self.assertIn("vibracao", meds)
        self.assertEqual(meds["vibracao"]["unidade"], "mm/s")

    def test_t03_troca_de_maquina_altera_origem(self):
        """T03: Alternar entre CENTRO-USINAGEM-01 e FURADEIRA-01 altera variáveis e limites."""
        d_centro = gerar_dados_didaticos_ultima_leitura("CENTRO-USINAGEM-01")
        d_furad = gerar_dados_didaticos_ultima_leitura("FURADEIRA-01")

        self.assertEqual(d_centro["machine_id"], "CENTRO-USINAGEM-01")
        self.assertEqual(d_furad["machine_id"], "FURADEIRA-01")

        # Centro possui corrente; Furadeira possui pressao
        self.assertIn("corrente", d_centro["medicoes"])
        self.assertNotIn("corrente", d_furad["medicoes"])
        self.assertIn("pressao", d_furad["medicoes"])
        self.assertNotIn("pressao", d_centro["medicoes"])

    def test_t04_historico_ordem_cronologica(self):
        """T04: Histórico apresenta ordem cronológica crescente e quantidade coerente."""
        df = gerar_dados_didaticos_historico("CENTRO-USINAGEM-01", limit=30)
        self.assertEqual(len(df), 30)
        self.assertTrue(df["timestamp"].is_monotonic_increasing)
        self.assertIn("temperatura", df.columns)

    def test_t05_conferencia_matematica_independente(self):
        """T05: Conferência independente dos cálculos estatísticos com ground truth conhecido."""
        # Conjunto fixo conhecido: [10, 20, 20, 30, 40, 50, 100]
        dados_conhecidos = pd.Series([10.0, 20.0, 20.0, 30.0, 40.0, 50.0, 100.0])

        res_hab = calcular_comportamento_habitual(dados_conhecidos)
        res_reg = calcular_regularidade(dados_conhecidos)

        # Média calculada manualmente: (10+20+20+30+40+50+100)/7 = 270 / 7 = 38.571...
        self.assertAlmostEqual(res_hab["media"], 38.571, places=2)
        # Mediana ordenada: elemento central index 3 é 30.0
        self.assertEqual(res_hab["mediana"], 30.0)
        # Amplitude total: 100 - 10 = 90
        self.assertEqual(res_reg["amplitude_total"], 90.0)
        # Mínimo e Máximo
        self.assertEqual(res_reg["valor_minimo"], 10.0)
        self.assertEqual(res_reg["valor_maximo"], 100.0)

    def test_t06_deteccao_outliers_iqr_reproduzivel(self):
        """T06: Detecção de anomalias por IQR de Tukey com critérios explícitos e auditáveis."""
        df_teste = pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=10, freq="min"),
            "vibracao": [1.0, 1.1, 1.05, 1.02, 1.08, 1.04, 1.07, 1.03, 1.06, 9.99],
        })

        anomalias = detectar_registros_incomuns(df_teste, "vibracao", fator_iqr=1.5)
        self.assertEqual(anomalias["quantidade_anomalias"], 1)
        self.assertEqual(anomalias["registros_anomalos"][0]["valor"], 9.99)
        self.assertEqual(anomalias["registros_anomalos"][0]["tipo"], "Acima do Limite Superior")

    def test_t07_bloqueio_comparacao_grandezas_incompativeis(self):
        """T07: Bloqueio estrito de comparação de variáveis com grandezas ou unidades incompatíveis."""
        df_a = pd.DataFrame({"corrente": [10.0, 12.0, 15.0]})
        df_b = pd.DataFrame({"pressao": [5.0, 6.0, 5.5]})

        # Furadeira não tem corrente
        with self.assertRaises(ValueError):
            comparar_maquinas(df_a, df_b, "CENTRO-USINAGEM-01", "FURADEIRA-01", "corrente")

        # Centro não tem pressão
        with self.assertRaises(ValueError):
            comparar_maquinas(df_a, df_b, "CENTRO-USINAGEM-01", "FURADEIRA-01", "pressao")

    def test_t08_function_calling_tools_schema(self):
        """T08: Validação da disponibilidade e assinaturas das ferramentas do Gemini."""
        self.assertGreaterEqual(len(FERRAMENTAS_GEMINI), 6)
        nomes = [f.__name__ for f in FERRAMENTAS_GEMINI]
        self.assertIn("consultar_ultima_leitura_maquina", nomes)
        self.assertIn("consultar_historico_leituras", nomes)
        self.assertIn("analisar_estatisticas_variavel", nomes)
        self.assertIn("detectar_anomalias_outliers", nomes)
        self.assertIn("avaliar_tendencia_temporal", nomes)
        self.assertIn("comparar_duas_maquinas", nomes)
        self.assertIn("obter_declaracao_e_limites", nomes)

    def test_t09_resiliencia_servidor_incorreto(self):
        """T09: URL incorreta ou servidor fora gera tratamento gracioso de erro sem crash."""
        with self.assertRaises(APIClientError):
            obter_ultima_leitura(
                servidor="http://servidor-inexistente-12345.local",
                maquina="CENTRO-USINAGEM-01",
                timeout=1,
                usar_fallback_se_offline=False,
            )

    def test_t10_declaracao_prudente_perguntas_especulativas(self):
        """T10: Perguntas especulativas contam com declaração formal de limites e didática."""
        self.assertIn("AI DataLab", DECLARACAO_DADOS_DIDATICOS)
        self.assertIn("didáticos", DECLARACAO_DADOS_DIDATICOS.lower())
        self.assertIn("não correspondendo a diagnósticos definitivos", DECLARACAO_DADOS_DIDATICOS)


if __name__ == "__main__":
    unittest.main()
