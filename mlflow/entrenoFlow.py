import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# Cojo datos y los divido para entrenar.
df_energia = pd.read_csv("df_energia_limpio.csv")

columnas_entrada = [
"anio",
"temperatura_media",
"viento_media",
"turismo_alto",
"mes_sin",
"mes_cos",
]

X, y = df_energia[columnas_entrada], df_energia["Energia_consumida"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Aquí establezco los parámetros de MLFlow.
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Energía Tenerife 4 - Random Forest")

# Al igual que vimos con el CVGridSearch, pongo unos cuántos valores de hiperparámetros.
max_depths = [None, 5, 10]
min_splits = [2, 5, 10]
n_estimators = [10, 50]
min_samples_leafs = [1, 2, 4]

columnas_a_escalar = ["anio", "temperatura_media", "viento_media", "turismo_alto"]
columnas_no_escalar = ["mes_sin", "mes_cos"]

preprocessor = ColumnTransformer(
    transformers=[
        ('scaler', StandardScaler(), columnas_a_escalar),
        ('passthrough', 'passthrough', columnas_no_escalar)  # No tocar estas
    ]
)


# Ahora simulo un poco lo que hace dicha clase.
# Lanzo todas las combinaciones...
for max_depth in max_depths:
    for min_samples_split in min_splits:
        for n_estimator in n_estimators:
            for min_samples_leaf in min_samples_leafs:

                # ... y las logueo.
                run_name = (
                    f"Lanzamiento de Random Forest, con profundidad_hoja={max_depth} y "
                    f" split={min_samples_split}"
                )

                # Iniciamos experimento
                with mlflow.start_run(run_name=run_name):

                    pipeline = Pipeline([
                        ('preprocessor', preprocessor),
                        ('forest', RandomForestRegressor(
                            max_depth=max_depth,
                            min_samples_split=min_samples_split,
                            n_estimators=n_estimator,
                            min_samples_leaf=min_samples_leaf,
                            random_state=42
                        ))
                    ])
                    
                    # Entrenar el pipeline (automáticamente escala solo las columnas necesarias)
                    pipeline.fit(X_train, y_train)

                    # Aquí predigo
                    y_pred = pipeline.predict(X_test)

                    # Saco las métricas
                    mse = mean_squared_error(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)   

                    # Miro a ver si hay sobreajuste
                    train_mse = mean_squared_error(y_train, pipeline.predict(X_train))
                    mse_gap = train_mse - mse

                    # Logueo estos parámetros
                    mlflow.log_param("modelo", "Random Forest")
                    mlflow.log_param("max_depth", str(max_depth)) # así evito que pete, porque puede ser None
                    mlflow.log_param("min_samples_split", min_samples_split)
                    mlflow.log_param("test_size", 0.2)
                    mlflow.log_param("random_state", 42)

                    # Logueo las métricas
                    mlflow.log_metric("test_mse", float(mse))
                    mlflow.log_metric("test_mae", float(mae))
                    mlflow.log_metric("test_r2", float(r2))


                    # Miro el sobreajuste (error entreno - error validación)
                    mlflow.log_metric("train_mse", float(train_mse))
                    mlflow.log_metric("mse_gap", float(mse_gap))

                    # Se guarda el modelo como artefacto (.pkl + metadatos...)
                    # Aquí NO LO REGISTRO. Lo podría registrar con registered_model_name
                    mlflow.sklearn.log_model(pipeline, name="modelo", input_example=X_test.sample())

                    print(
                        run_name,
                        f"test_mse={mse:.4f}",
                        f"test_mae={mae:.4f}",
                        f"test_r2={r2:.4f}"
                    )