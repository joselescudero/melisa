import base64

import httpx

from app.core.providers.base import ExcelProvider, SheetData

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class Microsoft365Provider(ExcelProvider):
    """Reads/writes Excel files stored in SharePoint / OneDrive via Microsoft Graph API."""

    @staticmethod
    def _encode_sharing_url(url: str) -> str:
        """Encode a sharing URL for the Graph /shares endpoint."""
        encoded = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
        return f"u!{encoded}"

    @staticmethod
    def _auth_headers(access_token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def read_sheet(self, file_url: str, sheet_name: str, access_token: str) -> SheetData:
        share_id = self._encode_sharing_url(file_url)
        url = f"{GRAPH_BASE}/shares/{share_id}/driveItem/workbook/worksheets('{sheet_name}')/usedRange"

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self._auth_headers(access_token))
            resp.raise_for_status()
            data = resp.json()

        values: list[list] = data.get("values", [])
        if not values:
            return SheetData(headers=[], rows=[])

        headers = [str(h) for h in values[0]]
        rows = values[1:]
        return SheetData(headers=headers, rows=rows)

    async def update_cell(
        self, file_url: str, sheet_name: str, cell_address: str, value: str, access_token: str
    ) -> None:
        share_id = self._encode_sharing_url(file_url)
        url = (
            f"{GRAPH_BASE}/shares/{share_id}/driveItem/workbook"
            f"/worksheets('{sheet_name}')/range(address='{cell_address}')"
        )

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.patch(
                url,
                headers=self._auth_headers(access_token),
                json={"values": [[value]]},
            )
            resp.raise_for_status()
