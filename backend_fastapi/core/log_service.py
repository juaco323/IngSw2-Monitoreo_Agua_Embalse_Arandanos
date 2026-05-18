import logging
import os
import socket
from typing import Any, Optional, Union
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from core.log_context import ensure_correlation_id, get_correlation_id, parse_correlation_id
from core.log_origins import LogLevel, LogOrigin, VALID_LEVELS, VALID_ORIGINS
from core.log_sanitizer import sanitize_details
from core.logging_config import write_fallback_record
from db.database import SessionLocal, init_log_tables

_console = logging.getLogger("structured_log")
_logging_in_progress = False

EXTRA_COLUMNS_BY_ORIGIN = {
    LogOrigin.DASHBOARD.value: {"service_name", "environment", "host"},
    LogOrigin.SUPABASE_DB.value: {"operation", "table_name", "query_type"},
    LogOrigin.TELEGRAM.value: {"chat_id_hash", "command", "sent_count", "failed_count"},
    LogOrigin.MAILERSEND.value: {"http_status", "recipient_count", "provider_message_id"},
}


class LogService:
    def __init__(self):
        self._tables_initialized = False

    def _ensure_tables(self) -> None:
        if not self._tables_initialized and SessionLocal is not None:
            try:
                init_log_tables()
                self._tables_initialized = True
            except Exception:
                pass

    def log(
        self,
        origin: Union[LogOrigin, str],
        level: Union[LogLevel, str],
        message: str,
        component: str,
        details: Optional[dict] = None,
        correlation_id: Optional[str] = None,
        **extra_columns: Any,
    ) -> bool:
        global _logging_in_progress

        origin_str = origin.value if isinstance(origin, LogOrigin) else origin
        level_str = level.value if isinstance(level, LogLevel) else level.upper()

        if origin_str not in VALID_ORIGINS or level_str not in VALID_LEVELS:
            return False

        corr = correlation_id or get_correlation_id() or ensure_correlation_id()
        clean_details = sanitize_details(details)

        if origin_str == LogOrigin.DASHBOARD.value:
            extra_columns.setdefault("service_name", "API Monitoreo Embalse Arandanos")
            extra_columns.setdefault("environment", os.getenv("APP_ENV", "development"))
            extra_columns.setdefault("host", socket.gethostname())

        self._log_console(level_str, message, component, origin_str, corr)

        if SessionLocal is None:
            write_fallback_record(
                origin=origin_str, level=level_str, message=message, component=component,
                correlation_id=corr, details=clean_details,
                insert_error="SUPABASE_DB_URL no configurada",
            )
            return False

        if _logging_in_progress:
            write_fallback_record(
                origin=origin_str, level=level_str, message=message, component=component,
                correlation_id=corr, details=clean_details, insert_error="recursive_log_guard",
            )
            return False

        from db.log_models import LOG_MODEL_BY_TABLE

        self._ensure_tables()
        model_cls = LOG_MODEL_BY_TABLE[origin_str]
        allowed = EXTRA_COLUMNS_BY_ORIGIN.get(origin_str, set())
        row = {
            "level": level_str,
            "message": message[:4000],
            "component": component[:80],
            "details": clean_details,
            "correlation_id": parse_correlation_id(corr),
        }
        for k, v in extra_columns.items():
            if k in allowed or hasattr(model_cls, k):
                row[k] = v

        db = SessionLocal()
        try:
            _logging_in_progress = True
            db.add(model_cls(**row))
            db.commit()
            return True
        except SQLAlchemyError as exc:
            db.rollback()
            write_fallback_record(
                origin=origin_str, level=level_str, message=message, component=component,
                correlation_id=corr, details=clean_details, insert_error=str(exc),
            )
            return False
        finally:
            _logging_in_progress = False
            db.close()

    def _log_console(self, level, message, component, origin, corr):
        text = f"[{origin}] [{component}] [{corr}] {message}"
        if level == "FATAL":
            _console.critical(text)
        elif level == "WARN":
            _console.warning(text)
        else:
            _console.info(text)

    def log_db(self, level, message, component, *, operation=None, table_name=None,
               query_type=None, details=None, correlation_id=None):
        return self.log(
            LogOrigin.SUPABASE_DB, level, message, component, details=details,
            correlation_id=correlation_id, operation=operation,
            table_name=table_name, query_type=query_type,
        )

    def log_login(self, level, message, component="auth.session", details=None):
        return self.log(LogOrigin.LOGIN, level, message, component, details=details)

    def log_telegram(
        self, level, message, component="telegram_sender", details=None, **kwargs
    ):
        return self.log(
            LogOrigin.TELEGRAM, level, message, component, details=details, **kwargs
        )

    def log_mailersend(
        self, level, message, component="mailersend_client", details=None, **kwargs
    ):
        return self.log(
            LogOrigin.MAILERSEND, level, message, component, details=details, **kwargs
        )


log_service = LogService()
