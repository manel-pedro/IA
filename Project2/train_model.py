import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Extra models (boosting)
from xgboost import XGBClassifier
from catboost import CatBoostClassifier

# Load data
data = pd.read_csv("Student_performance_data.csv")

# Target
y = data["GradeClass"]

# Features
X = data.drop(["GradeClass", "GPA", "StudentID"], axis=1)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=123,
    stratify=y
)

# Columns
categorical_cols = ["Gender", "Ethnicity"]

binary_cols = [
    "Tutoring", "ParentalSupport", "Extracurricular",
    "Sports", "Music", "Volunteering"
]

numerical_cols = ["Age", "ParentalEducation", "StudyTimeWeekly", "Absences"]

# Preprocessing
preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", "passthrough", numerical_cols),
        ("bin", "passthrough", binary_cols)
    ]
)

# Models
models = {
    "random_forest": RandomForestClassifier(n_estimators=200, random_state=123),
    "extra_trees": ExtraTreesClassifier(random_state=123),
    "decision_tree": DecisionTreeClassifier(random_state=123),
    "svm": SVC(probability=True),
    "log_reg": LogisticRegression(max_iter=1000),
    "knn": KNeighborsClassifier(),
    "xgboost": XGBClassifier(eval_metric="mlogloss", random_state=123),
    "catboost": CatBoostClassifier(verbose=0, random_state=123)
}

best_model = None
best_score = 0
best_name = ""

# Train and compare
for name, clf in models.items():
    pipeline = Pipeline(steps=[
        ("preprocess", preprocess),
        ("clf", clf)
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"{name} accuracy: {acc:.4f}")

    if acc > best_score:
        best_score = acc
        best_model = pipeline
        best_name = name

# Predictions do melhor modelo
y_pred = best_model.predict(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=best_model.classes_
)

fig, ax = plt.subplots(figsize=(6, 6))
disp.plot(ax=ax, cmap="Blues", values_format="d")

plt.title("Confusion Matrix - Best Model")
plt.show()

print("\nBest model:", best_name)
print("Best accuracy:", best_score)

# Save best model
joblib.dump(best_model, "model.pkl")

print("Saved best model successfully!")