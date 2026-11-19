from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.analyzer import SmartContractAnalyzer


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PROJECT_DIR = BASE_DIR.parent
SAMPLES_DIR = PROJECT_DIR / "samples"

app = FastAPI(
    title="SmartGuard",
    description="Prototipo académico para el análisis heurístico de contratos inteligentes Solidity.",
    version="0.2.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
analyzer = SmartContractAnalyzer()


class AnalyzeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=250_000)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": app.version, "rules": len(analyzer.get_rules())}


@app.get("/api/rules")
def rules():
    return {"total": len(analyzer.get_rules()), "rules": analyzer.get_rules()}


@app.get("/api/sample/{sample_name}", response_class=PlainTextResponse)
def sample(sample_name: str):
    allowed = {"vulnerable": "vulnerable.sol", "safer": "safer.sol"}
    file_name = allowed.get(sample_name)
    if not file_name:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    return (SAMPLES_DIR / file_name).read_text(encoding="utf-8")


@app.post("/api/analyze")
def analyze_contract(payload: AnalyzeRequest):
    findings = analyzer.analyze(payload.code)
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for finding in findings:
        severity = finding.get("severity")
        if severity in counts:
            counts[severity] += 1

    if counts["HIGH"]:
        review_level = "Revisión prioritaria"
    elif counts["MEDIUM"]:
        review_level = "Revisión recomendada"
    elif counts["LOW"]:
        review_level = "Observaciones menores"
    else:
        review_level = "Sin patrones configurados detectados"

    return {
        "version": app.version,
        "total_findings": len(findings),
        "severity_counts": counts,
        "review_level": review_level,
        "findings": findings,
        "disclaimer": (
            "SmartGuard es un prototipo educativo. Un hallazgo no confirma una vulnerabilidad "
            "explotable y la ausencia de hallazgos no garantiza que el contrato sea seguro."
        ),
    }
