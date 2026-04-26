import pytest

from app.core.providers import get_provider
from app.core.providers.base import ExcelProvider, SheetData
from app.core.providers.microsoft365 import Microsoft365Provider


class TestProviderFactory:
    def test_get_microsoft365_provider(self):
        provider = get_provider("microsoft365")
        assert isinstance(provider, Microsoft365Provider)
        assert isinstance(provider, ExcelProvider)

    def test_get_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider type"):
            get_provider("nonexistent")


class TestMicrosoft365Provider:
    def test_encode_sharing_url(self):
        url = "https://example.sharepoint.com/:x:/r/path/file.xlsx"
        encoded = Microsoft365Provider._encode_sharing_url(url)
        assert encoded.startswith("u!")
        assert "+" not in encoded
        assert "/" not in encoded[2:]  # skip "u!" prefix

    def test_auth_headers(self):
        headers = Microsoft365Provider._auth_headers("test-token-123")
        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["Content-Type"] == "application/json"


class TestSheetData:
    def test_sheet_data_creation(self):
        data = SheetData(
            headers=["Título", "Nombre", "Manager", "Access", "Resultado", "Other"],
            rows=[
                [1, "Eduard García", "jose.luis.escudero", "No", "", ""],
                [2, "Brian Keegar", "miguel.arbel", "No", "", ""],
            ],
        )
        assert len(data.headers) == 6
        assert len(data.rows) == 2
        assert data.rows[0][1] == "Eduard García"

    def test_empty_sheet_data(self):
        data = SheetData(headers=[], rows=[])
        assert data.headers == []
        assert data.rows == []
