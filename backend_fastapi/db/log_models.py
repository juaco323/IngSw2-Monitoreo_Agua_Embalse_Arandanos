from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class _LogBase:
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    level = Column(String(10), nullable=False)
    message = Column(Text, nullable=False)
    component = Column(String(80), nullable=False)
    details = Column(JSONB, nullable=False, default=dict)
    correlation_id = Column(UUID(as_uuid=True), nullable=True)


class DashboardLogDB(Base, _LogBase):
    __tablename__ = "dashboard_logs"
    service_name = Column(String(80))
    environment = Column(String(40))
    host = Column(String(255))


class RegistroHistoricoLogDB(Base, _LogBase):
    __tablename__ = "registro_historico_logs"


class ExportarPdfLogDB(Base, _LogBase):
    __tablename__ = "exportar_pdf_logs"


class LoginLogDB(Base, _LogBase):
    __tablename__ = "login_logs"


class SupabaseDbLogDB(Base, _LogBase):
    __tablename__ = "supabase_db_logs"
    operation = Column(String(50))
    table_name = Column(String(100))
    query_type = Column(String(20))


class TelegramBotLogDB(Base, _LogBase):
    __tablename__ = "telegram_bot_logs"
    chat_id_hash = Column(String(64))
    command = Column(String(100))
    sent_count = Column(Integer)
    failed_count = Column(Integer)


class MailersendApiLogDB(Base, _LogBase):
    __tablename__ = "mailersend_api_logs"
    http_status = Column(Integer)
    recipient_count = Column(Integer)
    provider_message_id = Column(String(255))


LOG_MODEL_BY_TABLE = {
    "dashboard_logs": DashboardLogDB,
    "registro_historico_logs": RegistroHistoricoLogDB,
    "exportar_pdf_logs": ExportarPdfLogDB,
    "login_logs": LoginLogDB,
    "supabase_db_logs": SupabaseDbLogDB,
    "telegram_bot_logs": TelegramBotLogDB,
    "mailersend_api_logs": MailersendApiLogDB,
}
