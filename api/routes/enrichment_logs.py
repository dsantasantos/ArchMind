from fastapi import APIRouter
from fastapi.responses import JSONResponse

from infra.log_store import get_execution_logs

router = APIRouter()


@router.get("/enrichment/logs/{execution_id}")
def get_enrichment_logs(execution_id: str):
    logs = get_execution_logs(execution_id)
    if logs is None:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"No logs found for execution_id '{execution_id}'"},
        )
    return JSONResponse(
        status_code=200,
        content={"status": "success", "execution_id": execution_id, "count": len(logs), "logs": logs},
    )
