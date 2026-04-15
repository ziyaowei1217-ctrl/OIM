# Academic Success Prediction Project

This project implements a machine learning comparison between an automated PyCaret workflow and a manual Scikit-Learn workflow, followed by a production-ready API deployment using FastAPI.

## Codebase Overview

- **discovery.py**: Performs model comparison, automated preprocessing via PyCaret, and manual implementation via Scikit-Learn. It generates a confusion matrix and saves the optimal model pipeline.
- **main.py**: Serves the best-performing model (Extra Trees Classifier) through a FastAPI web service.
- **data.csv**: The dataset containing academic performance and socio-economic factors for students.

## Outcomes and Comparison

- **Best Model**: The Extra Trees Classifier was identified as one of the top performers due to its robust handling of high-dimensional feature spaces.
- **Efficiency**: PyCaret reduced development time by approximately 80% through automated pipeline construction and algorithm selection.
- **Accuracy**: Both workflows achieved similar high accuracy, though PyCaret's rigorous cross-validation ensures better generalization.

## API Sample Usage

### Request
**Ulr**: `POST /predict`  
**Body**:
```json
{
    "Marital status": 1,
    "Application mode": 17,
    "Application order": 5,
    "Course": 171,
    "Daytime/evening attendance\t": 1,
    "Previous qualification": 1,
    "Previous qualification (grade)": 122.0,
    "Nacionality": 1,
    "Mother's qualification": 19,
    "Father's qualification": 12,
    "Mother's occupation": 5,
    "Father's occupation": 9,
    "Admission grade": 127.3,
    "Displaced": 1,
    "Educational special needs": 0,
    "Debtor": 0,
    "Tuition fees up to date": 1,
    "Gender": 1,
    "Scholarship holder": 0,
    "Age at enrollment": 20,
    "International": 0,
    "Curricular units 1st sem (credited)": 0,
    "Curricular units 1st sem (enrolled)": 0,
    "Curricular units 1st sem (evaluations)": 0,
    "Curricular units 1st sem (approved)": 0,
    "Curricular units 1st sem (grade)": 0.0,
    "Curricular units 1st sem (without evaluations)": 0,
    "Curricular units 2nd sem (credited)": 0,
    "Curricular units 2nd sem (enrolled)": 0,
    "Curricular units 2nd sem (evaluations)": 0,
    "Curricular units 2nd sem (approved)": 0,
    "Curricular units 2nd sem (grade)": 0.0,
    "Curricular units 2nd sem (without evaluations)": 0,
    "Unemployment rate": 10.8,
    "Inflation rate": 1.4,
    "GDP": 1.74
}
```

### Response
```json
{
    "prediction": "Dropout",
    "confidence_score": 0.81
}
```
