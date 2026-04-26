from pathlib import Path

import pytest
from openpyxl import Workbook

from app.core.providers import get_provider, requires_auth
from app.core.providers.local_file import LocalFileProvider


@pytest.fixture
def sample_xlsx(tmp_path: Path) -> Path:
    path = tmp_path / "demo.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["Título", "Nombre", "Manager", "Access", "Resultado", "Other"])
    ws.append([1, "Eduard García", "jose.luis", "No", "", ""])
    ws.append([2, "Brian Keegan", "miguel.arbel", "No", "", ""])
    wb.save(path)
    return path


class TestLocalProviderRegistration:
    def test_local_provider_registered(self):
        provider = get_provider("local")
        assert isinstance(provider, LocalFileProvider)

    def test_local_does_not_require_auth(self):
        assert requires_auth("local") is False

    def test_microsoft365_requires_auth(self):
        assert requires_auth("microsoft365") is True


class TestLocalFileProvider:
    @pytest.mark.asyncio
    async def test_read_sheet(self, sample_xlsx: Path):
        provider = LocalFileProvider()
        data = await provider.read_sheet(str(sample_xlsx), "Sheet1", "")
        assert data.headers == ["Título", "Nombre", "Manager", "Access", "Resultado", "Other"]
        assert len(data.rows) == 2
        assert data.rows[0][1] == "Eduard García"

    @pytest.mark.asyncio
    async def test_read_sheet_with_file_scheme(self, sample_xlsx: Path):
        provider = LocalFileProvider()
        data = await provider.read_sheet(f"file://{sample_xlsx}", "Sheet1", "")
        assert len(data.rows) == 2

    @pytest.mark.asyncio
    async def test_update_cell(self, sample_xlsx: Path):
        provider = LocalFileProvider()
        await provider.update_cell(str(sample_xlsx), "Sheet1", "E2", "Yes", "")
        data = await provider.read_sheet(str(sample_xlsx), "Sheet1", "")
        assert data.rows[0][4] == "Yes"

    @pytest.mark.asyncio
    async def test_missing_file_raises(self):
        provider = LocalFileProvider()
        with pytest.raises(FileNotFoundError):
            await provider.read_sheet("/nonexistent/file.xlsx", "Sheet1", "")

    @pytest.mark.asyncio
    async def test_unsupported_extension_raises(self, tmp_path: Path):
        bad = tmp_path / "old.xls"
        bad.write_bytes(b"fake")
        provider = LocalFileProvider()
        with pytest.raises(ValueError, match="Unsupported file format"):
            await provider.read_sheet(str(bad), "Sheet1", "")

    @pytest.mark.asyncio
    async def test_unknown_sheet_raises(self, sample_xlsx: Path):
        provider = LocalFileProvider()
        with pytest.raises(ValueError, match="not found"):
            await provider.read_sheet(str(sample_xlsx), "DoesNotExist", "")
