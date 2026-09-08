# Team Challenge Final: Despliegue de Modelo

API REST que sirve un modelo de clasificación (Iris, scikit-learn) mediante **FastAPI**, pensada para desplegarse en **Render**.

## Estructura del proyecto

```
TC-Despliegue/
├── app/
│   └── main.py                    # API FastAPI: endpoints "/", "/predict", "/retrain"
├── model/
│   ├── train_model.py             # Script de entrenamiento
│   └── model.pkl                  # Modelo entrenado (se regenera con train_model.py)
├── entrenamiento_modelo.ipynb     # Notebook de exploración y entrenamiento
├── requirements.txt               # Dependencias exactas del proyecto
├── render.yaml                    # Configuración de despliegue en Render
├── test_api.py                    # Pruebas locales de los endpoints
├── .gitignore
└── README.md
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Landing page: cómo usar el resto de endpoints (Swagger también disponible en `/docs`) |
| POST | `/predict` | Endpoint principal: recibe las 4 medidas de la flor y devuelve la predicción |
| POST | `/predict/proba` | **Comentado en el código** — reservado para el redespliegue en directo |

### Contrato de datos — `POST /predict`

```json
// Entrada
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
// Todos los campos: float, mayores que 0

// Salida
{
  "prediction": "setosa",
  "prediction_index": 0
}
```
### Contrato de datos — `POST /retrain` 

Archivo CSV (`multipart/form-data`, campo `file`) con las columnas:
`sepal_length, sepal_width, petal_length, petal_width, target` (target: 0, 1 o 2)

## Cómo correrlo en local

```bash
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt

# 1. Entrenar el modelo (genera/actualiza model/model.pkl)
python model/train_model.py

# 2. Levantar la API
uvicorn app.main:app --reload

# 3. En otra terminal, probar los endpoints
python test_api.py
```

Prueba manual rápida:

```python
import requests

requests.get("http://127.0.0.1:8000/").json()

requests.post("http://127.0.0.1:8000/predict", json={
    "sepal_length": 5.1, "sepal_width": 3.5,
    "petal_length": 1.4, "petal_width": 0.2
}).json()
```

## Control de versiones — Git Flow

Ramas ya creadas en el repositorio:

```
main                          <- código desplegado, solo recibe merges vía PR desde develop
 └── develop                  <- integración de ambas partes
      ├── feature/modelo            (Lucía — modelo y datos)
      ├── feature/api-despliegue    (Nil — API y despliegue)
      └── feature/predict-proba     (reservada para el redespliegue en directo)
```

## Despliegue en Render

1. El repositorio ya está en GitHub con la estructura anterior.
2. En [render.com](https://render.com) → **New +** → **Web Service** → conectar el repo, rama `main`.
3. Render detecta `render.yaml` automáticamente, o configurar a mano:
   - **Build Command**: `pip install -r requirements.txt && python model/train_model.py`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Deploy. La URL pública tendrá la forma `https://tc-despliegue.onrender.com`.
5. Probar desde Python: `requests.get("https://tu-url.onrender.com/")`.

**Antes de la presentación**: abrir la propia URL un par de minutos antes (el plan free "duerme" tras 15 min de inactividad) o configurar [cron-job.org](https://cron-job.org) para hacer ping cada 10-14 min.

## Redespliegue en directo

El endpoint `/predict/proba` está ya escrito pero comentado en `app/main.py`, en la rama `feature/predict-proba`. El día de la presentación:

```bash
git switch feature/predict-proba
git pull origin develop          # traer cualquier cambio reciente de develop
# descomentar el bloque /predict/proba en app/main.py
git add app/main.py
git commit -m "feat: add /predict/proba endpoint"
git push origin feature/predict-proba
# abrir PR feature/predict-proba -> main en GitHub, hacer merge en directo delante de la clase
```

Render redespliega automáticamente al hacer merge a `main` (si el auto-deploy está activado en la configuración del servicio).

## Reparto de roles (equipo de 2)

| | **Lucía Vetrano — Modelo & Datos** | **Nil Coronado — API & Despliegue** |
|---|---|---|
| Entrenamiento | `model/train_model.py`, notebook de exploración | — |
| Contrato de datos | Definir campos y tipos que necesita el modelo | Adaptar el esquema `IrisInput` (Pydantic) a ese contrato |
| Endpoint principal | Validar que la predicción es correcta | Implementar `POST /predict` en `app/main.py` |
| Landing page | — | Implementar `GET /` con la info de endpoints |
| Redespliegue en directo | Definir qué nueva funcionalidad mostrar | Dejarlo comentado y listo, ensayar el flujo de PR + merge |
| Extra voluntario (reentrenamiento) | Definir formato del CSV de reentrenamiento | Implementar `POST /retrain` |
| Testing local | Revisar que las predicciones tienen sentido | Escribir/ejecutar `test_api.py` |
| Despliegue en Render | — | Configurar `render.yaml`, variables de entorno, cron-job.org |
| Git / repo | Rama `feature/modelo`, PR a `develop` | Rama `feature/api-despliegue`, PR final `develop → main` |
| Presentación | Explicar el modelo y sus métricas | Hacer la demo en vivo de los endpoints y el redespliegue |

## Checklist de entregables

- [x] Repositorio con ramas `main` / `develop` / `feature/*`
- [x] `requirements.txt` correcto
- [ ] URL pública funcionando con `GET /` y `POST /predict`
- [x] Tercer endpoint comentado, listo para descomentar (`feature/predict-proba`)
- [x] Manejo de errores (422 ante datos incompletos, no 500)
- [ ] Despliegue verificado en Render
- [x] `/retrain` funcionando (extra voluntario)
- [ ] Demo ensayada, servicio "despertado" antes de presentar
