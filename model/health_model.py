import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("model/Training.csv")

# Drop rows where Disease or all symptoms are missing
df.dropna(subset=["Disease"], inplace=True)

# Fill missing symptom values with "None"
df.fillna("None", inplace=True)

# Clean symptom data - remove leading/trailing spaces
symptom_cols = [col for col in df.columns if col.startswith("Symptom")]
for col in symptom_cols:
    df[col] = df[col].str.strip()

# Use only first 15 symptoms for training
symptom_cols = [f"Symptom_{i}" for i in range(1, 16)]

# Label encode all symptom columns
le = LabelEncoder()

# Flatten all symptom values and fit label encoder
all_symptoms = pd.unique(df[symptom_cols].values.ravel())
all_symptoms = [str(s).strip() for s in all_symptoms if str(s).lower() != "none" and str(s) != "nan"]
all_symptoms = sorted(set(all_symptoms))
all_symptoms.append("None")  # ensure "None" is included

le.fit(all_symptoms)

# Encode symptom columns
for col in symptom_cols:
    df[col] = le.transform(df[col])

# Features and label
X = df[symptom_cols]
y = df["Disease"].str.strip()  # Clean disease names

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Training accuracy: {train_score:.4f}")
print(f"Testing accuracy: {test_score:.4f}")

# Save model and encoder
joblib.dump(model, "model/health_model.pkl")
joblib.dump(le, "model/label_encoder.pkl")

print("✅ Model trained and saved successfully!")
print(f"Number of classes: {len(model.classes_)}")
print(f"Classes: {model.classes_}")
