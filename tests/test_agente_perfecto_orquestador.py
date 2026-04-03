"""Tests unitarios para AgentePerfectoOrquestador y MesaDeLosListos."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agente_perfecto_orquestador import (
    AGENT_CATALOGUE,
    AgentePerfectoOrquestador,
    AgentStatus,
    MesaDeLosListos,
)


class TestAgentCatalogue(unittest.TestCase):
    def test_exactamente_61_agentes(self) -> None:
        self.assertEqual(len(AGENT_CATALOGUE), 61)

    def test_ids_unicos(self) -> None:
        ids = [t[0] for t in AGENT_CATALOGUE]
        self.assertEqual(len(ids), len(set(ids)))

    def test_nombres_unicos(self) -> None:
        names = [t[1] for t in AGENT_CATALOGUE]
        self.assertEqual(len(names), len(set(names)))

    def test_tryonyouagent_es_primero(self) -> None:
        self.assertEqual(AGENT_CATALOGUE[0][1], "tryonyouagent")

    def test_agent70_presente(self) -> None:
        names = [t[1] for t in AGENT_CATALOGUE]
        self.assertIn("agent70", names)

    def test_jules_presente(self) -> None:
        names = [t[1] for t in AGENT_CATALOGUE]
        self.assertIn("jules", names)

    def test_gemini_presente(self) -> None:
        names = [t[1] for t in AGENT_CATALOGUE]
        self.assertIn("gemini", names)

    def test_mesa_de_los_listos_presente(self) -> None:
        names = [t[1] for t in AGENT_CATALOGUE]
        self.assertIn("mesa_de_los_listos", names)


class TestMesaDeLosListos(unittest.TestCase):
    def setUp(self) -> None:
        self.mesa = MesaDeLosListos()

    def test_generar_idea(self) -> None:
        idea = self.mesa.generar_idea("test_origen", "contenido de prueba")
        self.assertEqual(idea["origen"], "test_origen")
        self.assertEqual(idea["contenido"], "contenido de prueba")
        self.assertEqual(idea["id"], 1)
        self.assertIn("timestamp", idea)

    def test_ideas_acumulan(self) -> None:
        self.mesa.generar_idea("a", "idea1")
        self.mesa.generar_idea("b", "idea2")
        self.assertEqual(len(self.mesa.ideas), 2)
        self.assertEqual(self.mesa.ideas[1]["id"], 2)

    def test_responder_a_gemini(self) -> None:
        resp = self.mesa.responder_a_gemini(
            pregunta="¿Estado del sistema?",
            via_agent70="Validación IP OK",
            via_jules="Finanzas BPI activas",
        )
        self.assertEqual(resp["destinatario"], "gemini")
        self.assertEqual(resp["coordinador"], "tryonyouagent")
        self.assertIn("respuesta_agent70", resp)
        self.assertIn("respuesta_jules", resp)
        self.assertIn("patent", resp)

    def test_sesion_decisiones_estructura(self) -> None:
        agents_summary = [
            {"status": "done"},
            {"status": "done"},
            {"status": "error"},
            {"status": "idle"},
        ]
        decision = self.mesa.sesion_decisiones(agents_summary)
        self.assertIn("decisiones", decision)
        self.assertIn("comercial", decision["decisiones"])
        self.assertIn("tecnica", decision["decisiones"])
        self.assertIn("resumen_agentes", decision)
        self.assertEqual(decision["resumen_agentes"]["total"], 4)
        self.assertEqual(decision["resumen_agentes"]["completados"], 2)
        self.assertEqual(decision["resumen_agentes"]["con_error"], 1)

    def test_sesion_genera_idea_gemini(self) -> None:
        self.mesa.sesion_decisiones([{"status": "done"}])
        self.assertGreater(len(self.mesa.ideas), 0)


class TestAgentePerfectoOrquestador(unittest.TestCase):
    def setUp(self) -> None:
        self.orq = AgentePerfectoOrquestador()

    def test_61_agentes_registrados(self) -> None:
        self.assertEqual(len(self.orq.agents), 61)

    def test_todos_inician_idle(self) -> None:
        for rec in self.orq.agents.values():
            self.assertEqual(rec.status, AgentStatus.IDLE)

    def test_snapshot_inicial(self) -> None:
        snap = self.orq.get_status_snapshot()
        self.assertEqual(snap["total_agents"], 61)
        self.assertEqual(snap["completados"], 0)
        self.assertEqual(snap["running"], 0)
        self.assertIn("patent", snap)

    def test_orquestar_todos_completa(self) -> None:
        resultado = asyncio.run(self.orq.orquestar_todos())
        self.assertIn("agents", resultado)
        self.assertEqual(len(resultado["agents"]), 61)
        done = sum(1 for a in resultado["agents"] if a["status"] == "done")
        self.assertEqual(done, 61)

    def test_orquestar_genera_mesa_decision(self) -> None:
        resultado = asyncio.run(self.orq.orquestar_todos())
        self.assertIn("mesa_decision", resultado)
        md = resultado["mesa_decision"]
        self.assertIn("decisiones", md)
        self.assertIn("resumen_agentes", md)
        self.assertEqual(md["resumen_agentes"]["completados"], 61)

    def test_orquestar_genera_respuesta_gemini(self) -> None:
        resultado = asyncio.run(self.orq.orquestar_todos())
        self.assertIn("gemini_response", resultado)
        gr = resultado["gemini_response"]
        self.assertEqual(gr["destinatario"], "gemini")
        self.assertEqual(gr["coordinador"], "tryonyouagent")
        self.assertIn("respuesta_agent70", gr)
        self.assertIn("respuesta_jules", gr)

    def test_snapshot_post_orquestacion(self) -> None:
        asyncio.run(self.orq.orquestar_todos())
        snap = self.orq.get_status_snapshot()
        self.assertEqual(snap["completados"], 61)
        self.assertEqual(snap["errores"], 0)


if __name__ == "__main__":
    unittest.main()
