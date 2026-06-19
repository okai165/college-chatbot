import os
from dotenv import load_dotenv
load_dotenv()
from app.routes.admin_auth import router as admin_auth_router
from app.routes.admin_stats import router as admin_stats_router
from app.routes.faculty import router as faculty_router
from app.routes.documents import router as documents_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.routes.notifications import router as notifications_router
# from app.crawler.scheduler import start_scheduler
from app.routes.admissions import router as admissions_router
print("API KEY LOADED:", os.getenv("GOOGLE_API_KEY"))

app = FastAPI()
@app.on_event("startup")
async def startup_event():
    print("Application Started")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_auth_router)
app.include_router(chat_router)
app.include_router(admin_stats_router)
app.include_router(faculty_router)
app.include_router(documents_router)
app.include_router(
    notifications_router,
    tags=["notifications"]
)
app.include_router(admissions_router)