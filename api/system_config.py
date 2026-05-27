from __future__ import annotations


class SystemConfig:
    def __init__(self):
        self.PROTOCOL = "OMEGA_V10.2"
        self.LATENCY_TARGET_MS = 21.8
        self.BIOMETRIC_PRECISION = 0.9982
        self.UI_THEME = {"PRIMARY": "#D4AF37", "SECONDARY": "#F5F5F5"}
        self.SENSOR_MODE = "EMPIRE"


config = SystemConfig()
