from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from uuid import uuid4
import csv, io, json
from app.services.file_validation_service import validate_telemetry_file
from app.orchestration.diagnosis_orchestrator import run_diagnosis
from app.api.routes.auth_routes import current_user
from app.services.report_history_service import save_report, list_reports, get_report

router = APIRouter(tags=['Diagnosis'])


def _records(filename: str, content: bytes):
    text = content.decode('utf-8-sig')
    if filename.lower().endswith('.json'):
        parsed = json.loads(text)
        return parsed if isinstance(parsed, list) else [parsed]
    return list(csv.DictReader(io.StringIO(text)))


@router.post('/diagnosis/start')
async def start_diagnosis(file: UploadFile = File(...), scenario: str = Form('Auto-detect from file'), user=Depends(current_user)):
    content = await file.read()
    filename = file.filename or 'telemetry.csv'
    try:
        validation = validate_telemetry_file(filename, content)
        records = _records(filename, content)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    incident_id = f'INC-{uuid4().hex[:8].upper()}'
    report = run_diagnosis(records, incident_id, filename, scenario)
    report['requested_by'] = user['email']
    save_report(user['id'], report)
    return report


@router.get('/reports')
def reports_history(user=Depends(current_user)):
    return {"reports": list_reports(user["id"])}

@router.get('/reports/{incident_id}')
def report_detail(incident_id: str, user=Depends(current_user)):
    report = get_report(user["id"], incident_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report
