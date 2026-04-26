from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_client_id: str = ""
    azure_tenant_id: str = ""
    excel_file_url: str = ""
    excel_sheet_name: str = "Sheet1"
    provider_type: str = "microsoft365"

    model_config = {"env_file": ".env"}


settings = Settings()
