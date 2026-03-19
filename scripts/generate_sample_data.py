from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

CHANNELS = ["Organic Search", "Paid Ads", "Referral", "Social Media", "Direct"]
COUNTRIES = ["UK", "USA", "Canada", "Germany", "Nigeria"]
DEVICES = ["mobile", "desktop", "tablet"]
LANDING_PAGES = ["/home", "/pricing", "/features", "/blog", "/demo", "/signup"]
SIGNUP_METHODS = ["email", "google", "linkedin"]
PLANS = {
    "Starter": 29.00,
    "Growth": 59.00,
    "Pro": 99.00,
}


def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def random_datetime_on_day(day: date) -> datetime:
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime.combine(day, time(hour, minute, second))


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    users = []
    sessions = []
    events = []
    signups = []
    conversions = []

    num_users = 180
    session_counter = 1
    event_counter = 1
    signup_counter = 1
    conversion_counter = 1

    start_window = date(2024, 1, 1)
    end_window = date(2025, 12, 31)

    for i in range(1, num_users + 1):
        user_id = f"USER{i:04d}"
        first_seen_date = random_date(start_window, end_window)

        acquisition_channel = random.choices(
            population=CHANNELS,
            weights=[0.28, 0.22, 0.14, 0.20, 0.16],
            k=1,
        )[0]
        country = random.choice(COUNTRIES)
        device_type = random.choice(DEVICES)

        did_signup = random.random() < 0.72
        did_activate = False
        did_convert = False

        signup_date = None
        activation_date = None

        if did_signup:
            signup_date = first_seen_date + timedelta(days=random.randint(0, 10))
            did_activate = random.random() < 0.78

            if did_activate:
                activation_date = signup_date + timedelta(days=random.randint(0, 14))
                did_convert = random.random() < 0.48

        users.append(
            {
                "user_id": user_id,
                "first_seen_date": first_seen_date.isoformat(),
                "signup_date": signup_date.isoformat() if signup_date else "",
                "activation_date": activation_date.isoformat() if activation_date else "",
                "acquisition_channel": acquisition_channel,
                "country": country,
                "device_type": device_type,
            }
        )

        num_sessions = random.randint(1, 6)
        user_session_ids = []

        for _ in range(num_sessions):
            session_id = f"SES{session_counter:05d}"
            user_session_ids.append(session_id)

            session_day = first_seen_date + timedelta(days=random.randint(0, 30))
            session_start = random_datetime_on_day(session_day)
            session_end = session_start + timedelta(minutes=random.randint(2, 40))
            landing_page = random.choice(LANDING_PAGES)

            sessions.append(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "session_start": session_start.isoformat(sep=" "),
                    "session_end": session_end.isoformat(sep=" "),
                    "traffic_source": acquisition_channel,
                    "landing_page": landing_page,
                    "device_type": device_type,
                }
            )

            event_sequence = ["page_view"]
            if random.random() < 0.75:
                event_sequence.append("view_pricing")
            if did_signup and random.random() < 0.85:
                event_sequence.append("signup_started")
                event_sequence.append("signup_completed")
            if did_activate and random.random() < 0.80:
                event_sequence.append("activation_completed")
            if did_convert and random.random() < 0.75:
                event_sequence.append("purchase_completed")

            for idx, event_name in enumerate(event_sequence):
                event_time = session_start + timedelta(minutes=idx * random.randint(1, 5) + 1)
                events.append(
                    {
                        "event_id": f"EVT{event_counter:06d}",
                        "session_id": session_id,
                        "user_id": user_id,
                        "event_time": event_time.isoformat(sep=" "),
                        "event_name": event_name,
                        "page_name": landing_page,
                    }
                )
                event_counter += 1

            session_counter += 1

        if did_signup:
            signups.append(
                {
                    "signup_id": f"SUP{signup_counter:05d}",
                    "user_id": user_id,
                    "signup_date": signup_date.isoformat(),
                    "signup_method": random.choice(SIGNUP_METHODS),
                    "signup_status": "completed",
                }
            )
            signup_counter += 1

        if did_convert:
            conversion_date = activation_date + timedelta(days=random.randint(0, 21))
            plan_name = random.choices(
                population=list(PLANS.keys()),
                weights=[0.45, 0.35, 0.20],
                k=1,
            )[0]
            conversions.append(
                {
                    "conversion_id": f"CONV{conversion_counter:05d}",
                    "user_id": user_id,
                    "conversion_date": conversion_date.isoformat(),
                    "conversion_type": "subscription_purchase",
                    "revenue": PLANS[plan_name],
                    "plan_name": plan_name,
                }
            )
            conversion_counter += 1

    pd.DataFrame(users).to_csv(RAW_DIR / "users.csv", index=False)
    pd.DataFrame(sessions).to_csv(RAW_DIR / "sessions.csv", index=False)
    pd.DataFrame(events).to_csv(RAW_DIR / "events.csv", index=False)
    pd.DataFrame(signups).to_csv(RAW_DIR / "signups.csv", index=False)
    pd.DataFrame(conversions).to_csv(RAW_DIR / "conversions.csv", index=False)

    print("Sample CSV files created successfully.")
    print(f"Saved to: {RAW_DIR}")


if __name__ == "__main__":
    main()