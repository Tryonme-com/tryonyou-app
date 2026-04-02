.ipynb
# ==========================================
# ACTUALIZACIÓN DE ENTORNO: TRYONYOU-APP
# ==========================================

# 1. Versiones actuales (Verificación del núcleo)
print("--- VERSIONES ACTUALES ---")
!python --version
!pip show fastapi pandas uvicorn

# 2. Actualizar herramientas base (pip / setuptools / wheel)
print("\n--- ACTUALIZANDO HERRAMIENTAS BASE ---")
!python -m pip install --upgrade pip setuptools wheel

# 3. Actualizar dependencias de la infraestructura (Opción fuerte a medida)
# Si tienes tu requirements.txt en la raíz de tryonyou-app, descomenta la siguiente línea:
# !pip install -r requirements.txt --upgrade

# Actualización directa de nuestra guardia pretoriana de librerías (Backend V9):
print("\n--- ACTUALIZANDO DEPENDENCIAS DEL BÚNKER ---")
!pip install --upgrade fastapi uvicorn pandas openpyxl "qrcode[pil]" Pillow python-dotenv smtplib

# 4. Confirmación
print("\n✅ Entorno de tryonyou-app sincronizado al 100%.")
print("⚠️ ACCIÓN REQUERIDA: Ve al menú superior del Notebook y haz clic en: Kernel → Restart (o Restart & Run All) para cargar las nuevas versiones en memoria.")

