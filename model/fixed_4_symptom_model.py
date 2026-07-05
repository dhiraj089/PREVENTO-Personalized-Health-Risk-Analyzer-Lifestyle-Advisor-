import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import json

# Load dataset
df = pd.read_csv("model/Training.csv")

# Define simple diseases to focus on
simple_diseases = [
    "Allergy",
    "Gastroenteritis", 
    "Migraine",
    "Acne",
    "Urinary tract infection",
    "Common Cold",
    "Fungal infection",
    "Drug Reaction",
    "GERD",
    "Bronchial Asthma"
]

# Filter dataset to only include simple diseases
df = df[df['Disease'].isin(simple_diseases)]

# Drop rows where Disease or all symptoms are missing
df.dropna(subset=["Disease"], inplace=True)

# Fill missing symptom values with "None"
df.fillna("None", inplace=True)

# Clean symptom data - remove leading/trailing spaces
symptom_cols_all = [col for col in df.columns if col.startswith("Symptom")]
for col in symptom_cols_all:
    df[col] = df[col].str.strip()

# Label encode all symptom values from the *entire* filtered dataset
le = LabelEncoder()
all_symptoms_for_encoder = pd.unique(df[symptom_cols_all].values.ravel())
all_symptoms_for_encoder = [str(s).strip() for s in all_symptoms_for_encoder if str(s).lower() != "none" and str(s) != "nan"]
all_symptoms_for_encoder = sorted(set(all_symptoms_for_encoder))
all_symptoms_for_encoder.append("None")  # ensure "None" is included
le.fit(all_symptoms_for_encoder)

# Use only first 4 symptoms for training (exactly 4 symptoms)
symptom_cols_for_model = [f"Symptom_{i}" for i in range(1, 5)]

# Encode symptom columns
for col in symptom_cols_for_model:
    df[col] = le.transform(df[col])

# Features and label
X = df[symptom_cols_for_model]
y = df["Disease"].str.strip()  # Clean disease names

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model with more trees for better accuracy
model = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
model.fit(X_train, y_train)

# Evaluate model
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Training accuracy: {train_score:.4f}")
print(f"Testing accuracy: {test_score:.4f}")

# Save model and encoder
joblib.dump(model, "model/fixed_4_symptom_model.pkl")
joblib.dump(le, "model/fixed_4_symptom_encoder.pkl")

print("✅ Fixed 4-symptom model trained and saved successfully!")
print(f"Number of classes: {len(model.classes_)}")
print(f"Classes: {model.classes_}")

# Create simple precautions for these diseases
fixed_precautions = {
    "Allergy": ["Avoid allergens", "Take antihistamines", "Use air purifier", "Keep windows closed"],
    "Gastroenteritis": ["Stay hydrated", "Eat BRAT diet", "Rest", "Avoid dairy"],
    "Migraine": ["Rest in a quiet, dark room", "Stay hydrated", "Take pain relievers", "Avoid bright lights"],
    "Acne": ["Keep face clean", "Avoid touching face", "Use gentle cleanser", "Don't pop pimples"],
    "Urinary tract infection": ["Drink plenty of water", "Increase vitamin C intake", "Drink cranberry juice", "Take probiotics"],
    "Common Cold": ["Rest", "Drink plenty of fluids", "Take over-the-counter cold medicine", "Use humidifier"],
    "Fungal infection": ["Keep area clean and dry", "Use antifungal cream", "Avoid tight clothing", "Change socks regularly"],
    "Drug Reaction": ["Stop taking the medication", "Contact your doctor", "Monitor symptoms", "Stay hydrated"],
    "GERD": ["Avoid spicy foods", "Eat smaller meals", "Don't lie down after eating", "Elevate head while sleeping"],
    "Bronchial Asthma": ["Use inhaler as prescribed", "Avoid triggers", "Keep rescue inhaler handy", "Monitor breathing"]
}

# Save simple precautions
with open("model/fixed_4_symptom_precautions.json", "w") as f:
    json.dump(fixed_precautions, f, indent=2)

print("✅ Fixed 4-symptom precautions saved!")

# Test the model with different symptom combinations
print("\n" + "="*60)
print("TESTING FIXED 4-SYMPTOM MODEL PREDICTIONS")
print("="*60)

test_combinations = [
    # Test 1: Common Cold symptoms
    ["high_fever", "cough", "fatigue", "headache"],
    
    # Test 2: Gastroenteritis symptoms
    ["nausea", "vomiting", "diarrhoea", "abdominal_pain"],
    
    # Test 3: Acne symptoms
    ["skin_rash", "itching", "blackheads", "blister"],
    
    # Test 4: Bronchial Asthma symptoms
    ["chest_pain", "breathlessness", "cough", "fatigue"],
    
    # Test 5: Migraine symptoms
    ["headache", "nausea", "vomiting", "fatigue"],
    
    # Test 6: Allergy symptoms
    ["continuous_sneezing", "shivering", "chills", "watering_from_eyes"],
    
    # Test 7: GERD symptoms
    ["stomach_pain", "acidity", "ulcers_on_tongue", "vomiting"],
    
    # Test 8: Fungal infection symptoms
    ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic _patches"]
]

for i, symptoms in enumerate(test_combinations):
    print(f"\nTest {i+1}:")
    print(f"Symptoms: {symptoms}")
    
    try:
        # Ensure exactly 4 symptoms
        while len(symptoms) < 4:
            symptoms.append("None")
        symptoms = symptoms[:4]
        
        # Encode symptoms
        encoded = le.transform(symptoms)
        input_df = pd.DataFrame([encoded], columns=[f"Symptom_{i}" for i in range(1, 5)])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        probabilities = model.predict_proba(input_df)[0]
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[-3:][::-1]
        
        print(f"Predicted Disease: {prediction}")
        print(f"Top 3 predictions:")
        for idx in top_indices:
            print(f"  {model.classes_[idx]}: {probabilities[idx]:.4f}")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("TESTING COMPLETED")
print("="*60)
