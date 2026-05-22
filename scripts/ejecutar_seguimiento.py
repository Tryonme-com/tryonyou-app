import os, csv, time, base64
from datetime import datetime
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CSV_FILE = 'contactos_seguimiento.csv'

def enviar_correo(servicio, to, subject, body):
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['to'], msg['subject'] = to, subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
        servicio.users().messages().send(userId='me', body={'raw': raw}).execute()
        return True
    except Exception as e:
        print(f"Error con {to}: {e}")
        return False

if __name__ == '__main__':
    creds = Credentials.from_authorized_user_file('token.json', SCOPES) if os.path.exists('token.json') else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
        else: creds = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES).run_local_server(port=0)
        with open('token.json', 'w') as t: t.write(creds.to_json())
    
    srv = build('gmail', 'v1', credentials=creds)
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        filas = list(csv.DictReader(f))
    
    for fila in filas:
        if fila['Status'] == 'Pending reply' and fila['Email']:
            saludo = fila['Contact Name'] if fila['Contact Name'] != 'General' else "Team"
            cuerpo = f"Hello {saludo},\n\nI am following up on the innovation proposal previously transmitted regarding our high-performance systems and international patent architecture.\n\nBest regards,\nSystems Architecture"
            print(f"Enviando a {fila['Institution']}...")
            if enviar_correo(srv, fila['Email'], f"Follow-up: Innovation Proposal - {fila['Institution']}", cuerpo):
                fila['Status'], fila['Next Action'], fila['Last Action Date'] = 'Followed up', 'Awaiting reply', datetime.now().strftime('%Y-%m-%d')
                time.sleep(10)
                
    with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)
    print("Completado.")
