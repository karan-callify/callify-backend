from datetime import timedelta
from sqlalchemy import select, func
from collections import defaultdict
import statistics
import json
import os
import uuid

from app.api.routes.v1.analysis.models import JobInvite
from app.db.session import async_session_maker
from app.config import CronSettings

cron_days_settings = CronSettings()

# ---------------- Utility Functions ---------------- #

def get_time_ranges():
    """Generate hourly ranges like 10:01-11:00."""
    return [(h, f"{h:02d}:01-{(h+1) % 24:02d}:00") for h in range(24)]

def classify_call(total_call):
    """Classify call based on duration."""
    if not total_call or total_call == 0:
        return "not_answered"
    elif total_call < 120:
        return "not_interested"
    return "interested"

def bucketize_calls(rows):
    """Group calls into weekday + time range buckets with percentages."""
    ranges = get_time_ranges()
    weekmap = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    data = defaultdict(lambda: defaultdict(dict))

    # First pass: Count calls
    for r in rows:
        if not r.call_start_time:
            continue
        weekday = weekmap[r.call_start_time.weekday()]
        hour = r.call_start_time.hour
        _, range_label = ranges[hour]
        cls = classify_call(r.total_call)
        
        # Initialize dict for this time slot if needed
        if range_label not in data[weekday]:
            data[weekday][range_label] = {"not_answered": 0, "not_interested": 0, "interested": 0}
        
        data[weekday][range_label][cls] += 1

    # Second pass: Convert to percentages and clean up empty slots
    for weekday in list(data.keys()):
        for range_label in list(data[weekday].keys()):
            counts = data[weekday][range_label]
            total = sum(counts.values())
            
            if total > 0:
                # Convert to percentages, keeping all values even if 0
                data[weekday][range_label] = {
                    k: round((v / total) * 100, 2)
                    for k, v in counts.items()
                }
            else:
                # Only remove time slot if all values are 0
                del data[weekday][range_label]
                
        # Remove empty weekdays
        if not data[weekday]:
            del data[weekday]
            
    return data

def count_questions_from_dtmf(dtmf: str) -> int:
    """Old method: count number of comma-separated non-empty entries."""
    if not dtmf:
        return 0
    return sum(1 for p in str(dtmf).split(",") if p.strip() != "")

def calculate_averages(rows):
    """Calculate average call duration and questions answered."""
    durations = [r.total_call for r in rows if getattr(r, "total_call", None) and r.total_call > 0]
    dtmf_counts = [count_questions_from_dtmf(getattr(r, "DTMF", "")) for r in rows if getattr(r, "DTMF", None)]

    return {
        "avg_call_duration": round(statistics.mean(durations), 2) if durations else 0.0,
        "avg_number_of_questions_answered": round(statistics.mean(dtmf_counts), 2) if dtmf_counts else 0.0,
    }

def average_missing_day(all_weekdays):
    """Average across available weekdays to synthesize missing one."""
    ranges = get_time_ranges()
    result = {}
    for _, range_label in ranges:
        values = [all_weekdays[w][range_label] for w in all_weekdays if range_label in all_weekdays[w]]
        if not values:
            result[range_label] = {"not_answered": 0.0, "not_interested": 0.0, "interested": 0.0}
            continue

        avg_counts = {
            "not_answered": statistics.mean(v["not_answered"] for v in values),
            "not_interested": statistics.mean(v["not_interested"] for v in values),
            "interested": statistics.mean(v["interested"] for v in values),
        }

        # normalize
        total = sum(avg_counts.values())
        if total > 0:
            avg_counts = {k: round((v / total) * 100, 2) for k, v in avg_counts.items()}

        result[range_label] = avg_counts
    return result

def fix_missing_days(buckets, old_buckets, window="three_months", fallback_from=None):
    """
    Apply rules:
      - Missing weekdays → average / old data
      - Weekdays with <4 slots → pull from fallback (7d→3m, 3m→old, fallback to average if no old data)
    """
    weekmap = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    existing_days = set(buckets.keys())
    missing_days = [d for d in weekmap if d not in existing_days]

    print(f"Window: {window}")
    print(f"Existing days: {existing_days}")
    print(f"Missing days: {missing_days}")
    print(f"Old buckets keys: {list(old_buckets.keys())} if old_buckets exists: {bool(old_buckets)}")

    # Missing weekdays
    if len(missing_days) == 1:
        buckets[missing_days[0]] = average_missing_day(buckets)
        print(f"Added missing day {missing_days[0]} using average")
    elif len(missing_days) >= 2:
        for md in missing_days:
            if old_buckets and md in old_buckets:
                buckets[md] = old_buckets[md]
                print(f"Added missing day {md} from old_buckets")
            else:
                buckets[md] = average_missing_day(buckets)
                print(f"Added missing day {md} using average")

    # Weak weekdays (<4 slots)
    for wd in weekmap:
        if wd not in buckets:
            continue
        print(f"Checking {wd} with {len(buckets[wd])} slots")
        if len(buckets[wd]) < 4:
            if window == "seven_days" and fallback_from and wd in fallback_from:
                buckets[wd] = fallback_from[wd]
                print(f"Replaced {wd} from fallback_from (three_months)")
            elif window == "three_months" and old_buckets and wd in old_buckets:
                buckets[wd] = old_buckets[wd]
                print(f"Replaced {wd} from old_buckets")
            else:
                buckets[wd] = average_missing_day(buckets)
                print(f"Replaced {wd} using average_missing_day due to missing old_buckets data")

    return buckets

# ---------------- Core Analysis ---------------- #

async def generate_best_times_new():
    """Perform new analysis with fallbacks and missing/weak-day handling."""
    run_id = str(uuid.uuid4())
    print(f"Starting generate_best_times_new with run_id: {run_id}")

    # Load old results
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "analysis_results",
        "best_times.json"
    )
    old_data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                old_data = json.load(f)
            print(f"Successfully loaded old_data from {file_path}: {json.dumps(old_data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"Failed to load JSON from {file_path}: {e}")
            old_data = {}
        except Exception as e:
            print(f"Error accessing {file_path}: {e}")
            old_data = {}
    else:
        print(f"File {file_path} does not exist")

    async with async_session_maker() as session:
        latest_date_result = await session.execute(select(func.max(JobInvite.call_start_time)))
        latest_date = latest_date_result.scalar_one_or_none()
        if not latest_date:
            print("No records in DB. Exiting.")
            return

        # Query cutoff = 3 months
        start_date = latest_date - timedelta(days=cron_days_settings.THREE_MONTHS)
        stmt = select(JobInvite).where(JobInvite.call_start_time >= start_date)

        country_map = defaultdict(list)
        try:
            async for row in (await session.stream(stmt.execution_options(yield_per=1000))).scalars():
                # Normalize country code to string
                country_code = str(row.countryCode)
                country_map[country_code].append(row)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return

        if not country_map:
            print("No new data fetched. Exiting.")
            return

        print(f"Data fetched for countries: {list(country_map.keys())}")

        final_results = {}

        for country, rows in country_map.items():
            final_results[country] = {}
            windows = {
                "three_months": latest_date - timedelta(days=cron_days_settings.THREE_MONTHS),
                "seven_days": latest_date - timedelta(days=cron_days_settings.SEVEN_DAYS),
            }

            for key, cutoff in windows.items():
                print(f"Processing window: {key} for country: {country}")
                window_rows = [r for r in rows if r.call_start_time >= cutoff]
                buckets = bucketize_calls(window_rows)
                avgs = calculate_averages(window_rows)

                # old buckets for fallback, normalize country code
                old_buckets = old_data.get(str(country), {}).get(key, {})
                print(f"Old buckets for {country}/{key}: {json.dumps(old_buckets, indent=2)}")
                fallback_from = final_results[country].get("three_months", {}) if key == "seven_days" else None

                # Apply fix rules
                buckets = fix_missing_days(buckets, old_buckets, window=key, fallback_from=fallback_from)

                # Special case: if 7d completely empty
                if key == "seven_days" and not buckets:
                    buckets = old_buckets or final_results[country].get("three_months", {})

                window_obj = dict(buckets)
                window_obj.update(avgs)
                final_results[country][key] = window_obj

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(final_results, f, default=str, indent=4)

        print(f"Results saved to {file_path} for run_id: {run_id}")
