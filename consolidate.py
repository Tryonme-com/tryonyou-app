consolidate.py
import pandas as pd
from datetime import datetime

def process_leads(input_file):
    # Cargar datos
    df = pd.read_csv(input_file)
    
    # Configurar fechas
    today = datetime(2026, 4, 20)
    df['Next_Action_Date'] = pd.to_datetime(df['Next_Action_Date'])
    
    # Calcular retraso real (103 días al 20/04/2026)
    df['Real_Delay_Days'] = (today - df['Next_Action_Date']).dt.days
    
    # Marcar Gaps de Información
    df['Data_Gap'] = df['Email'].isna() | (df['Email'] == '')
    
    # Clasificar para acción
    ready_for_outreach = df[~df['Data_Gap']].copy()
    blocked_leads = df[df['Data_Gap']].copy()
    
    # Exportar resultados
    ready_for_outreach.to_csv('ready_to_contact.csv', index=False)
    blocked_leads.to_csv('missing_info_report.csv', index=False)
    
    print(f"--- PROCESO COMPLETADO ---")
    print(f"Total Leads: {len(df)}")
    print(f"Listos para contactar: {len(ready_for_outreach)}")
    print(f"Bloqueados (sin email): {len(blocked_leads)}")
    print(f"Retraso detectado: {df['Real_Delay_Days'].iloc[0]} días.")

if __name__ == "__main__":
    process_leads('leads_raw.csv')
    