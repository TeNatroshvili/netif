# ------------------------------------------
# interface to the Scraping for 1810 Switch
# ------------------------------------------
# author:   Natroshvili Teimuraz
# created:  2023-03-07
# version:  1.4
# ------------------------------------------
from influxdb import InfluxDBClient
import pandas as pd
from datetime import datetime
from fpdf import FPDF, YPos
from datetime import datetime, timedelta
import os

from samba import upload as uploadPDF



#hosts angeben
hosts = ['N304', 'N306', 'N307', 'N310', 'N312', 'N313',
         'N314', 'N315', 'N316', 'N317', 'N318', 'N319']

#Schulstunden in den richtigen format definieren
now = datetime.now() - timedelta(days=2)
time0 = now.replace(hour=7, minute=50, second=0, microsecond=0)
stunde0 = time0.strftime('%Y-%m-%dT%H:%M:%SZ')
time1 = now.replace(hour=8, minute=40, second=0, microsecond=0)
stunde1 = time1.strftime('%Y-%m-%dT%H:%M:%SZ')
time2 = now.replace(hour=9, minute=30, second=0, microsecond=0)
stunde2 = time2.strftime('%Y-%m-%dT%H:%M:%SZ')
time3 = now.replace(hour=10, minute=30, second=0, microsecond=0)
stunde3 = time3.strftime('%Y-%m-%dT%H:%M:%SZ')
time4 = now.replace(hour=11, minute=20, second=0, microsecond=0)
stunde4 = time4.strftime('%Y-%m-%dT%H:%M:%SZ')
time5 = now.replace(hour=12, minute=10, second=0, microsecond=0)
stunde5 = time5.strftime('%Y-%m-%dT%H:%M:%SZ')
time6 = now.replace(hour=13, minute=10, second=0, microsecond=0)
stunde6 = time6.strftime('%Y-%m-%dT%H:%M:%SZ')
time7 = now.replace(hour=14, minute=00, second=0, microsecond=0)
stunde7 = time7.strftime('%Y-%m-%dT%H:%M:%SZ')
time8 = now.replace(hour=14, minute=50, second=0, microsecond=0)
stunde8 = time8.strftime('%Y-%m-%dT%H:%M:%SZ')
time9 = now.replace(hour=15, minute=50, second=0, microsecond=0)
stunde9 = time9.strftime('%Y-%m-%dT%H:%M:%SZ')
time10 = now.replace(hour=16, minute=40, second=0, microsecond=0)
stunde10 = time10.strftime('%Y-%m-%dT%H:%M:%SZ')

#Ein string mit alle Schulstunden
stunden = [stunde10, stunde9, stunde8, stunde7, stunde6, stunde5, stunde4, stunde3, stunde2, stunde1, stunde0]

#Funktion zum PDF generieren
def generate_pdf_table(result_list_download, result_list_upload, new_col):

    for file in os.listdir('./reports'):
        if (str(file).endswith(".gitkeep") != True):
            os.remove(os.path.join('./reports', file))

    pdf = FPDF()
    pdf.add_page()

   
    #Überschrift
    s2 = now.strftime("%d.%m.%Y")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, ' Datum: ' + s2, 0, 1)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Download', 0, 1, 'C')
    #Tabellenüberschrifte
    pdf.cell(15, 10, 'Host', border=1)
    #pdf.cell(50, 10, 'Time', border=1)

    for i in range(10):
        pdf.cell(18, 10, str(i+1), border=1)
    

    pdf.ln()
    j=-1
    pdf.set_font('Arial', '', 12)
    for sublist2 in new_col.values[0][0]:
        pdf.cell(15, 10, str(sublist2), border=1)
        j+=1
       
        for i in range(len(stunden)-1):
            if(j<len(result_list_download[i][0])) and i != 7: # TODO in 8 school hour there is an error with the substraction so negative numbers occur
                pdf.cell(18, 10, str(result_list_download[i][0][j]), border=1)
            else:
                pdf.cell(18, 10, "-", border=1)

        pdf.ln()

    pdf.set_font('Arial', '', 11)
    pdf.cell(w=106, h=10,txt= ' Angaben in MB', align='R')
    pdf.add_page()

    #Überschrift
    s2 = now.strftime("%d.%m.%Y")
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, 'Datum: ' + s2, 0, 1)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Upload', 0, 1, 'C')
    #Tabellenüberschrifte
    pdf.cell(15, 10, 'Host', border=1)
    #pdf.cell(50, 10, 'Time', border=1)

    for i in range(10):
        pdf.cell(18, 10, str(i+1), border=1)
    

    pdf.ln()
    j=-1
    pdf.set_font('Arial', '', 12)
    for sublist2 in new_col.values[0][0]:
        pdf.cell(15, 10, str(sublist2), border=1)
        j+=1
       
        for i in range(len(stunden)-1):
            if(j<len(result_list_upload[i][0])) and i != 7: # TODO in 8 school hour there is an error with the substraction so negative numbers occur
                pdf.cell(18, 10, str(result_list_upload[i][0][j]), border=1)
            else:
                pdf.cell(18, 10, "-", border=1)

        pdf.ln()

    pdf.set_font('Arial', '', 11)
    pdf.cell(w=106, h=10,txt= ' Angaben in MB', align='R')
    s3 = now.strftime("%d-%m-%Y")
    filename = 'DailyReport_' + s3 + '.pdf'
    #PDF Namen zuteilen
    pdf.output('reports/'+filename)

    return filename


#Funktion zum RX (Download) daten abholen
def getBaseRX(hosts, base_str):

    client = None
    try:
        #Datenbank client für die Datanbankverbindung
        client = InfluxDBClient(host="10.128.10.7", port=8086, username="syp",
                            password="Syp2022", timeout=2, database="collectd")

        results = []
        #for loop um hosts durchzugehen
        for host in hosts:
            #query zum abholen der Daten von snmp_rx mit richtigen host und zeit
            query = f'SELECT FIRST(value) FROM "snmp_rx" WHERE ("host" = \'{host}\' AND "type" = \'if_octets\' AND "type_instance" = \'traffic25 Gigabit - Level\') AND time >= \'{base_str}\' - 20s fill(null)'
            result = client.query(query)
        
            if(len(result)==0):
                query = f'SELECT FIRST(value) FROM "snmp_rx" WHERE ("host" = \'{host}\' AND "type" = \'if_octets\' AND "type_instance" = \'trafficPort: 25 SFP - Level\') AND time >= \'{base_str}\' - 20s fill(null)'
                result = client.query(query)
            #erhaltene Daten speichern
            points = list(result.get_points())
            #Datenüberprüfung
            if points:
                points[0]['host'] = host
                results.append(points[0])
    finally:
        client.close()

    #Daten in richtigen format speichern
    df = pd.DataFrame(results)
    df['time'] = pd.to_datetime(df['time'], utc=True)
    df = df.set_index(['host', 'time']).sort_index()
    return df


#Funktion zum TX (Upload Daten Abholen)
def getBaseTX(hosts, base_str):

    client = None
    try:
        #Datenbank client für die Datanbankverbindung
        client = InfluxDBClient(host="10.128.10.7", port=8086, username="syp",
                            password="Syp2022", timeout=2, database="collectd")
        results = []
        #for loop um hosts durchzugehen
        for host in hosts:
            #query zum abholen der Daten von snmp_tx mit richtigen host und zeit
            query = f'SELECT FIRST(value) FROM "snmp_tx" WHERE ("host" = \'{host}\' AND "type" = \'if_octets\' AND "type_instance" = \'traffic25 Gigabit - Level\') AND time >= \'{base_str}\' - 20s fill(null)'
            result = client.query(query)
            
            if(len(result)==0):
                query = f'SELECT FIRST(value) FROM "snmp_rx" WHERE ("host" = \'{host}\' AND "type" = \'if_octets\' AND "type_instance" = \'trafficPort: 25 SFP - Level\') AND time >= \'{base_str}\' - 20s fill(null)'
                result = client.query(query)
            #erhaltene Daten speichern
            points = list(result.get_points())
            #Datenüberprüfung
            if points:
                points[0]['host'] = host
                results.append(points[0])
    finally:
        client.close()

    #Daten in richtigen format speichern
    df = pd.DataFrame(results)
    df['time'] = pd.to_datetime(df['time'], utc=True)
    df = df.set_index(['host', 'time']).sort_index()
    return df

#Zwischensumme für die Berechnung von stündlichen Daten
subtractor = []

#Endergebnis
download = []

#Download Datenverarbeitung
#For Loop für die Schulstunden
for stunde in stunden:
    #RX (Download) Dataframe
    RXdf = getBaseRX(hosts=hosts, base_str=stunde)
    #Extrahieren von value der Dataframe
    values = pd.DataFrame(RXdf['first'].values)
    hostiterate = RXdf.index.get_level_values(0)
    index_values = hostiterate.tolist()
    #Checken ob Subtractor schon erhalten worden ist wenn nicht wird der Subtractor gespeichert
    if len(subtractor)==0:
        subtractor = values
    else:
        #von kb auf mb umrechnen und runden
        intersum = (subtractor - values)//1000000
        #datetime format angemessen extrahieren
        dt_object = datetime.fromisoformat(stunde[:-1])            
        new_col = pd.DataFrame({'time': [dt_object]*len(intersum)})
        #datetime zum values dazugeben
        intersum = pd.concat([intersum, new_col], axis=1)
        #zwischensumme zu der aktuellen df hinzufügen
        download.append(intersum)
    subtractor = values

#Variablen Resetten
upload = []
new_col = []
subtractor = []

#Upload Datenverarvbeitung
#For Loop für die Schulstunden
for stunde in stunden:
    TXdf = getBaseTX(hosts=hosts, base_str=stunde)
    values = pd.DataFrame(TXdf['first'].values)
    hostiterate = TXdf.index.get_level_values(0)
    index_values = hostiterate.tolist()
    #Checken ob Subtractor schon erhalten worden ist wenn nicht wird der Subtractor gespeichert
    if len(subtractor)==0:
        subtractor = values
    else:
        #von kb auf mb umrechnen und runden
        intersum = (subtractor - values)//1000000
        #datetime format angemessen extrahieren
        dt_object = datetime.fromisoformat(stunde[:-1])            
        new_col = pd.DataFrame({'time': [dt_object]*len(intersum)})
        #datetime zum values dazugeben
        intersum = pd.concat([intersum, new_col], axis=1)
        #zwischensumme zu der aktuellen df hinzufügen
        upload.append(intersum)
    #subtractor auf values setzen
    subtractor = values

#hosts im richtigen format übertragen
new_col = pd.DataFrame({'host': [index_values]})

#PDF generierungs Funktion aufrufen für TX und RX (Upload und Download)
uploadPDF(generate_pdf_table(result_list_download=download, result_list_upload=upload, new_col=new_col))