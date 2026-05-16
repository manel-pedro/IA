import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Load data
data = pd.read_csv("dataSet.csv")

y = data["Grade"]
X = data.drop(["Grade", "Student_ID"], axis=1)

categorical_cols = X.columns

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
    ]
)

model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("clf", RandomForestClassifier(n_estimators=200, random_state=123))
])

model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model saved successfully!")