from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler
import mlflow
import pandas as pd
import numpy as np
import os

from dotenv import load_dotenv
load_dotenv()

os.environ['DATABRICKS_HOST'] = os.getenv('DATABRICKS_HOST')
os.environ['DATABRICKS_TOKEN'] = os.getenv('DATABRICKS_TOKEN')

mlflow.set_tracking_uri("databricks")

URL_MODELO = "models:/workspace.default.energia_tenerife/1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.modelo = mlflow.sklearn.load_model(URL_MODELO)
        print("Modelo cargado desde MLflow")
    except Exception as e:
        print("Error cargando el modelo:", e)
        app.state.modelo = None

    yield
    
    print("Aplicación detenida")

# -----------------------
# App
# -----------------------
app = FastAPI(
    title="API Modelo Energia",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)


class InputData(BaseModel):
    anio: int
    temperatura_media: float
    viento_media: float
    turismo_alto: int
    mes: int
    

@app.get("/health")
def health():
    if app.state.modelo is None:
        return {"status": "error", "message": "Modelo no cargado"}
    
    return {"status": "ok"}
    
    
@app.post("/predict")
def predict(data: InputData):
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
    
    # Predecir
    prediction = app.state.modelo.predict(df)
    
    return {
        "anio": data.anio,
        "mes": data.mes,
        "prediction": prediction[0]
    }


