from __future__ import annotations

import _bootstrap  # noqa: F401

from product_funnel.quality import run_quality_checks


def main() -> None:
    results = run_quality_checks(write_report=True)
    for result in results:
        print(
            f"{result.status.upper():4} | {result.severity:8} | "
            f"{result.name}: {result.failing_rows} failing row(s)"
        )

    failed = [result for result in results if result.status == "fail" and result.severity == "critical"]
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
