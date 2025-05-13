import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
import joblib

class CreditScoringModel:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.models = {
            'Logistic Regression': LogisticRegression(),
            'Random Forest': RandomForestClassifier(),
            'XGBoost': XGBClassifier()
        }
        self.best_models = {}
        self.results = {}
        
        # Configuración de visualización
        plt.style.use('ggplot')
        sns.set_palette("husl")
        
    def load_data(self):
        """Carga y prepara los datos"""
        print("\n=== Cargando y preparando datos ===")
        self.df = pd.read_csv(self.file_path, sep=';', decimal='.')
        self.df['tipo'] = self.df['tipo'].replace({'Otro': 'Nuevo', 'Nuevo': 'Nuevo', 'Renovado': 'Renovado'})
        print(f"Datos cargados: {self.df.shape[0]} registros, {self.df.shape[1]} columnas")
        return self
        
    def eda(self):
        """Análisis exploratorio de datos"""
        print("\n=== Realizando análisis exploratorio ===")
        
        # Segmentación de datos
        nuevos = self.df[self.df['tipo'] == 'Nuevo']
        renovados = self.df[self.df['tipo'] == 'Renovado']
        
        # Visualización distribución del target
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        sns.countplot(data=nuevos, x='atraso_30', ax=ax[0])
        ax[0].set_title('Distribución de Default - Nuevos')
        sns.countplot(data=renovados, x='atraso_30', ax=ax[1])
        ax[1].set_title('Distribución de Default - Renovados')
        plt.show()
        
        # Análisis correlaciones
        print("\nCorrelaciones con target (Nuevos):")
        print(nuevos.corr(numeric_only=True)['atraso_30'].sort_values(ascending=False).head(5))
        print("\nCorrelaciones con target (Renovados):")
        print(renovados.corr(numeric_only=True)['atraso_30'].sort_values(ascending=False).head(5))
        
        return self
    
    def preprocess_data(self):
        """Preprocesamiento de datos"""
        print("\n=== Preprocesando datos ===")
        
        # Definición de variables
        self.features = [
            'edad', 'monto_solicitado', 'cant_cuotas', 'ingreso',
            'antiguedad_laboral', 'promedio_atraso_negofin',
            'maximo_atraso_negofin', 'sexo', 'estado_civil', 'tipo_sucursal'
        ]
        
        self.target = 'atraso_30'
        
        # Transformadores
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), ['edad', 'monto_solicitado', 'cant_cuotas', 
                                         'ingreso', 'antiguedad_laboral',
                                         'promedio_atraso_negofin', 'maximo_atraso_negofin']),
                ('cat', OneHotEncoder(handle_unknown='ignore'), ['sexo', 'estado_civil', 'tipo_sucursal'])
            ])
        
        return self
    
    def train_models(self):
        """Entrenamiento de modelos por segmento"""
        print("\n=== Entrenando modelos ===")
        
        for grupo in ['Nuevo', 'Renovado']:
            print(f"\n--- Entrenando para grupo: {grupo} ---")
            df_group = self.df[self.df['tipo'] == grupo]
            X = df_group[self.features]
            y = df_group[self.target]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y)
            
            resultados = {}
            best_auc = 0
            best_model = None
            
            for name, model in self.models.items():
                # Pipeline
                pipeline = Pipeline(steps=[
                    ('preprocessor', self.preprocessor),
                    ('model', model)
                ])
                
                # Entrenamiento
                pipeline.fit(X_train, y_train)
                
                # Evaluación
                y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
                auc = roc_auc_score(y_test, y_pred_proba)
                resultados[name] = auc
                
                # Mejor modelo
                if auc > best_auc:
                    best_auc = auc
                    best_model = pipeline
                    
                print(f"{name}: AUC = {auc:.4f}")
            
            self.results[grupo] = resultados
            self.best_models[grupo] = best_model
            print(f"\nMejor modelo para {grupo}: {best_model.named_steps['model'].__class__.__name__} (AUC = {best_auc:.4f})")
        
        return self
    
    def save_models(self):
        """Guarda los mejores modelos"""
        print("\n=== Guardando modelos ===")
        for grupo, modelo in self.best_models.items():
            filename = f"mejor_modelo_{grupo.lower()}.pkl"
            joblib.dump(modelo, filename)
            print(f"Modelo guardado como: {filename}")
        return self
    
    def show_results(self):
        """Muestra los resultados finales"""
        print("\n=== Resultados Finales ===")
        resultados_df = pd.DataFrame(self.results).T
        print(resultados_df)
        return self

if __name__ == "__main__":
    # Ejecución completa del proceso
    pipeline = (
        CreditScoringModel('bd_consumo_muestra.csv')
        .load_data()
        .eda()
        .preprocess_data()
        .train_models()
        .show_results()
        .save_models()
    )