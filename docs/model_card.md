# Model Card: Conversion Propensity Model

## Intended Use

The model estimates the probability that a user will convert based on acquisition attributes, product behavior, and funnel progression signals. It is designed for portfolio demonstration, growth analytics exploration, and prioritization analysis.

## Prediction Target

- Target variable: `did_convert`
- Positive class: user has at least one conversion record.
- Unit of prediction: user.

## Features

The model uses:

- Acquisition channel.
- Country.
- Device type.
- Signup method.
- Session count and duration.
- Event count.
- Pricing views.
- Signup and activation event counts.
- Days to signup.
- Days to activation.
- Signup and activation flags.

## Algorithms

The training script compares:

- Logistic regression.
- Random forest classifier.

The best model is selected by ROC AUC and saved to `models/conversion_propensity_model.pkl`.

## Evaluation

Metrics are written to `reports/model_metrics.json`:

- Accuracy.
- Precision.
- Recall.
- F1 score.
- ROC AUC.

## Limitations

The dataset is simulated, so model performance should not be interpreted as production evidence. Some features, such as activation status, may create leakage depending on the real-world prediction timing. In a production version, the feature set should be restricted to events available before the intended scoring moment.

## Recommended Next Steps

- Add a strict scoring cutoff date.
- Compare models with cross-validation.
- Add calibration checks.
- Track feature importance or SHAP explanations.
- Save experiment metadata for repeatability.
