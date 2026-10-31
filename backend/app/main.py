from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.upload_routes import router as upload_router
from app.api.routes.diagnosis_routes import router as diagnosis_router
from app.api.routes.auth_routes import router as auth_router

app = FastAPI(title="NetCoop API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(diagnosis_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "service": "netcoop-api"}
