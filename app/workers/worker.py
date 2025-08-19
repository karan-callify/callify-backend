# app/workers/worker.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
from apscheduler.triggers.cron import CronTrigger # type: ignore
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.workers.utils.find_and_analyze_cron import generate_best_times

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        generate_best_times,
        CronTrigger(
            day_of_week="sat",
            hour=0,             # 12 AM
            minute=0,           # 00 minutes
            second=0,
            timezone="Asia/Kolkata"            # 00 seconds
        )
    )
    scheduler.start()
    print("Scheduler started ✅")
    yield
    scheduler.shutdown()
    print("Scheduler stopped ❌")
