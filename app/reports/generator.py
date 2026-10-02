import json
import csv
from app.database.crud import get_incidents

def generate_json_report(incident_id=None):
    incidents = get_incidents(limit=100)
    if incident_id:
        incidents = [i for i in incidents if i['id'] == incident_id]
    with open('report.json', 'w') as f:
        json.dump(incidents, f, indent=2)
    return 'report.json'

def generate_csv_report(incident_id=None):
    incidents = get_incidents(limit=100)
    if incident_id:
        incidents = [i for i in incidents if i['id'] == incident_id]
    with open('report.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'score', 'level', 'timestamp', 'affected_files', 'suspect_process'])
        for inc in incidents:
            writer.writerow([
                inc['id'], inc['score'], inc['level'], inc['timestamp'],
                json.dumps(inc['affected_files']), json.dumps(inc['suspect_process'])
            ])
    return 'report.csv'
