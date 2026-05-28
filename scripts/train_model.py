from __future__ import annotations

import _bootstrap  # noqa: F401

from product_funnel.modeling import train_conversion_models


def main() -> None:
    results = train_conversion_models()
    print(f"Best model: {results['best_model']}")
    print(f"Model artifact: {results['model_path']}")
    print(f"Score output: {results['scores_path']}")


if __name__ == "__main__":
    main()
