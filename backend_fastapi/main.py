import os
import logging
from datetime import datetime
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN MONGODB
# ============================================================================

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "embalse_arandanos")

try:
    mongo_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    # Verificar conexión
    mongo_client.admin.command('ping')
    db = mongo_client[MONGODB_DB]
    logger.info("✓ Conexión a MongoDB establecida")
except ConnectionFailure:
    logger.warning("⚠ No se pudo conectar a MongoDB. Usando almacenamiento en memoria.")
    mongo_client = None
    db = None


app = FastAPI(
    title="API Monitoreo Embalse Arandanos",
    description=(
        "API para exponer lecturas de sensores y respaldo de alertas del dashboard."
    ),
    version="1.0.0",
)

# Agregar middleware CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (cambiar a lista específica en prod)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, OPTIONS, etc)
    allow_headers=["*"],
)


class SensorData(BaseModel):
    value: float
    min: float
    max: float
    safeMax: float
    lastUpdated: datetime
    status: Literal["stable", "warning", "critical"]


# ============================================================================
# MODELOS PARA RECIBIR DATOS DEL ESP8266
# ============================================================================

class SensorReading(BaseModel):
    ph: float
    temperature: float
    conductivity: float
    timestamp: int


class SensorDataResponse(BaseModel):
    ph: float
    temperature: float
    conductivity: float
    timestamp: datetime
    id: Optional[str] = None


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
    nombreDispositivo: str | None = None
    valor: float | None = None
    minimo: float | None = None
    maximo: float | None = None


class MailerSendConfig(BaseModel):
    api_token: str | None
    from_email: str | None
    from_name: str
    to_emails: list[str]


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


# ============================================================================
# FUNCIONES MONGODB
# ============================================================================

def save_sensor_reading_to_mongodb(reading: SensorReading) -> Optional[str]:
    """Guardar lectura de sensores en MongoDB"""
    if db is None:
        logger.warning("MongoDB no está disponible")
        return None
    
    try:
        collection = db["sensor_readings"]
        document = {
            "ph": reading.ph,
            "temperature": reading.temperature,
            "conductivity": reading.conductivity,
            "timestamp": datetime.utcfromtimestamp(reading.timestamp),
            "created_at": datetime.utcnow()
        }
        result = collection.insert_one(document)
        logger.info(f"✓ Lectura guardada en MongoDB con ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error guardando en MongoDB: {e}")
        return None


def get_latest_sensor_reading() -> Optional[dict]:
    """Obtener la última lectura de sensores desde MongoDB"""
    if db is None:
        logger.warning("MongoDB no está disponible")
        return None
    
    try:
        collection = db["sensor_readings"]
        reading = collection.find_one(sort=[("timestamp", -1)])
        if reading:
            reading["_id"] = str(reading["_id"])
            return reading
        return None
    except Exception as e:
        logger.error(f"Error leyendo de MongoDB: {e}")
        return None


def get_sensor_readings_history(limit: int = 100) -> list[dict]:
    """Obtener historial de lecturas de sensores"""
    if db is None:
        logger.warning("MongoDB no está disponible")
        return []
    
    try:
        collection = db["sensor_readings"]
        readings = list(collection.find().sort("timestamp", -1).limit(limit))
        for reading in readings:
            reading["_id"] = str(reading["_id"])
        return readings
    except Exception as e:
        logger.error(f"Error leyendo historial de MongoDB: {e}")
        return []


def update_dashboard_state_from_mongodb() -> None:
    """Actualizar el estado del dashboard desde la última lectura en MongoDB"""
    global dashboard_state
    
    reading = get_latest_sensor_reading()
    if reading:
        now = datetime.utcnow()
        
        # Determinar estado basado en rangos
        def get_status(value: float, min_val: float, max_val: float, safe_max: float) -> str:
            if value < min_val or value > max_val:
                return "critical"
            elif value > safe_max:
                return "warning"
            return "stable"
        
        dashboard_state = DashboardResponse(
            ph=SensorData(
                value=reading["ph"],
                min=6.0,
                max=8.5,
                safeMax=8.0,
                lastUpdated=reading.get("timestamp", now),
                status=get_status(reading["ph"], 6.0, 8.5, 8.0),
            ),
            temperature=SensorData(
                value=reading["temperature"],
                min=5,
                max=35,
                safeMax=28,
                lastUpdated=reading.get("timestamp", now),
                status=get_status(reading["temperature"], 5, 35, 28),
            ),
            conductivity=SensorData(
                value=reading["conductivity"],
                min=100,
                max=2000,
                safeMax=1500,
                lastUpdated=reading.get("timestamp", now),
                status=get_status(reading["conductivity"], 100, 2000, 1500),
            ),
            metadata=Metadata(
                systemStatus="operational",
                arduinoConnected=True,
                lastSync=now,
                uptime=int((now - reading.get("timestamp", now)).total_seconds()),
                activeSensors=3,
            ),
        )
        logger.info("✓ Dashboard actualizado desde MongoDB")


def get_mailersend_config() -> MailerSendConfig:
    to_emails_raw = os.getenv("MAILERSEND_TO_EMAILS", "")
    to_emails = [email.strip() for email in to_emails_raw.split(",") if email.strip()]
    return MailerSendConfig(
        api_token=os.getenv("MAILERSEND_API_TOKEN"),
        from_email=os.getenv("MAILERSEND_FROM_EMAIL"),
        from_name=os.getenv("MAILERSEND_FROM_NAME", "Monitoreo Embalse Arandanos"),
        to_emails=to_emails,
    )


def measurement_is_out_of_range(payload: AlertCreate) -> bool:
    if payload.valor is None or payload.minimo is None or payload.maximo is None:
        return True
    return payload.valor < payload.minimo or payload.valor > payload.maximo


def send_mailersend_notification(device_name: str, sensor: str, medicion: str, now: datetime) -> None:
    config = get_mailersend_config()
    if not config.api_token or not config.from_email or not config.to_emails:
        logger.warning(
            f"MailerSend no configurado. API Token: {bool(config.api_token)}, "
            f"From Email: {bool(config.from_email)}, To Emails: {bool(config.to_emails)}"
        )
        return

    logger.info(f"Enviando alerta por email: {device_name} - {sensor}")

    day_names = {
        0: "Lunes",
        1: "Martes",
        2: "Miercoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sabado",
        6: "Domingo",
    }
    day_name = day_names[now.weekday()]
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S")

    payload = {
        "from": {
            "email": config.from_email,
            "name": config.from_name,
        },
        "to": [{"email": email} for email in config.to_emails],
        "subject": f"⚠️ Alerta: {sensor} fuera de rango - {device_name}",
        "template_id": "351ndgw8m7rgzqx8",
        "personalization": [
            {
                "email": email,
                "data": {
                    "DEVICE_NAME": device_name,
                    "DAY_NAME": day_name,
                    "FECHA": fecha,
                    "HORA": hora,
                    "SENSOR": sensor,
                    "MEDICION": medicion,
                }
            }
            for email in config.to_emails
        ],
    }
    headers = {
        "Authorization": f"Bearer {config.api_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.mailersend.com/v1/email",
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code not in [200, 202]:
            logger.error(f"Respuesta MailerSend: {response.status_code} - {response.text}")
            response.raise_for_status()

        logger.info(f"Email enviado exitosamente a {config.to_emails}")
    except requests.RequestException as exc:
        logger.error(f"Error enviando email: {exc}")


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {"message": "API de Monitoreo Embalse Arandanos activa"}


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
def get_dashboard_data() -> DashboardResponse:
    """Obtener datos del dashboard, actualizados desde MongoDB"""
    update_dashboard_state_from_mongodb()
    return dashboard_state


# ============================================================================
# ENDPOINTS PARA SENSORES (ESP8266)
# ============================================================================

@app.put("/api/sensors/ph", response_model=dict, status_code=200, tags=["Sensores"])
def update_sensor_readings(reading: SensorReading):
    """
    Recibir lecturas de sensores del ESP8266 y guardar en MongoDB.
    El ESP8266 envia datos vía HTTP PUT en formato JSON.
    """
    logger.info(f"Recibiendo datos de sensores: pH={reading.ph}, Temp={reading.temperature}, Cond={reading.conductivity}")
    
    # Guardar en MongoDB
    mongo_id = save_sensor_reading_to_mongodb(reading)
    
    # Actualizar dashboard inmediatamente
    update_dashboard_state_from_mongodb()
    
    return {
        "status": "success",
        "message": "Datos guardados en MongoDB",
        "id": mongo_id,
        "data": {
            "ph": reading.ph,
            "temperature": reading.temperature,
            "conductivity": reading.conductivity,
            "timestamp": reading.timestamp
        }
    }


@app.post("/api/sensors/readings", response_model=dict, status_code=201, tags=["Sensores"])
def create_sensor_reading(reading: SensorReading):
    """
    Recibir y guardar una lectura de sensores.
    Alternativa POST al endpoint PUT.
    """
    logger.info(f"Nueva lectura de sensores: pH={reading.ph}, Temp={reading.temperature}, Cond={reading.conductivity}")
    
    mongo_id = save_sensor_reading_to_mongodb(reading)
    update_dashboard_state_from_mongodb()
    
    return {
        "status": "success",
        "message": "Lectura guardada",
        "id": mongo_id,
        "data": reading.dict()
    }


@app.get("/api/sensors/latest", response_model=Optional[SensorDataResponse], tags=["Sensores"])
def get_latest_reading():
    """Obtener la última lectura de sensores desde MongoDB"""
    reading = get_latest_sensor_reading()
    if reading:
        return SensorDataResponse(**reading)
    return None


@app.get("/api/sensors/history", response_model=list[SensorDataResponse], tags=["Sensores"])
def get_readings_history(limit: int = 100):
    """Obtener historial de lecturas de sensores (últimas N lecturas)"""
    readings = get_sensor_readings_history(limit)
    return [SensorDataResponse(**r) for r in readings]


@app.get("/api/alerts", response_model=list[AlertRecord], tags=["Alertas"])
def list_alerts() -> list[AlertRecord]:
    return alerts_store


@app.post("/api/alerts", response_model=AlertRecord, status_code=201, tags=["Alertas"])
def create_alert(payload: AlertCreate) -> AlertRecord:
    now = datetime.utcnow()
    device_name = payload.nombreDispositivo or payload.embalse
    new_alert = AlertRecord(
        id=(alerts_store[-1].id + 1) if alerts_store else 1,
        fecha=now.strftime("%Y-%m-%d"),
        hora=now.strftime("%H:%M"),
        embalse=device_name,
        sensor=payload.sensor,
        medicion=payload.medicion,
    )

    if measurement_is_out_of_range(payload):
        send_mailersend_notification(
            device_name=device_name,
            sensor=payload.sensor,
            medicion=payload.medicion,
            now=now,
        )

    alerts_store.append(new_alert)
    return new_alert


@app.get("/api/alerts/{alert_id}", response_model=AlertRecord, tags=["Alertas"])
def get_alert(alert_id: int) -> AlertRecord:
    for alert in alerts_store:
        if alert.id == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alerta no encontrada")
