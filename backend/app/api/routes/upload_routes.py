from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.file_validation_service import validate_telemetry_file
from app.api.routes.auth_routes import current_user
router = APIRouter(tags=["Telemetry"])

@router.post("/upload/validate")
async def validate_file(file: UploadFile = File(...), user=Depends(current_user)):
    content = await file.read()
    try:
        result = validate_telemetry_file(file.filename or "", content)
        return {"valid": True, "filename": file.filename, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
