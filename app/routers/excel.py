from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.providers import get_provider, requires_auth

router = APIRouter(prefix="/api/excel", tags=["excel"])

_provider = get_provider(settings.provider_type)
_needs_auth = requires_auth(settings.provider_type)


class CellUpdate(BaseModel):
    file_url: str
    sheet_name: str
    cell_address: str
    value: str


def _extract_token(authorization: str | None) -> str:
    if not _needs_auth:
        return ""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")
    return token


@router.get("/config")
async def get_config() -> dict:
    return {
        "provider_type": settings.provider_type,
        "requires_auth": _needs_auth,
        "azure_client_id": settings.azure_client_id,
        "azure_tenant_id": settings.azure_tenant_id,
        "excel_file_url": settings.excel_file_url,
        "excel_sheet_name": settings.excel_sheet_name,
    }


@router.get("/sheet")
async def read_sheet(
    file_url: str | None = None,
    sheet_name: str | None = None,
    authorization: str | None = Header(default=None),
) -> dict:
    token = _extract_token(authorization)
    url = file_url or settings.excel_file_url
    sheet = sheet_name or settings.excel_sheet_name

    if not url:
        raise HTTPException(status_code=400, detail="No Excel file URL configured")

    try:
        data = await _provider.read_sheet(url, sheet, token)
        return {"headers": data.headers, "rows": data.rows}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to read Excel: {exc}") from exc


@router.patch("/cell")
async def update_cell(body: CellUpdate, authorization: str | None = Header(default=None)) -> dict:
    token = _extract_token(authorization)

    try:
        await _provider.update_cell(body.file_url, body.sheet_name, body.cell_address, body.value, token)
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to update cell: {exc}") from exc
