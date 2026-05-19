# To run: python3 train_model.py
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
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, classification_report

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
    "log_reg": LogisticRegression(max_iter=1000),
    "decision_tree": DecisionTreeClassifier(random_state=123),
    "random_forest": RandomForestClassifier(n_estimators=200, random_state=123),
    "svm": SVC(probability=True),
    "knn": KNeighborsClassifier(),
    "naive_bayes": GaussianNB()
}

best_model = None
best_score = 0
best_name = ""

line = "─" * 50

# Train and compare
for name, clf in models.items():
    pipeline = Pipeline(steps=[
        ("preprocess", preprocess),
        ("clf", clf)
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")

    print("\n" + line)
    print(f" Modelo: {name.upper()}")
    print(line)
    print(f"{'Accuracy':<12}: {acc:.4f}")
    print(f"{'Precision':<12}: {precision:.4f}")
    print(f"{'Recall':<12}: {recall:.4f}")
    print(f"{'F1-score':<12}: {f1:.4f}")
    print(line)

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

# Final summary
print("\n" + line)
print(f" MELHOR MODELO: {best_name.upper()}")
print(line)
print(f"Accuracy final: {best_score:.4f}")
print(line)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save best model
joblib.dump(best_model, "model.pkl")
print("\nSaved best model successfully!")
