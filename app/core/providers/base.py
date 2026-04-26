from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SheetData:
    headers: list[str]
    rows: list[list[str | int | float | None]]


class ExcelProvider(ABC):
    """Abstract base for Excel file providers.

    Each provider encapsulates how to authenticate, locate, read, and write
    to an Excel file in a specific storage backend (M365, Google Sheets, local, etc.).
    """

    @abstractmethod
    async def read_sheet(self, file_url: str, sheet_name: str, access_token: str) -> SheetData:
        """Read all data from a sheet. Returns headers + data rows."""

    @abstractmethod
    async def update_cell(
        self, file_url: str, sheet_name: str, cell_address: str, value: str, access_token: str
    ) -> None:
        """Update a single cell value (e.g. cell_address='E2')."""
