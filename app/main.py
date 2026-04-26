from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.excel import router as excel_router

app = FastAPI(title="Excel Processor")
app.include_router(excel_router)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
