from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="API Monitoreo Embalse Arandanos",
    description=(
        "API para exponer lecturas de sensores y respaldo de alertas del dashboard."
    ),
    version="1.0.0",
)


class SensorData(BaseModel):
    value: float
    min: float
    max: float
    safeMax: float
    lastUpdated: datetime
    status: Literal["stable", "warning", "critical"]


class Metadata(BaseModel):
    systemStatus: Literal["operational", "degraded", "down"]
    arduinoConnected: bool
    lastSync: datetime
    uptime: int = Field(..., ge=0, description="Tiempo de actividad en segundos")
    activeSensors: int = Field(..., ge=0)


class DashboardResponse(BaseModel):
    ph: SensorData
    temperature: SensorData
    conductivity: SensorData
    metadata: Metadata


class AlertRecord(BaseModel):
    id: int
    fecha: str
    hora: str
    embalse: str
    sensor: str
    medicion: str


class AlertCreate(BaseModel):
    embalse: str
    sensor: str
    medicion: str


dashboard_state = DashboardResponse(
    ph=SensorData(
        value=7.2,
        min=6.0,
        max=8.5,
        safeMax=8.0,
        lastUpdated=datetime.utcnow(),
        status="stable",
    ),
    temperature=SensorData(
        value=22.5,
        min=5,
        max=35,
        safeMax=28,
        lastUpdated=datetime.utcnow(),
        status="stable",
    ),
    conductivity=SensorData(
        value=650,
        min=100,
        max=2000,
        safeMax=1500,
        lastUpdated=datetime.utcnow(),
        status="stable",
    ),
    metadata=Metadata(
        systemStatus="operational",
        arduinoConnected=True,
        lastSync=datetime.utcnow(),
        uptime=3600,
        activeSensors=3,
    ),
)

alerts_store: list[AlertRecord] = [
    AlertRecord(
        id=1,
        fecha="2026-03-24",
        hora="14:30",
        embalse="Embalse Norte",
        sensor="Conductividad",
        medicion="1.2 mS/cm",
    )
]


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {"message": "API de Monitoreo Embalse Arandanos activa"}


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
def get_dashboard_data() -> DashboardResponse:
    return dashboard_state


@app.get("/api/alerts", response_model=list[AlertRecord], tags=["Alertas"])
def list_alerts() -> list[AlertRecord]:
    return alerts_store


@app.post("/api/alerts", response_model=AlertRecord, status_code=201, tags=["Alertas"])
def create_alert(payload: AlertCreate) -> AlertRecord:
    now = datetime.utcnow()
    new_alert = AlertRecord(
        id=(alerts_store[-1].id + 1) if alerts_store else 1,
        fecha=now.strftime("%Y-%m-%d"),
        hora=now.strftime("%H:%M"),
        embalse=payload.embalse,
        sensor=payload.sensor,
        medicion=payload.medicion,
    )
    alerts_store.append(new_alert)
    return new_alert


@app.get("/api/alerts/{alert_id}", response_model=AlertRecord, tags=["Alertas"])
def get_alert(alert_id: int) -> AlertRecord:
    for alert in alerts_store:
        if alert.id == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alerta no encontrada")
