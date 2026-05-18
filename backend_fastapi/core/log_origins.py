from enum import Enum


class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    FATAL = "FATAL"


class LogOrigin(str, Enum):
    DASHBOARD = "dashboard_logs"
    REGISTRO_HISTORICO = "registro_historico_logs"
    EXPORTAR_PDF = "exportar_pdf_logs"
    LOGIN = "login_logs"
    SUPABASE_DB = "supabase_db_logs"
    TELEGRAM = "telegram_bot_logs"
    MAILERSEND = "mailersend_api_logs"


VALID_ORIGINS = {o.value for o in LogOrigin}
VALID_LEVELS = {l.value for l in LogLevel}
