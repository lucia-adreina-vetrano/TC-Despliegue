# Team Challenge Final: Despliegue de Modelo

API REST que sirve un modelo de clasificación (Iris, scikit-learn) mediante **FastAPI**, pensada para desplegarse en **Render**.

## Estructura del proyecto

```
team_challenge_despliegue/
├── app/
│   └── main.py           # API FastAPI: endpoints "/", "/predict", "/retrain"
├── model/
│   ├── train_model.py    # Script de entrenamiento
│   └── model.pkl         # Modelo entrenado (se genera al ejecutar train_model.py)
├── requirements.txt
├── render.yaml            # Configuración de despliegue en Render
├── test_api.py             # Pruebas locales con requests
├── .gitignore
└── README.md
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Landing page: cómo usar la API (equivale a "/docs" también disponible) |
| POST | `/predict` | Endpoint principal: recibe las 4 medidas de la flor y devuelve la predicción |
| POST | `/predict/proba` | **Comentado en el código** — listo para descomentar y redesplegar en directo |
| POST | `/retrain` | Extra voluntario: sube un CSV nuevo y reentrena el modelo |

La documentación interactiva (Swagger) está disponible automáticamente en `/docs`.

## Cómo correrlo en local

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt

# 1. Entrenar el modelo (genera model/model.pkl)
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

## Despliegue en Render

1. Sube este proyecto a un repositorio de GitHub (rama `main`).
2. En [render.com](https://render.com) → **New +** → **Web Service** → conecta el repo.
3. Render detecta `render.yaml` automáticamente, o configura a mano:
   - **Build Command**: `pip install -r requirements.txt && python model/train_model.py`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Deploy. La URL pública tendrá la forma `https://team-challenge-despliegue.onrender.com`.
5. Prueba desde Python: `requests.get("https://tu-url.onrender.com/")`.

**Antes de la presentación**: abre tu propia URL un par de minutos antes (el plan free "duerme" tras 15 min de inactividad) o configura [cron-job.org](https://cron-job.org) para hacer ping cada 10-14 min.

## Redespliegue en directo

El endpoint `/predict/proba` está ya escrito pero comentado en `app/main.py`. Para la demo:

```bash
git switch -c feature/predict-proba
# descomentar el bloque en app/main.py
git add app/main.py
git commit -m "feat: add /predict/proba endpoint"
git push -u origin feature/predict-proba
# abrir PR feature/predict-proba -> main en GitHub, hacer merge en directo
```

Render redespliega automáticamente al hacer push/merge a `main` (si el auto-deploy está activado en la configuración del servicio).

## Reparto de roles (equipo de 2)

| | **Persona A — Modelo & Datos** | **Persona B — API & Despliegue** |
|---|---|---|
| Entrenamiento | `model/train_model.py`, elegir/ajustar el modelo | — |
| Contrato de datos | Definir qué campos necesita el modelo y sus tipos | Traducirlo al esquema `IrisInput` (Pydantic) |
| Endpoint principal | Validar que la predicción es correcta | Implementar `POST /predict` en `app/main.py` |
| Landing page | — | Implementar `GET /` con la info de endpoints |
| Endpoint del redespliegue en directo | Definir qué nueva funcionalidad mostrar (ej. probabilidades) | Dejarlo comentado y listo, ensayar el flujo de PR + merge |
| Extra voluntario (reentrenamiento) | Definir formato del CSV de reentrenamiento | Implementar `POST /retrain` |
| Testing local | Revisar que las predicciones tienen sentido | Escribir/ejecutar `test_api.py` |
| Despliegue en Render | — | Configurar `render.yaml`, variables de entorno, cron-job.org |
| Git / repo | Rama `feature/modelo`, PRs de su parte | Rama `feature/api-despliegue`, gestión de `main`/`develop`, mergea PRs |
| Presentación | Explicar el modelo y sus métricas | Hacer la demo en vivo de los endpoints y el redespliegue |

Sugerencia de ramas Git Flow (ver también los talleres):

```
main        <- solo vía PR, es lo que está desplegado
develop     <- integración
feature/modelo              (Persona A)
feature/api-despliegue      (Persona B)
feature/predict-proba       (preparada para el redespliegue en directo)
```

## Checklist de entregables

- [ ] Repositorio con `main`/`develop`/`feature` branches
- [ ] `requirements.txt` correcto y probado desde cero
- [ ] URL pública funcionando con `GET /` y `POST /predict`
- [ ] Tercer endpoint comentado, listo para descomentar
- [ ] Manejo de errores (probar con JSON incompleto/mal formado)
- [ ] Variables de entorno (si aplica) configuradas en Render, no en el código
- [ ] (Opcional) `/retrain` funcionando
- [ ] Demo ensayada, servicio "despertado" antes de presentar
