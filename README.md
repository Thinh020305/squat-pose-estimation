# Squat Pose Coach MVC

## Structure

```text
app.py
wsgi.py
main.py
backend/
  controllers/
  models/
  services/
  database/
    db.py
    squat_coach.sqlite3
  utils/
frontend/
  templates/
  static/
  uploads/
ml_models/
  squat_error_model.pkl
  squat_random_forest_model.pkl
data/
  squat_features_augmented.csv
requirements.txt
```

## Run

```powershell
cd C:\Users\Admin\Documents\Squat_pose_estimation
.\.venv\Scripts\python.exe main.py
```

The browser opens at `http://127.0.0.1:5000`.

## Train SVM

```powershell
.\.venv\Scripts\python.exe -m backend.services.train_svm
```

Model: `ml_models/squat_error_model.pkl`

## Train Random Forest

```powershell
.\.venv\Scripts\python.exe -m backend.services.train_random_forest
```

Model: `ml_models/squat_random_forest_model.pkl`

Dataset: `data/squat_features_augmented.csv`

AI runtime priority: Random Forest first, then SVM fallback if Random Forest has not been trained.

Runtime database: `backend/database/squat_coach.sqlite3`
