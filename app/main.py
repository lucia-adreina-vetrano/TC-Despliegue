"""
API de despliegue del modelo - Team Challenge.

Endpoints:
    GET  /            -> landing page: cómo usar la API
    POST /predict      -> predicción del modelo (endpoint principal)
    POST /predict/proba -> [COMENTADO] endpoint de reserva para el
                            redespliegue en directo durante la presentación
    POST /retrain      -> [EXTRA VOLUNTARIO] reentrenamiento del modelo
                           con un dataset nuevo

Rol sugerido: Persona B (API / estructura / despliegue), en colaboración
con Persona A para el contrato de datos de entrada del modelo.
"""

from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Carga del modelo
# ---------------------------------------------------------------------------

MODEL_PATH = Path(__file__).parent.parent / "model" / "model.pkl"

app = FastAPI(
    title="Team Challenge - Despliegue de Modelo",
    description="API de ejemplo para el Team Challenge Final de despliegue.",
    version="1.0.0",
)

_bundle = None


def get_model_bundle():
    """Carga perezosa del modelo (evita fallos si el .pkl no existe aún al importar)."""
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail=(
                    "El modelo no está disponible en el servidor. "
                    "Ejecuta model/train_model.py antes de arrancar la API."
                ),
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


# ---------------------------------------------------------------------------
# Esquemas de entrada / salida (validación automática con Pydantic)
# ---------------------------------------------------------------------------

class IrisInput(BaseModel):
    sepal_length: float = Field(..., gt=0, description="Longitud del sépalo en cm")
    sepal_width: float = Field(..., gt=0, description="Anchura del sépalo en cm")
    petal_length: float = Field(..., gt=0, description="Longitud del pétalo en cm")
    petal_width: float = Field(..., gt=0, description="Anchura del pétalo en cm")

    class Config:
        json_schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        }


class PredictionOutput(BaseModel):
    prediction: str
    prediction_index: int


# ---------------------------------------------------------------------------
# Endpoint 1: landing page ("/")
# ---------------------------------------------------------------------------

@app.get("/", tags=["Info"])
def read_root():
    """Landing page: explica cómo usar el resto de endpoints."""
    return {
        "mensaje": "API de despliegue del modelo - Team Challenge",
        "documentacion_interactiva": "/docs",
        "endpoints": {
            "GET /": "Esta página. Información general de la API.",
            "POST /predict": (
                "Endpoint principal. Envía un JSON con los 4 campos "
                "(sepal_length, sepal_width, petal_length, petal_width) "
                "y devuelve la predicción del modelo."
            ),
            "POST /retrain": (
                "[Extra voluntario] Sube un CSV con nuevos datos de "
                "entrenamiento y reentrena el modelo."
            ),
        },
        "ejemplo_predict": {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    }


# ---------------------------------------------------------------------------
# Endpoint 2: predicción (endpoint principal)
# ---------------------------------------------------------------------------

@app.post("/predict", response_model=PredictionOutput, tags=["Modelo"])
def predict(data: IrisInput):
    """
    Devuelve la predicción del modelo para las 4 medidas de la flor.

    FastAPI + Pydantic validan automáticamente los datos de entrada:
    si falta un campo o el tipo no es correcto, se devuelve un 422
    con un mensaje claro, sin llegar a ejecutar el modelo.
    """
    bundle = get_model_bundle()
    model = bundle["model"]
    target_names = bundle["target_names"]

    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width,
    ]]

    try:
        pred_index = int(model.predict(features)[0])
        pred_label = target_names[pred_index]
    except Exception as exc:
        # Manejo de errores: nunca dejamos que salte un 500 críptico
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo generar la predicción: {exc}",
        )

    return PredictionOutput(prediction=pred_label, prediction_index=pred_index)


# ---------------------------------------------------------------------------
# Endpoint 3: PREPARADO PARA EL REDESPLIEGUE EN DIRECTO
# ---------------------------------------------------------------------------
# Descomentar este bloque, hacer commit/push (o merge del PR preparado) y
# redesplegar en Render durante la presentación. Devuelve las probabilidades
# de cada clase, no solo la etiqueta ganadora.
#
# class ProbaOutput(BaseModel):
#     probabilities: dict
#
# @app.post("/predict/proba", response_model=ProbaOutput, tags=["Modelo"])
# def predict_proba(data: IrisInput):
#     bundle = get_model_bundle()
#     model = bundle["model"]
#     target_names = bundle["target_names"]
#
#     features = [[
#         data.sepal_length,
#         data.sepal_width,
#         data.petal_length,
#         data.petal_width,
#     ]]
#
#     try:
#         proba = model.predict_proba(features)[0]
#     except Exception as exc:
#         raise HTTPException(
#             status_code=400,
#             detail=f"No se pudieron calcular las probabilidades: {exc}",
#         )
#
#     return ProbaOutput(
#         probabilities={name: float(p) for name, p in zip(target_names, proba)}
#     )


# ---------------------------------------------------------------------------
# Extra voluntario: reentrenamiento del modelo vía endpoint
# ---------------------------------------------------------------------------

@app.post("/retrain", tags=["Extra"])
async def retrain(file: UploadFile = File(...)):
    """
    [Extra voluntario] Reentrena el modelo añadiendo un nuevo dataset.

    Espera un CSV con las columnas:
        sepal_length, sepal_width, petal_length, petal_width, target
    donde 'target' es el índice de clase (0, 1 o 2).

    El nuevo CSV se guarda en model/data/ (para quedar versionado en el
    repo si se hace commit) y se reentrena el modelo con el dataset
    original + el nuevo.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .csv")

    try:
        df_new = pd.read_csv(file.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"CSV inválido: {exc}")

    required_cols = {"sepal_length", "sepal_width", "petal_length", "petal_width", "target"}
    if not required_cols.issubset(df_new.columns):
        raise HTTPException(
            status_code=422,
            detail=f"El CSV debe contener las columnas: {sorted(required_cols)}",
        )

    from sklearn.datasets import load_iris
    from sklearn.ensemble import RandomForestClassifier

    data = load_iris()
    X_original = pd.DataFrame(data.data, columns=[
        "sepal_length", "sepal_width", "petal_length", "petal_width"
    ])
    y_original = pd.Series(data.target)

    X_combined = pd.concat([X_original, df_new[[
        "sepal_length", "sepal_width", "petal_length", "petal_width"
    ]]], ignore_index=True)
    y_combined = pd.concat([y_original, df_new["target"]], ignore_index=True)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_combined, y_combined)

    bundle = {
        "model": model,
        "target_names": list(data.target_names),
        "feature_names": list(data.feature_names),
    }
    joblib.dump(bundle, MODEL_PATH)

    global _bundle
    _bundle = bundle  # refrescamos el modelo en memoria sin reiniciar el servidor

    return JSONResponse(
        content={
            "mensaje": "Modelo reentrenado correctamente",
            "filas_nuevas_anadidas": len(df_new),
            "filas_totales_entrenamiento": len(X_combined),
        }
    )
