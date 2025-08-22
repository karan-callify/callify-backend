# app/workers/worker.py
import asyncio
from app.config import CronSettings
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
from apscheduler.triggers.cron import CronTrigger # type: ignore
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.workers.utils.find_and_analyze_cron import generate_best_times_new

scheduler = AsyncIOScheduler()
cron_settings = CronSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        generate_best_times_new,  # pass the coroutine directly
        CronTrigger(
            # day_of_week=cron_settings.CRON_DAY_OF_WEEK,
            # hour=cron_settings.CRON_HOUR,
            # minute=cron_settings.CRON_MINUTE,
            second=cron_settings.CRON_SECOND,
            # timezone=cron_settings.CRON_TIMEZONE,
        ),
        coalesce=True,
        max_instances=1,
    )
    scheduler.start()
    print("Scheduler started ✅")
    yield
    scheduler.shutdown()
    print("Scheduler stopped ❌")
