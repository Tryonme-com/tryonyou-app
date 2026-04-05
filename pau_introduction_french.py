"""
Sincronización de Identidad V10.2: El Saludo de Pau en Lafayette.
Traducción al francés con el alma de Eric y la energía de Rubén.

PCT/EP2025/067317 · SIREN 943 610 196
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations


class PauIntroductionFrench:
    """
    Sincronización de Identidad V10.2: El Saludo de Pau en Lafayette.
    Traducción al francés con el alma de Eric y la energía de Rubén.
    """

    def __init__(self):
        """Inicializa los atributos de identidad, ubicación y tono de Pau."""
        self.identity = "P.A.U."
        self.location = "Galeries Lafayette Haussmann"
        self.tone = "Raffiné et Chaleureux"

    def deliver_welcome(self) -> str:
        """Devuelve el guion de bienvenida en francés, formateado para el espejo digital."""
        # El guion exacto que Pau recita al salir de su moneda
        script = {
            "salutation": "Bonjour ! Comment allez-vous ?",
            "presentation": "Moi, c'est Pau.",
            "question": "Et vous, comment vous appelez-vous ?",
            "connection": "Enchanté de faire votre connaissance.",
            "mission": (
                "Je suis votre nouvel ami, votre personal shopper. "
                "Je vais m'occuper de faire briller votre personnalité "
                "en tenant compte de vos goûts et en vous aidant à choisir "
                "les meilleurs looks."
            ),
            "energy_closing": "C'est parti ! Boom ! Vivido !",
        }

        return self._format_for_display(script)

    def _format_for_display(self, data: dict) -> str:
        """Estructura el diccionario del guion como texto multi-línea para la interfaz del espejo digital."""
        # Estructura visual para la interfaz del espejo digital
        return (
            f"{data['salutation']}\n"
            f"{data['presentation']} {data['question']}\n\n"
            f"{data['connection']}\n"
            f"{data['mission']}\n\n"
            f"{data['energy_closing']}"
        )


if __name__ == "__main__":
    pau_fr = PauIntroductionFrench()
    # Ejecución del primer contacto en el Mirror
    print(pau_fr.deliver_welcome())
