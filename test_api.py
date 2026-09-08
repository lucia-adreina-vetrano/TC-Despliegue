"""
Prueba local de los endpoints antes de desplegar.

1. Arranca la API en una terminal:
       uvicorn app.main:app --reload

2. En otra terminal, ejecuta este script:
       python test_api.py

Rol sugerido: Persona B, con revisión de Persona A sobre los valores de
entrada esperados por el modelo.
"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_landing_page():
    resp = requests.get(f"{BASE_URL}/")
    print("GET / ->", resp.status_code)
    print(resp.json())
    assert resp.status_code == 200


def test_predict_ok():
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    print("POST /predict (válido) ->", resp.status_code)
    print(resp.json())
    assert resp.status_code == 200


def test_predict_bad_input():
    # Falta un campo a propósito, para comprobar el manejo de errores
    payload = {"sepal_length": 5.1, "sepal_width": 3.5}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    print("POST /predict (incompleto) ->", resp.status_code)
    print(resp.json())
    assert resp.status_code == 422  # error de validación, no un 500


if __name__ == "__main__":
    test_landing_page()
    test_predict_ok()
    test_predict_bad_input()
    print("\nTodos los tests pasaron correctamente.")
