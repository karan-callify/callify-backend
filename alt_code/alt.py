# Fetch data from the database using SQL Query Language (SQLAlchemy)


async def generate_best_times():
    async with async_session_maker() as session:
        # Get latest call_start_time
        latest_date_result = await session.execute(
            select(func.max(JobInvite.call_start_time))
        )
        latest_date = latest_date_result.scalar_one_or_none()
        if not latest_date:
            print("No records in DB.")
            return

        final_results = {}
        ranges = {
            "90_days": latest_date - timedelta(days=90),
            "7_days": latest_date - timedelta(days=7),
        }

        for label, start_date in ranges.items():
            # ---- Hourly aggregation ----
            stmt_hours = text("""
                SELECT
                    countryCode,
                    DAYNAME(call_start_time) AS weekday,
                    HOUR(call_start_time) AS hour,
                    COUNT(*) * 1.0 / COUNT(DISTINCT DATE(call_start_time)) AS avg_calls
                FROM jobinvite
                WHERE call_start_time >= :start_date
                GROUP BY countryCode, weekday, hour
            """)

            rows_hours = (await session.execute(stmt_hours, {"start_date": start_date})).mappings().all()

            # Organize by country -> weekday -> [(hour, avg_calls)]
            country_hours = defaultdict(lambda: defaultdict(list))
            for r in rows_hours:
                country_hours[r["countryCode"]][r["weekday"]].append((r["hour"], r["avg_calls"]))

            # ---- Averages ----
            stmt_avg = text("""
                SELECT
                    countryCode,
                    AVG(total_call) AS avg_call_time,
                    AVG(
                        CASE 
                            WHEN DTMF IS NOT NULL AND DTMF != '' 
                            THEN LENGTH(REPLACE(DTMF, ',', '')) 
                            ELSE 0
                        END
                    ) AS avg_questions
                FROM jobinvite
                WHERE call_start_time >= :start_date
                GROUP BY countryCode
            """)

            rows_avg = (await session.execute(stmt_avg, {"start_date": start_date})).mappings().all()
            avg_map = {r["countryCode"]: r for r in rows_avg}

            # ---- Build result per country ----
            for country in set(list(country_hours.keys()) + list(avg_map.keys())):
                if country not in final_results:
                    final_results[country] = {}

                # format best hours
                best_hours = {}
                weekdays_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                for day in weekdays_order:
                    hours = sorted(country_hours[country].get(day, []), key=lambda x: x[1], reverse=True)[:3]
                    best_hours[day.lower()[:3]] = [f"{h:02d}:00" for h, _ in hours]

                avg_row = avg_map.get(country, {})
                final_results[country][label] = {
                    "best_hours": best_hours,
                    "avg_number_of_question_user_answers": round(avg_row.get("avg_questions", 0) or 0, 2),
                    "average_call_time": round(avg_row.get("avg_call_time", 0) or 0, 2),
                }

        # ---- Save to JSON ----
        file_path = os.path.join(os.path.dirname(__file__), "best_times.json")
        with open(file_path, "w") as f:
            json.dump(final_results, f, default=str, indent=4)

        print(f"Results saved to {file_path}")



# cron job that uses average call times and best hours
from datetime import datetime, timedelta
from sqlalchemy import select, func
from collections import defaultdict
import statistics
import json
import os

from app.api.routes.v1.analysis.models import JobInvite
from app.db.session import async_session_maker


async def analyze_calls(results):
    # Prepare data
    data = []
    for i in results:
        if not i.call_start_time or not i.total_call:
            continue
        data.append({
            "call_start_time": i.call_start_time,
            "total_call": i.total_call,
            "DTMF": i.DTMF,
        })

    if not data:
        return {
            "best_hours": {},
            "top_overall_hours": [],
            "avg_number_of_question_user_answers": 0,
            "average_call_time": 0,
        }

    # Calculate min_duration (average total_call)
    min_duration = statistics.mean([d["total_call"] for d in data])

    # Filter calls where total_call > min_duration
    filtered = [d for d in data if d["total_call"] > min_duration]

    if not filtered:
        return {
            "best_hours": {},
            "top_overall_hours": [],
            "avg_number_of_question_user_answers": 0,
            "average_call_time": 0,
        }

    # Add weekday, hour, date
    for d in filtered:
        d["weekday"] = d["call_start_time"].strftime("%A")
        d["hour"] = d["call_start_time"].hour
        d["date"] = d["call_start_time"].date()

    # Unique days per weekday
    unique_days = set((d["date"], d["weekday"]) for d in filtered)
    num_days_per_weekday = {
        day: sum(1 for _, w in unique_days if w == day)
        for day in set(w for _, w in unique_days)
    }

    # Group by weekday, hour
    grouped = defaultdict(lambda: defaultdict(int))
    for d in filtered:
        grouped[d["weekday"]][d["hour"]] += 1

    # Calculate average calls per hour per weekday
    avg_calls = defaultdict(dict)
    for weekday, hours in grouped.items():
        for hour, total_calls in hours.items():
            days = num_days_per_weekday.get(weekday, 1)
            avg_calls[weekday][hour] = total_calls / days

    # ---- Overall top hours (whole dataset, ignore weekday) ----
    overall_counts = defaultdict(int)
    for weekday, hours in grouped.items():
        for hour, total_calls in hours.items():
            overall_counts[hour] += total_calls

    top_overall_hours = sorted(
        overall_counts.items(), key=lambda x: x[1], reverse=True
    )[:3]
    top_overall_hours = [f"{h:02d}:00" for h, _ in top_overall_hours]

    # For each weekday, get top 3 hours
    weekdays_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]
    result = {}
    for day in weekdays_order:
        hours = avg_calls.get(day, {})
        top_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]
        result[day.lower()[:3]] = [f"{h:02d}:00" for h, _ in top_hours]

    # Calculate avg_number_of_question_user_answers
    dtmf_counts = []
    for d in filtered:
        if d["DTMF"]:
            dtmf_counts.append(len([x for x in d["DTMF"].split(",") if x.strip()]))
    avg_questions = statistics.mean(dtmf_counts) if dtmf_counts else 0

    # Calculate average_call_time
    avg_call_time = statistics.mean([d["total_call"] for d in filtered])

    return {
        "best_hours": result,
        "top_overall_hours": top_overall_hours,
        "avg_number_of_question_user_answers": round(avg_questions, 2),
        "average_call_time": round(avg_call_time, 2),
    }


async def generate_best_times(days_large: int = 3000, days_small: int = 1500):
    async with async_session_maker() as session:
        # Find latest call time
        latest_date_result = await session.execute(select(func.max(JobInvite.call_start_time)))
        latest_date = latest_date_result.scalar_one_or_none()
        if not latest_date:
            print("No records in DB.")
            return

        final_results = {}

        # ---- Fetch only once (large window, e.g., 90 days) ----
        start_date = latest_date - timedelta(days=days_large)
        stmt = select(JobInvite).where(JobInvite.call_start_time >= start_date)  # type: ignore

        country_map = defaultdict(list)
        async for row in (await session.stream(stmt.execution_options(yield_per=1000))).scalars():
            country_map[row.countryCode].append(row)

        print("data fetched for all countries.")

        # ---- Analyze for all windows ----
        for country, rows in country_map.items():
            cutoff_small = latest_date - timedelta(days=days_small)

            data_large = rows
            data_small = [r for r in rows if r.call_start_time >= cutoff_small]

            res_large = await analyze_calls(data_large)
            res_small = await analyze_calls(data_small)

            # ---- Apply fallback ----
            best_hours_7 = res_small["best_hours"]
            empty_days = [day for day, times in best_hours_7.items() if not times]

            if len(empty_days) == 1:
                # Fill with overall top hours from 7 days
                best_hours_7[empty_days[0]] = res_small["top_overall_hours"]
            elif len(empty_days) > 1:
                # Copy from 30 days
                for day in empty_days:
                    best_hours_7[day] = res_large["best_hours"].get(day, [])

            final_results[country] = {
                "30_days": res_large,
                "7_days": {**res_small, "best_hours": best_hours_7},
            }

        # ---- Save results ----
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "analysis_results",
            "best_times.json"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(final_results, f, default=str, indent=4)

        print(f"Results saved to {file_path}")
