{
  "memory_note": "bunker_sovereignty",
  "title": "Supercommit_Max y Dossier Fatality",
  "project": "TryOnYou / Espejo Digital Soberano",
  "owner": "Rubén Espinar Rodríguez",
  "patent": "PCT/EP2025/067317",
  "siret": "94361019600017",
  "operational_points": [
    "Supercommit_Max sincroniza nodo 75011 (Oberkampf) con la galería web en la rama actual.",
    "Cada éxito operativo se reporta vía @tryonyou_deploy_bot usando token en variable de entorno.",
    "Seguridad: martes 08:00 (Europe/Paris), confirmar >=450000 EUR y activar Dossier Fatality.",
    "No exponer secretos; usar variables de entorno y notificación segura."
  ],
  "scripts": {
    "supercommit_max": "supercommit_max.sh",
    "deploy_notifier": "scripts/notify_tryonyou_deploy_bot.py",
    "fatality_guard": "scripts/fatality_tuesday_guard.py"
  }
}
