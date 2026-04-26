import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestConfigEndpoint:
    @pytest.mark.asyncio
    async def test_get_config(self, client: AsyncClient):
        resp = await client.get("/api/excel/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "provider_type" in data
        assert "requires_auth" in data
        assert "excel_file_url" in data
        assert "excel_sheet_name" in data


class TestAuthBehavior:
    """Auth header is optional for local provider, required for cloud providers.

    These tests reflect whichever provider is currently active in settings.
    """

    @pytest.mark.asyncio
    async def test_sheet_endpoint_responds(self, client: AsyncClient):
        resp = await client.get("/api/excel/sheet")
        if settings.provider_type == "local":
            # No auth required — should not return 401
            assert resp.status_code != 401
        else:
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_cell_endpoint_responds(self, client: AsyncClient):
        resp = await client.patch(
            "/api/excel/cell",
            json={"file_url": "http://x", "sheet_name": "Sheet1", "cell_address": "E2", "value": "Yes"},
        )
        if settings.provider_type == "local":
            assert resp.status_code != 401
        else:
            assert resp.status_code == 401
