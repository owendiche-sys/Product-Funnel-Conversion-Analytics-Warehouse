from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from product_funnel.database import query_dataframe
from product_funnel.paths import report_dir


@dataclass
class QualityCheck:
    name: str
    status: str
    failing_rows: int
    severity: str
    description: str


CHECKS = [
    (
        "users_unique",
        "SELECT COUNT(*) AS failing_rows FROM (SELECT user_id FROM raw_users GROUP BY user_id HAVING COUNT(*) > 1)",
        "critical",
        "User IDs should be unique.",
    ),
    (
        "sessions_have_users",
        "SELECT COUNT(*) AS failing_rows FROM raw_sessions s LEFT JOIN raw_users u ON s.user_id = u.user_id WHERE u.user_id IS NULL",
        "critical",
        "Every session should map to an existing user.",
    ),
    (
        "events_have_sessions",
        "SELECT COUNT(*) AS failing_rows FROM raw_events e LEFT JOIN raw_sessions s ON e.session_id = s.session_id WHERE s.session_id IS NULL",
        "critical",
        "Every event should map to an existing session.",
    ),
    (
        "signup_after_first_seen",
        "SELECT COUNT(*) AS failing_rows FROM stg_users WHERE signup_date IS NOT NULL AND signup_date < first_seen_date",
        "critical",
        "Signup date should not precede first seen date.",
    ),
    (
        "activation_after_signup",
        "SELECT COUNT(*) AS failing_rows FROM stg_users WHERE activation_date IS NOT NULL AND signup_date IS NOT NULL AND activation_date < signup_date",
        "critical",
        "Activation date should not precede signup date.",
    ),
    (
        "conversion_after_activation",
        "SELECT COUNT(*) AS failing_rows FROM stg_conversions c JOIN stg_users u ON c.user_id = u.user_id WHERE u.activation_date IS NOT NULL AND c.conversion_date < u.activation_date",
        "warning",
        "Conversion date should not precede activation date.",
    ),
    (
        "revenue_non_negative",
        "SELECT COUNT(*) AS failing_rows FROM stg_conversions WHERE revenue < 0",
        "critical",
        "Revenue should be non-negative.",
    ),
]


def run_quality_checks(write_report: bool = True) -> list[QualityCheck]:
    results: list[QualityCheck] = []
    for name, query, severity, description in CHECKS:
        failing_rows = int(query_dataframe(query).iloc[0]["failing_rows"])
        results.append(
            QualityCheck(
                name=name,
                status="pass" if failing_rows == 0 else "fail",
                failing_rows=failing_rows,
                severity=severity,
                description=description,
            )
        )

    if write_report:
        output_path = report_dir() / "data_quality_report.json"
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump([asdict(result) for result in results], file, indent=2)

    return results
