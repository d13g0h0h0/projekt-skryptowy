import logging
import traceback


class DatabaseLogHandler(logging.Handler):

    def emit(self, record):
        try:
            from .models import ErrorLog

            request = getattr(record, "request", None)
            user = getattr(request, "user", None)
            ErrorLog.objects.create(
                level=record.levelname,
                logger=record.name[:100],
                message=record.getMessage(),
                traceback="".join(traceback.format_exception(*record.exc_info)) if record.exc_info else "",
                method=getattr(request, "method", "") or "",
                path=(getattr(request, "path", "") or "")[:500],
                status_code=getattr(record, "status_code", None),
                username=user.get_username() if getattr(user, "is_authenticated", False) else "",
            )
        except Exception:
            self.handleError(record)