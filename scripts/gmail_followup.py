import os
import csv
import time
import base64
from datetime import datetime
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Alcance de permisos requerido para el envío de correos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
ARCHIVO_CSV = 'contactos_seguimiento.csv'

def inicializar_base_datos():
    """Crea el archivo CSV local con los datos proporcionados si no existe."""
    datos_iniciales = [
        {"Institution": "Big Sur Ventures", "Contact Name": "General", "Email": "info@bigsurventures.vc", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Atlantic Bridge Ventures", "Contact Name": "General", "Email": "info@abven.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Axon Innovation Growth II", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Innvierte Deep-Tech (CDTI/FEI)", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Elaia", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "TRL13", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Inventure", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Voima Ventures", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Jolt Capital", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "OTB Ventures", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "UVC Partners", "Contact Name": "General", "Email": "", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "IP Group", "Contact Name": "Dealflow", "Email": "dealflow@ipgroupplc.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "IQ Capital", "Contact Name": "General", "Email": "hello@iqcapital.vc", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Intellectual Ventures", "Contact Name": "Patent Sales", "Email": "patentsales@intven.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "RPX Corporation", "Contact Name": "Deals", "Email": "mlower@rpxcorp.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Acacia Research", "Contact Name": "IR", "Email": "ir@acaciares.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Fortress Investment Group", "Contact Name": "Opportunities", "Email": "opportunities@fortress.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Alumni Ventures", "Contact Name": "Partnerships", "Email": "partnerships@av.vc", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "Speedinvest Deep Tech", "Contact Name": "Office", "Email": "office@speedinvest.com", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
        {"Institution": "TechAccel", "Contact Name": "Michael Pavia", "Email": "Michael@TechAccel.net", "Status": "Pending reply", "Last Action Date": "", "Next Action": "Follow-up pending", "Offer Sent": "YES", "Notes / Comments": "Initial outreach sent"},
    ]

    if not os.path.exists(ARCHIVO_CSV):
        columnas = ["Institution", "Contact Name", "Email", "Status", "Last Action Date", "Next Action", "Offer Sent", "Notes / Comments"]
        with open(ARCHIVO_CSV, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(datos_iniciales)
        print(f"[+] Base de datos inicializada en {ARCHIVO_CSV}")

def obtener_servicio_gmail():
    """Autentica al usuario y conecta con la API de Gmail utilizando credentials.json."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Error: El archivo 'credentials.json' obligatorio no se encuentra en el directorio.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def enviar_correo(servicio, destinatario, asunto, cuerpo_texto):
    """Estructura y envía el correo electrónico a través de la API."""
    try:
        mensaje = MIMEText(cuerpo_texto, 'plain', 'utf-8')
        mensaje['to'] = destinatario
        mensaje['subject'] = asunto
        raw_mensaje = base64.urlsafe_b64encode(mensaje.as_bytes()).decode('utf-8')

        servicio.users().messages().send(userId='me', body={'raw': raw_mensaje}).execute()
        return True
    except HttpError as error:
        print(f"[-] Error en el envío a {destinatario}: {error}")
        return False

def procesar_lote_seguimiento():
    """Lee el CSV local, procesa los envíos pendientes y actualiza el archivo."""
    inicializar_base_datos()

    try:
        servicio = obtener_servicio_gmail()
    except Exception as e:
        print(f"[-] Error de autenticación: {e}")
        return

    contactos_actualizados = []
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    with open(ARCHIVO_CSV, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        campos = reader.fieldnames
        filas = list(reader)

    print(f"[+] Procesando registros de la lista...")

    for fila in filas:
        # Filtrar contactos que necesitan seguimiento y tienen correo definido
        if fila.get('Status') == 'Pending reply' and fila.get('Next Action') == 'Follow-up pending':
            institucion = fila.get('Institution')
            nombre_contacto = fila.get('Contact Name', '').strip()
            email_destino = fila.get('Email', '').strip()

            if not email_destino:
                print(f"[!] Saltando {institucion}: Sin dirección de correo registrada.")
                contactos_actualizados.append(fila)
                continue

            saludo = nombre_contacto if nombre_contacto and nombre_contacto.lower() != 'general' else "Team"
            asunto_correo = f"Follow-up: Deep-tech / IP Innovation Proposal - {institucion}"

            cuerpo_correo = (
                f"Hello {saludo},\n\n"
                f"I am following up on the innovation proposal previously transmitted regarding our high-performance "
                f"systems and international patent architecture. We are currently consolidating our implementation "
                f"phases and technical validation metrics.\n\n"
                f"Given your focus, we would like to confirm if the documentation has been successfully reviewed "
                f"by your technical evaluation or investment team, or if further specification is required.\n\n"
                f"Best regards,\n"
                f"Systems Architecture & Engineering"
            )

            print(f"[>] Enviando correo a {institucion} ({email_destino})...")
            exito = enviar_correo(servicio, email_destino, asunto_correo, cuerpo_correo)

            if exito:
                fila['Status'] = 'Followed up'
                fila['Last Action Date'] = fecha_hoy
                fila['Next Action'] = 'Awaiting reply'
                print(f"[+] Envío confirmado a {email_destino}")
                time.sleep(30)  # Pausa de seguridad anti-bloqueo
            else:
                print(f"[-] Envío fallido para {email_destino}. Revisión manual requerida.")

        contactos_actualizados.append(fila)

    # Sobrescribir el archivo con los estados modificados
    with open(ARCHIVO_CSV, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=campos)
        writer.writeheader()
        writer.writerows(contactos_actualizados)
    print("[+] Ejecución completada y estados actualizados localmente.")

if __name__ == '__main__':
    procesar_lote_seguimiento()
