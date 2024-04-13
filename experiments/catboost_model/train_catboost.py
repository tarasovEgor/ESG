import os
import sys

import mlflow
import numpy as np
import optuna
from catboost import CatBoostClassifier
from optuna.trial import Trial
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
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run(nested=True) as run:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 1, 10),
            "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1, log=True),
            "silent": trial.suggest_categorical("silent", [True]),
            "task_type": trial.suggest_categorical("task_type", ["GPU"]),
        }

        model = CatBoostClassifier(**params)
        model.fit(X_train, y_train, silent=True)
        y_pred = model.predict(X_test)

        mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
        mlflow.log_metric("f1", f1_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("precision", precision_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("recall", recall_score(y_test, y_pred, average="macro"))
        mlflow.log_params(params)

    return f1_score(y_test, y_pred, average="macro")


def main():
    name, X, y = args.parse_args()
    experiment_name = f"Catboost with {name}"

    with mlflow.start_run(run_name=experiment_name, description=experiment_name) as run:
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=30, n_jobs=1)

        best_params = study.best_params
        name, X, y = args.parse_args()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        clf = CatBoostClassifier(**best_params)
        clf.fit(X_train, y_train, silent=True)
        y_pred = clf.predict(X_test)

        mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
        mlflow.log_metric("f1", f1_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("precision", precision_score(y_test, y_pred, average="macro"))
        mlflow.log_metric("recall", recall_score(y_test, y_pred, average="macro"))
        mlflow.log_params(best_params)

        mlflow.catboost.log_model(clf, "model")
        conf_matrix = ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
        mlflow.log_figure(conf_matrix.figure_, f"Best {experiment_name}.png")


if __name__ == "__main__":
    main()
