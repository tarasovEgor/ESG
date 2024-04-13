import os
import sys

import mlflow
import numpy as np
import optuna
from optuna.trial import Trial
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

PATH = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)), "common")
sys.path.append(PATH)
import args


def objective(trial: Trial) -> float:
    name, X, y = args.parse_args()

    with mlflow.start_run(nested=True) as run:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Define hyperparameters to optimize
        params = {
            "loss": trial.suggest_categorical("loss", ["log_loss"]),
            "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2"]),
        }

        # Train model with hyperparameters
        model = GradientBoostingClassifier(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Log metrics
        mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
        mlflow.log_metric("f1", f1_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("precision", precision_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("recall", recall_score(y_test, y_pred, average="macro"))
        mlflow.log_params(params)

    return f1_score(y_test, y_pred, average="macro")


def main():
    name, X, y = args.parse_args()
    experiment_name = f"GradientBoostingClassifier with {name}"

    with mlflow.start_run(run_name=experiment_name, description=experiment_name) as run:
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=30, n_jobs=-1)

        best_params = study.best_params
        name, X, y = args.parse_args()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = GradientBoostingClassifier(**best_params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
        mlflow.log_metric("f1", f1_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("precision", precision_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("recall", recall_score(y_test, y_pred, average="macro"))
        mlflow.log_params(best_params)

        mlflow.sklearn.log_model(model, "model")
        conf_matrix = ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
        mlflow.log_figure(conf_matrix.figure_, f"Best {experiment_name}.png")


if __name__ == "__main__":
    main()
