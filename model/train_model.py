
import joblib
from pathlib import Path

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_PATH = Path(__file__).parent / "model.pkl"


def train_and_save_model(output_path: Path = MODEL_PATH) -> None:
    data = load_iris()
    X, y = data.data, data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"Accuracy en test: {acc:.4f}")

    # Guardamos el modelo junto con los nombres de las clases,
    # así el endpoint no depende de tener sklearn.datasets disponible.
    bundle = {
        "model": model,
        "target_names": list(data.target_names),
        "feature_names": list(data.feature_names),
    }
    joblib.dump(bundle, output_path)
    print(f"Modelo guardado en: {output_path}")


if __name__ == "__main__":
    train_and_save_model()
