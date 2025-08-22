from datetime import datetime, timedelta
from sqlalchemy import select, func
from collections import defaultdict
import json
import os
import statistics

from app.api.routes.v1.analysis.models import JobInvite
from app.db.session import async_session_maker
from app.config import CronSettings


cron_days_settings = CronSettings()


# ---------------- Utility Functions ---------------- #

def get_time_ranges():
    """Generate hourly ranges like 10:01-11:00."""
    ranges = []
    for h in range(0, 24):
        start = f"{h:02d}:01"
        end = f"{(h+1)%24:02d}:00"
        ranges.append((h, f"{start}-{end}"))
    return ranges


def classify_call(total_call):
    """Classify call based on duration."""
    if not total_call or total_call == 0:
        return "not_answered"
    elif total_call < 120:
        return "not_interested"
    else:
        return "interested"


def bucketize_calls(rows):
    """Group calls into weekday + time range buckets with percentages."""
    ranges = get_time_ranges()
    weekmap = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    # structure: weekday -> range_label -> counts
    data = defaultdict(lambda: defaultdict(lambda: {
        "not_answered": 0,
        "not_interested": 0,
        "interested": 0
    }))

    for r in rows:
        if not r.call_start_time:
            continue

        weekday = weekmap[r.call_start_time.weekday()]
        hour = r.call_start_time.hour

        # map hour to range
        _, range_label = ranges[hour]

        cls = classify_call(r.total_call)
        data[weekday][range_label][cls] += 1

    # ✅ convert to percentages
    for weekday, ranges_dict in data.items():
        for range_label, counts in ranges_dict.items():
            total = sum(counts.values())
            if total > 0:
                data[weekday][range_label] = {
                    k: round((v / total) * 100, 2)  # 2 decimal %
                    for k, v in counts.items()
                }
            else:
                data[weekday][range_label] = {
                    "not_answered": 0.0,
                    "not_interested": 0.0,
                    "interested": 0.0
                }

    return data


def count_questions_from_dtmf(dtmf: str) -> int:
    """
    Old method: count number of comma-separated non-empty entries in DTMF.
    Examples:
      "1,1" -> 2
      "1,  ,2" -> 2
      "" or None -> 0
    """
    if not dtmf:
        return 0
    parts = [p.strip() for p in str(dtmf).split(",")]
    return sum(1 for p in parts if p != "")


def calculate_averages(rows):
    """
    Calculate averages directly from raw rows:
      - avg_call_duration: mean of total_call > 0
      - avg_number_of_questions_answered: mean of counts from DTMF split method
    """
    durations = [r.total_call for r in rows if getattr(r, "total_call", None) and r.total_call > 0]

    dtmf_counts = []
    for r in rows:
        dtmf_val = getattr(r, "DTMF", None)
        if dtmf_val:  # only include rows that actually have a DTMF string
            dtmf_counts.append(count_questions_from_dtmf(dtmf_val))

    avg_call_duration = round(statistics.mean(durations), 2) if durations else 0.0
    avg_questions_answered = round(statistics.mean(dtmf_counts), 2) if dtmf_counts else 0.0

    return {
        "avg_call_duration": avg_call_duration,
        "avg_number_of_questions_answered": avg_questions_answered,
    }


# ---------------- Core Analysis ---------------- #

async def generate_best_times_new():
    """Perform new analysis for 3 months, 1 month, and 7 days."""
    async with async_session_maker() as session:
        latest_date_result = await session.execute(select(func.max(JobInvite.call_start_time)))
        latest_date = latest_date_result.scalar_one_or_none()
        if not latest_date:
            print("No records in DB.")
            return

        # Fetch all data for last 3 months in one query (kept same as your current code)
        start_date = latest_date - timedelta(days=cron_days_settings.THREE_MONTHS)
        stmt = select(JobInvite).where(JobInvite.call_start_time >= start_date)

        country_map = defaultdict(list)
        async for row in (await session.stream(stmt.execution_options(yield_per=1000))).scalars():
            country_map[row.countryCode].append(row)

        print("Data fetched for all countries.")

        final_results = {}

        for country, rows in country_map.items():
            windows = {
                "three_months": latest_date - timedelta(days=cron_days_settings.THREE_MONTHS),
                # "one_month": latest_date - timedelta(days=2500),
                "seven_days": latest_date - timedelta(days=cron_days_settings.SEVEN_DAYS),
            }

            final_results[country] = {}
            for key, cutoff in windows.items():
                window_rows = [r for r in rows if r.call_start_time >= cutoff]

                # Buckets (percentages) — unchanged
                buckets = bucketize_calls(window_rows)

                # Averages from raw rows using the old DTMF split logic
                avgs = calculate_averages(window_rows)

                # Merge: keep weekday buckets at top level, and add averages
                window_obj = dict(buckets)  # copy to mutate safely
                window_obj["avg_call_duration"] = avgs["avg_call_duration"]
                window_obj["avg_number_of_questions_answered"] = avgs["avg_number_of_questions_answered"]

                final_results[country][key] = window_obj

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
