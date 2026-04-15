from fastapi import FastAPI
from pycaret.classification import load_model, predict_model
import pandas as pd

# ==========================================
# Part 3: Model Serving (main.py)
# ==========================================

app = FastAPI(title="Academic Success Prediction API")

# Load the saved PyCaret pipeline (best_pipeline.pkl)
model = load_model('best_pipeline')

@app.post("/predict")
def predict(data: dict):
    """
    Endpoint for making predictions.
    Expects a JSON object containing the feature values.
    """
    # Convert input JSON to DataFrame
    df_input = pd.DataFrame([data])
    
    # Generate predictions using PyCaret's pipeline
    predictions = predict_model(model, data=df_input)
    
    # Return result
    # In PyCaret 3.x, prediction results include 'prediction_label' and 'prediction_score'
    label = predictions['prediction_label'][0]
    score = predictions['prediction_score'][0]
    
    return {
        "prediction": str(label),
        "confidence_score": float(score)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)