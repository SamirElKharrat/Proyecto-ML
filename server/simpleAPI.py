from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler

import mlflow
import pandas as pd
import numpy as np


mlflow.set_tracking_uri("http://127.0.0.1:5000")# la URL de MLFLOW. Aquí es local, pero si estuviese en la nube...

URL_MODELO = "models:/prueba/1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Antes del yield se lanzará al iniciar el server
    # cargamos el modelo con pickle
    try:
        app.state.modelo = mlflow.sklearn.load_model(URL_MODELO)
        print("Modelo cargado desde MLflow")
    except Exception as e:
        print("Error cargando el modelo:", e)
        app.state.modelo = None

    yield

    # Esto se lanzará cuando apaguemos el server.
    print("Aplicación detenida")

# -----------------------
# App
# -----------------------
app = FastAPI(
    title="API Modelo Energia",
    lifespan=lifespan
)


class InputData(BaseModel):
    anio: int
    temperatura_media: float
    viento_media: float
    turismo_alto: int
    mes: int
    
    
@app.post("/predict")
def predict(data: InputData):
    if app.state.modelo is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    
    # Calculo el sin y cos del mes
    mes_sin = np.sin(2 * np.pi * data.mes / 12)
    mes_cos = np.cos(2 * np.pi * data.mes / 12)
    
    # Creamos el dataframe
    df = pd.DataFrame([{
        "anio": data.anio,
        "temperatura_media": data.temperatura_media,
        "viento_media": data.viento_media,
        "turismo_alto": data.turismo_alto,
        "mes_sin": mes_sin,
        "mes_cos": mes_cos
    }])

    
    print(df)
    
    # Predecir
    prediction = app.state.modelo.predict(df)
    
     # Ver qué pasa internamente
    if hasattr(app.state.modelo, 'named_steps'):
        # Es un pipeline
        print("Pipeline steps:", app.state.modelo.named_steps.keys())
        # Ver la transformación
        transformed = app.state.modelo.named_steps['preprocessor'].transform(df)
        print("Datos escalados:", transformed)
    
    
    print("Prediction:", prediction)

    
    return {
        "anio": data.anio,
        "mes": data.mes,
        "prediction": prediction[0]
    }


