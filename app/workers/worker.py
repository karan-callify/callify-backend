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
        CronTrigger(second=5)  # adjust to desired schedule
    )
    scheduler.start()
    print("Scheduler started ✅")
    yield
    scheduler.shutdown()
    print("Scheduler stopped ❌")
