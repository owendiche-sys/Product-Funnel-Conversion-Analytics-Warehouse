from __future__ import annotations

import _bootstrap  # noqa: F401

from product_funnel.pipeline import run_pipeline


def main() -> None:
    results = run_pipeline(generate_data=True, train_model=True)
    print(f"Pipeline completed successfully: {results['database_path']}")
    print(f"Quality checks: {len(results['quality_checks'])}")
    if results["model"]:
        print(f"Best model: {results['model']['best_model']}")
        print(f"Scores: {results['model']['scores_path']}")


if __name__ == "__main__":
    main()
