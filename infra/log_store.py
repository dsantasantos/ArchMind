import logging
from collections import deque
from datetime import datetime

_MAX_EXECUTIONS = 200
_store: dict[str, list[dict]] = {}
_order: deque[str] = deque(maxlen=_MAX_EXECUTIONS)

_INTERNAL_FIELDS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "taskName", "execution_id",
}


class ExecutionLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        execution_id = getattr(record, "execution_id", None)
        if execution_id is None:
            return

        if execution_id not in _store:
            if len(_order) == _MAX_EXECUTIONS:
                _store.pop(_order[0], None)
            _store[execution_id] = []
            _order.append(execution_id)

        entry = {
            "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update({
            k: v for k, v in record.__dict__.items()
            if k not in _INTERNAL_FIELDS and not k.startswith("_")
        })
        _store[execution_id].append(entry)


def get_execution_logs(execution_id: str) -> list[dict] | None:
    return _store.get(execution_id)
