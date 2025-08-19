from datetime import datetime, timedelta
from sqlalchemy import select, func
from collections import defaultdict, Counter
import statistics
import json
import os

from app.api.routes.v1.analysis.models import JobInvite
from app.db.session import async_session_maker


# ---------------- Utility Functions ---------------- #

def prepare_call_data(results):
    """Filter and prepare raw call data."""
    data = []
    for i in results:
        if i.call_start_time and i.total_call:
            data.append({
                "call_start_time": i.call_start_time,
                "total_call": i.total_call,
                "DTMF": i.DTMF,
            })
    return data


def filter_calls(data):
    """Filter out calls shorter than the dynamic min_duration (average call length)."""
    if not data:
        return []

    # min_duration = statistics.mean([d["total_call"] for d in data])
    min_duration = 10  # Fallback to a default value if no data is available
    if min_duration <= 0:   # Avoid division by zero
        min_duration = 10
    return [d for d in data if d["total_call"] > min_duration]


def add_time_features(data):
    """Add weekday, hour, and date fields to call records."""
    for d in data:
        d["weekday"] = d["call_start_time"].strftime("%A")
        d["hour"] = d["call_start_time"].hour
        d["date"] = d["call_start_time"].date()
    return data


def compute_avg_calls_per_hour(data):
    """Compute average calls per hour per weekday."""
    unique_days = set((d["date"], d["weekday"]) for d in data)
    num_days_per_weekday = {
        day: sum(1 for _, w in unique_days if w == day)
        for day in set(w for _, w in unique_days)
    }

    grouped = defaultdict(lambda: defaultdict(int))
    for d in data:
        grouped[d["weekday"]][d["hour"]] += 1

    avg_calls = defaultdict(dict)
    for weekday, hours in grouped.items():
        for hour, total_calls in hours.items():
            days = num_days_per_weekday.get(weekday, 1)
            avg_calls[weekday][hour] = total_calls / days
    return avg_calls, grouped


def get_top_overall_hours(grouped, top_n=3):
    """Get overall top hours ignoring weekdays."""
    overall_counts = Counter()
    for _, hours in grouped.items():
        for hour, total_calls in hours.items():
            overall_counts[hour] += total_calls
    return [f"{h:02d}:00" for h, _ in overall_counts.most_common(top_n)]


def get_best_hours_by_weekday(avg_calls, top_n=3):
    """Get top N hours for each weekday."""
    weekdays_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]
    result = {}
    for day in weekdays_order:
        hours = avg_calls.get(day, {})
        top_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:top_n]
        result[day.lower()[:3]] = [f"{h:02d}:00" for h, _ in top_hours]
    return result


def compute_call_statistics(data):
    """Compute average DTMF count and call time."""
    dtmf_counts = []
    for d in data:
        if d["DTMF"]:
            dtmf_counts.append(len([x for x in d["DTMF"].split(",") if x.strip()]))
    avg_questions = statistics.mean(dtmf_counts) if dtmf_counts else 0
    avg_call_time = statistics.mean([d["total_call"] for d in data]) if data else 0
    return round(avg_questions, 2), round(avg_call_time, 2)


# ---------------- Core Analysis ---------------- #

async def analyze_calls(results):
    """Perform analysis on call records."""
    data = prepare_call_data(results)
    data = filter_calls(data)

    if not data:
        return {
            "best_hours": {},
            "top_overall_hours": [],
            "avg_number_of_question_user_answers": 0,
            "average_call_time": 0,
        }

    data = add_time_features(data)
    avg_calls, grouped = compute_avg_calls_per_hour(data)

    best_hours = get_best_hours_by_weekday(avg_calls)
    top_overall_hours = get_top_overall_hours(grouped)
    avg_questions, avg_call_time = compute_call_statistics(data)

    return {
        "best_hours": best_hours,
        "top_overall_hours": top_overall_hours,
        "avg_number_of_question_user_answers": avg_questions,
        "average_call_time": avg_call_time,
    }


def fill_missing_days(res_small, res_large):
    """Fill missing best_hours using weekly average or fallback to large window."""
    best_hours_7 = res_small["best_hours"]
    empty_days = [day for day, times in best_hours_7.items() if not times]

    if len(empty_days) == 1:
        # Fill with weekly average from non-empty days
        all_hours = [h for times in best_hours_7.values() if times for h in times]
        if all_hours:
            avg_top = [h for h, _ in Counter(all_hours).most_common(3)]
            best_hours_7[empty_days[0]] = avg_top
    elif len(empty_days) > 1:
        # Fill all with overall top from 90 days
        for day in empty_days:
            best_hours_7[day] = res_large["top_overall_hours"]

    return best_hours_7


# ---------------- Orchestration ---------------- #

async def generate_best_times(days_large: int = 2000, days_small: int = 1800):
    async with async_session_maker() as session:
        latest_date_result = await session.execute(select(func.max(JobInvite.call_start_time)))
        latest_date = latest_date_result.scalar_one_or_none()
        if not latest_date:
            print("No records in DB.")
            return

        final_results = {}

        start_date = latest_date - timedelta(days=days_large)
        stmt = select(JobInvite).where(JobInvite.call_start_time >= start_date)  # type: ignore

        country_map = defaultdict(list)
        async for row in (await session.stream(stmt.execution_options(yield_per=1000))).scalars():
            country_map[row.countryCode].append(row)

        print("Data fetched for all countries.")

        for country, rows in country_map.items():
            cutoff_small = latest_date - timedelta(days=days_small)

            data_large = rows
            data_small = [r for r in rows if r.call_start_time >= cutoff_small]

            res_large = await analyze_calls(data_large)
            res_small = await analyze_calls(data_small)

            # Fallback filling
            res_small["best_hours"] = fill_missing_days(res_small, res_large)

            final_results[country] = {
                "90_days": res_large,
                "7_days": res_small,
            }

        # Save results
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "analysis_results",
            "best_times.json"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(final_results, f, default=str, indent=4)

        print(f"Results saved to {file_path}")
