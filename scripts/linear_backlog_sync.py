from __future__ import annotations

import os
from typing import Any

import requests

LINEAR_API_KEY = os.environ.get("LINEAR_API_KEY", "").strip()
PROJECT_ID = os.environ.get("LINEAR_PROJECT_ID", "").strip()
TEAM_ID = os.environ.get("LINEAR_TEAM_ID", "").strip()

URL_API = "https://api.linear.app/graphql"

BACKLOG_TASKS: list[dict[str, Any]] = [
    {
        "title": "[TEC-01] Encriptación Biométrica End-to-End (Privacy Firewall)",
        "description": "Implementar cifrado AES-256 para los datos de silueta mapeados en tránsito y reposo. Forzar la destrucción absoluta de datos biométricos brutos post-escaneo en la API Serverless, persistiendo únicamente el identificador único de elasticidad.",
        "priority": 1,
        "labels": ["Infraestructura", "Seguridad", "RGPD"],
    },
    {
        "title": "[TEC-02] Balanceo de Carga para Renderizado de Capas Visuales",
        "description": "Configurar nodos dedicados y optimizar rutas de renderizado en Vercel Edge Network para evitar latencias en el cambio de look ('snap'). Garantizar estabilidad operativa del z-index de la interfaz de usuario.",
        "priority": 2,
        "labels": ["Infraestructura", "DevOps"],
    },
    {
        "title": "[TEC-03] API Gateway unificada para Inventarios Externos de Lujo",
        "description": "Desplegar la capa de abstracción para conectar los inventarios en tiempo real de marcas asociadas (Dior, Balmain, Burberry) mediante la Shopify Admin API (Agente 26).",
        "priority": 1,
        "labels": ["Infraestructura", "Integraciones"],
    },
    {
        "title": "[TEC-04] Logs de Auditoría y Trazabilidad GDPR Inmutable",
        "description": "Desarrollar el registro estricto e inalterable de accesos a datos sensibles dentro del módulo 'Private Management' para auditorías de cumplimiento institucional ante la Chambre de Commerce.",
        "priority": 3,
        "labels": ["Seguridad", "Cumplimiento"],
    },
    {
        "title": "[ALG-05] Calibración de Visión Inteligente en Tiempo Real",
        "description": "Optimizar el ajuste dinámico del canvas overlay según las condiciones de iluminación de la cabina física. Sincronizar MediaPipe Pose utilizando los 33 landmarks corporales clave.",
        "priority": 1,
        "labels": ["Algoritmo", "ComputerVision"],
    },
    {
        "title": "[ALG-06] Motor de Sugerencia Adaptativa de Estilismo Absoluto",
        "description": "Desplegar la lógica de recomendación en la unidad PAU basándose en la intención de uso ('Occasion') y la sensación de caída física ('Feeling'), presentando el conjunto estético completo y terminado.",
        "priority": 2,
        "labels": ["AI-PersonalShopper", "UX"],
    },
    {
        "title": "[ALG-07] Shader Visual 'Snap' para Transición Estilizada",
        "description": "Desarrollar un efecto de partículas mediante shaders GPU y transiciones fluidas con Framer Motion en el Virtual Mirror al alternar entre colecciones.",
        "priority": 3,
        "labels": ["Frontend", "UX"],
    },
    {
        "title": "[ALG-08] Algoritmo de Detección de Colisiones 3D Textil",
        "description": "Evitar el clipping o solapamiento de la prenda virtual adaptada sobre la silueta del gemelo digital. Integrar lógica matemática predictiva para la caída del tejido según el coeficiente de elasticidad.",
        "priority": 2,
        "labels": ["Algoritmo", "ComputerVision"],
    },
    {
        "title": "[OPS-09] Webhook de Reserva de Probador Físico (O2O Core)",
        "description": "Desarrollar el disparador instantáneo que conecte la sesión digital del probador virtual con el staff de la tienda física de Galeries Lafayette mediante un código QR único.",
        "priority": 1,
        "labels": ["Operaciones", "Integraciones"],
    },
    {
        "title": "[OPS-10] Dashboard de Conversión en Tiempo Real",
        "description": "Estructurar las métricas clave de analítica: Escaneos vs Reservas de cabina vs Ventas efectivas para demostrar la reducción del 85% en la tasa de retornos.",
        "priority": 1,
        "labels": ["Operaciones", "Analítica"],
    },
    {
        "title": "[OPS-11] Pipeline de Exportación Multimedia Social-Ready",
        "description": "Permitir la exportación directa de capturas de looks adaptados para redes sociales purgando automáticamente metadatos técnicos sensibles.",
        "priority": 2,
        "labels": ["Operaciones", "Frontend"],
    },
    {
        "title": "[OPS-12] Mapping Inteligente de Tallas Invisibles",
        "description": "Consolidar el motor de traducción interno que convierte la métrica de elasticidad biométrica pura a las dimensiones reales de los patrones del taller de costura sin revelar tallas comerciales (S, M, L).",
        "priority": 1,
        "labels": ["Algoritmo", "Operaciones"],
    },
    {
        "title": "[SYS-13] Modo Offline Controlado para Espejos Digitales",
        "description": "Establecer una caché local de emergencia para permitir escaneos biométricos básicos y almacenamiento diferido de leads en caso de caída de la red local de la tienda.",
        "priority": 3,
        "labels": ["Sistemas", "Arquitectura"],
    },
    {
        "title": "[SYS-14] Optimización de Rendimiento de Renderizado (60 FPS)",
        "description": "Saneamiento de código del canvas en React 18.3.1 + Vite 7.1.2 para asegurar que el procesamiento de MediaPipe Pose mantenga un refresco estable en dispositivos locales.",
        "priority": 2,
        "labels": ["Frontend", "Optimización"],
    },
    {
        "title": "[SYS-15] Stress Test de Concurrencia en Red de Tienda",
        "description": "Simular peticiones concurrentes y balanceo de carga para un despliegue de hasta 50 espejos biométricos paralelos procesando flujos de datos hacia el Agente Jules V7.",
        "priority": 2,
        "labels": ["Sistemas", "QA"],
    },
    {
        "title": "[SYS-16] Core SDK para Integración Simplificada de Marcas",
        "description": "Crear el pipeline estandarizado de ingesta para que los equipos de diseño de las marcas de lujo puedan mapear sus prendas directamente en el catálogo digital.",
        "priority": 3,
        "labels": ["Arquitectura", "Integraciones"],
    },
    {
        "title": "[QA-17] Validación del Sesgo Algorítmico de Silueta",
        "description": "Realizar pruebas de control masivas para asegurar una precisión técnica superior al 99.7% en todo tipo de complexiones, alturas y morfologías físicas.",
        "priority": 1,
        "labels": ["QA", "Algoritmo"],
    },
    {
        "title": "[QA-18] Módulo de Micro-feedback Post-Experiencia",
        "description": "Integrar un sistema de valoración instantáneo cualitativo en la pantalla final para medir el incremento del confort psicológico del usuario y la mitigación del trauma de tallas.",
        "priority": 3,
        "labels": ["QA", "UX"],
    },
    {
        "title": "[QA-19] Pruebas de Latencia Extrema en Edge API",
        "description": "Verificar y auditar mediante scripts automatizados que el tiempo de respuesta crítico de la capa `/api` se mantenga de forma homogénea en t < 22 ms.",
        "priority": 1,
        "labels": ["QA", "Sistemas"],
    },
    {
        "title": "[QA-20] Sistema de Alertas Automatizado (Health Monitor)",
        "description": "Configurar flujos de trabajo en GitHub Actions para monitorizar el uptime total de `tryonyou.app` y despachar alertas SMTP inmediatas en caso de anomalías en producción.",
        "priority": 2,
        "labels": ["Sistemas", "DevOps"],
    },
]


CREATE_ISSUE_MUTATION = """
mutation CreateIssue(
  $teamId: String!,
  $projectId: String!,
  $title: String!,
  $description: String!,
  $priority: Int!
) {
  issueCreate(input: {
    teamId: $teamId,
    projectId: $projectId,
    title: $title,
    description: $description,
    priority: $priority
  }) {
    success
    issue {
      id
      url
    }
  }
}
"""


def _auth_header(token: str) -> str:
    return token if token.startswith("Bearer ") else "Bearer " + token.strip()


def _required_env(name: str, value: str) -> str:
    if value:
        return value
    raise ValueError(f"Missing required environment variable: {name}")


def _description_with_labels(task: dict[str, Any]) -> str:
    labels = task.get("labels") or []
    if not labels:
        return str(task["description"])
    return f"{task['description']}\n\nSuggested labels: {', '.join(labels)}"


def create_linear_issue(task: dict[str, Any], *, team_id: str, project_id: str, api_key: str) -> bool:
    variables = {
        "teamId": team_id,
        "projectId": project_id,
        "title": task["title"],
        "description": _description_with_labels(task),
        "priority": int(task["priority"]),
    }

    response = requests.post(
        URL_API,
        json={"query": CREATE_ISSUE_MUTATION, "variables": variables},
        headers={
            "Authorization": _auth_header(api_key),
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        print(f"💥 Network error while creating {task['title']}: {response.status_code}")
        return False

    result = response.json()
    if "errors" in result:
        error_messages = [str(err.get("message", "Unknown error")) for err in result["errors"] if isinstance(err, dict)]
        joined_errors = " | ".join(error_messages) if error_messages else "Unknown error"
        print(f"❌ Error in {task['title']}: {joined_errors}")
        return False

    issue_data = result["data"]["issueCreate"]["issue"]
    print(f"✅ Created: {task['title']} -> {issue_data['url']}")
    return True


def main() -> int:
    try:
        api_key = _required_env("LINEAR_API_KEY", LINEAR_API_KEY)
        project_id = _required_env("LINEAR_PROJECT_ID", PROJECT_ID)
        team_id = _required_env("LINEAR_TEAM_ID", TEAM_ID)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1

    print("🚀 Starting V10 backlog sync to Linear...")
    success_count = 0
    failure_count = 0
    for task in BACKLOG_TASKS:
        if create_linear_issue(task, team_id=team_id, project_id=project_id, api_key=api_key):
            success_count += 1
        else:
            failure_count += 1

    print(f"🎉 Sync completed. Success: {success_count} | Failed: {failure_count}")
    return 1 if failure_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
