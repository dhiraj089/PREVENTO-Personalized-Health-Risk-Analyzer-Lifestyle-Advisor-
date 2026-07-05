from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
import pandas as pd
import joblib
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, KFold
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from datetime import datetime
import io
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
from config import Config
from models import db, User, Prediction
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Initialize database
db.init_app(app)

# Load fixed 4-symptom model and label encoder
model = joblib.load("model/fixed_4_symptom_model.pkl")
le = joblib.load("model/fixed_4_symptom_encoder.pkl")

# Load fixed 4-symptom precautions
with open("model/fixed_4_symptom_precautions.json", "r") as f:
    fixed_precautions = json.load(f)

# Import disease stage classifier
from model.disease_stages import get_disease_stage_info

# Map simple symptoms to training data symptoms (using actual symptoms from dataset)
symptom_mapping = {
    "high_fever": "high_fever",
    "cough": "cough",
    "fatigue": "fatigue", 
    "headache": "headache",
    "muscle_pain": "muscle_pain",
    "vomiting": "vomiting",
    "diarrhoea": "diarrhoea",
    "stomach_pain": "stomach_pain",
    "acidity": "acidity",
    "indigestion": "indigestion",
    "chest_pain": "chest_pain",
    "breathlessness": "breathlessness",
    "skin_rash": "skin_rash",
    "itching": "itching",
    "continuous_sneezing": "continuous_sneezing"
}

# Database initialization function
def _ensure_user_columns():
    """Add any missing User columns to the existing users table."""
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return

    existing_columns = {col['name'] for col in inspector.get_columns('users')}
    alter_statements = []

    if 'age' not in existing_columns:
        alter_statements.append("ALTER TABLE users ADD COLUMN age INTEGER")
    if 'gender' not in existing_columns:
        alter_statements.append("ALTER TABLE users ADD COLUMN gender VARCHAR(50)")
    if 'weight' not in existing_columns:
        alter_statements.append("ALTER TABLE users ADD COLUMN weight FLOAT")
    if 'height' not in existing_columns:
        alter_statements.append("ALTER TABLE users ADD COLUMN height FLOAT")

    if alter_statements:
        for stmt in alter_statements:
            db.session.execute(text(stmt))
        db.session.commit()


def init_db():
    """Initialize the database and create tables"""
    with app.app_context():
        try:
            db.create_all()
            _ensure_user_columns()
            print("Database tables created successfully!")
        except Exception as exc:
            print(f"Database initialization failed: {exc}")

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form.get("email", "")
        first_name = request.form.get("first_name", "")
        last_name = request.form.get("last_name", "")
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose a different username.", "error")
            return render_template("register.html")
        
        # Check if email already exists (if provided)
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash("Email already registered! Please use a different email.", "error")
                return render_template("register.html")
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email if email else None,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash("Registration successful! Please login with your credentials.", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            print(f"Registration error: {e}")
            return render_template("register.html")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Find user in database
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("welcome"))
        else:
            flash("Invalid username or password. Please try again.", "error")
            return render_template("login.html")
    
    return render_template("login.html")

@app.route("/welcome")
def welcome():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    if not user or not user.is_active:
        session.clear()
        flash("Your account is no longer active. Please contact support.", "error")
        return redirect(url_for("login"))

    # Build dashboard metrics to render server-side (no client fetch)
    try:
        # Load dataset
        df = pd.read_csv("model/Training.csv")
        df = df.dropna(subset=["Disease"]).copy()
        df.fillna("None", inplace=True)

        # All symptom columns present in dataset (for cleaning and summary)
        symptom_cols_all = [c for c in df.columns if c.startswith("Symptom")]
        for col in symptom_cols_all:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # Compute dataset summary
        total_samples = int(len(df))
        unique_symptoms = set()
        for col in symptom_cols_all:
            if col in df.columns:
                unique_symptoms.update(set(df[col].astype(str)))
        # Remove non-meaningful tokens
        for token in ["None", "nan", "NaN", "",
                      "NONE", "NAN"]:
            if token in unique_symptoms:
                unique_symptoms.discard(token)
        # Keep summary aligned with the model: first 15 symptom inputs
        total_symptoms = 15
        total_diseases = int(df["Disease"].astype(str).str.strip().nunique())

        # Disease distribution for pie chart
        disease_series = df["Disease"].astype(str).str.strip()
        disease_counts = disease_series.value_counts()
        disease_labels = list(disease_counts.index)
        disease_values = [int(v) for v in disease_counts.values]

        # Load trained model and label encoder
        rf_model = joblib.load("model/health_model.pkl")
        label_encoder = joblib.load("model/label_encoder.pkl")

        # Encode features
        # Model was trained on first 15 symptoms, keep compatibility for scoring
        model_symptom_cols = [f"Symptom_{i}" for i in range(1, 16)]
        X = df[model_symptom_cols].copy()
        for col in model_symptom_cols:
            X[col] = label_encoder.transform(X[col])
        y = disease_series

        # Train/test split for real-time accuracy of current model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        train_accuracy = float(rf_model.score(X_train, y_train)) * 100.0
        test_accuracy = float(rf_model.score(X_test, y_test)) * 100.0

        # Accuracy trend via K-Fold CV using a clone with same hyperparameters
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        trend_labels = []
        trend_train = []
        trend_test = []
        fold_index = 1
        for train_idx, test_idx in kf.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
            model_clone = clone(rf_model)
            model_clone.fit(X_tr, y_tr)
            trend_train.append(float(model_clone.score(X_tr, y_tr)) * 100.0)
            trend_test.append(float(model_clone.score(X_te, y_te)) * 100.0)
            trend_labels.append(f"Fold {fold_index}")
            fold_index += 1

        dashboard = {
            "train_accuracy": round(train_accuracy, 2),
            "test_accuracy": round(test_accuracy, 2),
            "trend_labels": trend_labels,
            "trend_train": [round(v, 2) for v in trend_train],
            "trend_test": [round(v, 2) for v in trend_test],
            "disease_labels": disease_labels,
            "disease_values": disease_values,
            "summary": {
                "total_samples": total_samples,
                "total_symptoms": total_symptoms,
                "total_diseases": total_diseases
            }
        }
    except Exception as e:
        print(f"Error building welcome dashboard: {e}")
        dashboard = {
            "train_accuracy": None,
            "test_accuracy": None,
            "trend_labels": [],
            "trend_train": [],
            "trend_test": [],
            "disease_labels": [],
            "disease_values": [],
            "summary": {"total_samples": 0, "total_symptoms": 0, "total_diseases": 0}
        }

    return render_template("welcome.html", username=user.username, user=user, dashboard=dashboard)

@app.route("/train-model", methods=["POST"])
def train_model_endpoint():
    """Retrain the dataset model (health_model.pkl) using all Symptom_* columns.
    Uses class balancing and saves updated artifacts.
    Returns JSON with new train/test accuracy.
    """
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        df = pd.read_csv("model/Training.csv")
        df = df.dropna(subset=["Disease"]).copy()
        df.fillna("None", inplace=True)

        # All symptom columns
        symptom_cols_all = [c for c in df.columns if c.startswith("Symptom")]
        for col in symptom_cols_all:
            df[col] = df[col].astype(str).str.strip()

        # Build a single label encoder over all symptom values (including "None")
        from sklearn.preprocessing import LabelEncoder
        le_all = LabelEncoder()
        all_values = pd.unique(df[symptom_cols_all].values.ravel())
        cleaned_values = [str(v).strip() for v in all_values]
        unique_values = sorted(set(cleaned_values))
        if "None" not in unique_values:
            unique_values.append("None")
        le_all.fit(unique_values)

        # Transform features
        X = df[symptom_cols_all].copy()
        for col in symptom_cols_all:
            X[col] = le_all.transform(X[col])
        y = df["Disease"].astype(str).str.strip()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Balanced RandomForest
        rf = RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=42
        )
        rf.fit(X_train, y_train)

        train_acc = float(rf.score(X_train, y_train)) * 100.0
        test_acc = float(rf.score(X_test, y_test)) * 100.0

        # Save artifacts in the same paths used by dashboard
        joblib.dump(rf, "model/health_model.pkl")
        joblib.dump(le_all, "model/label_encoder.pkl")

        return jsonify({
            "message": "Model retrained successfully",
            "train_accuracy": round(train_acc, 2),
            "test_accuracy": round(test_acc, 2),
            "features": len(symptom_cols_all)
        })
    except Exception as e:
        print(f"Error retraining model: {e}")
        return jsonify({"error": "Failed to retrain model"}), 500

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "details":
            user.first_name = request.form.get("first_name")
            user.last_name = request.form.get("last_name")
            user.email = request.form.get("email")
            user.age = request.form.get("age", type=int)
            user.gender = request.form.get("gender")
            user.weight = request.form.get("weight", type=float)
            user.height = request.form.get("height", type=float)
            db.session.commit()
            flash("Your details have been updated successfully.", "success")
            return redirect(url_for("profile"))

        elif form_type == "password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_new_password = request.form.get("confirm_new_password")

            if not user.check_password(current_password):
                flash("Current password is incorrect.", "error")
            elif new_password != confirm_new_password:
                flash("New passwords do not match.", "error")
            else:
                user.set_password(new_password)
                db.session.commit()
                flash("Your password has been changed successfully.", "success")
                return redirect(url_for("profile"))

    return render_template("profile.html", user=user)



@app.route("/survey", methods=["GET", "POST"])
def survey():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("survey.html")

@app.route("/accuracy")
def accuracy_page():
    """Display dataset accuracy page"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    if not user or not user.is_active:
        session.clear()
        flash("Your account is no longer active. Please contact support.", "error")
        return redirect(url_for("login"))
    
    return render_template("accuracy.html", username=user.username)

@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get selected symptoms from checkboxes (only 4 symptoms maximum)
    selected_symptoms = []
    for i in range(1, 16):  # Check all 15 symptom slots
        symptom = request.form.get(f"symptom{i}")
        if symptom:
            # Map simple symptom name to training data symptom name
            mapped_symptom = symptom_mapping.get(symptom, symptom)
            selected_symptoms.append(mapped_symptom)
    
    # Ensure we have exactly 4 symptoms (pad with "None" if less than 4)
    while len(selected_symptoms) < 4:
        selected_symptoms.append("None")
    selected_symptoms = selected_symptoms[:4]  # Take only first 4

    # Encode symptoms using the saved label encoder
    try:
        encoded = le.transform(selected_symptoms)
        input_df = pd.DataFrame([encoded], columns=[f"Symptom_{i}" for i in range(1, 5)])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        
        # Get prediction probabilities for debugging
        probabilities = model.predict_proba(input_df)[0]
        classes = model.classes_
        
        print(f"Prediction: {prediction}")
        print(f"Selected symptoms: {[s for s in selected_symptoms if s != 'None']}")
        print(f"Top 3 predictions with probabilities:")
        for i, (cls, prob) in enumerate(zip(classes, probabilities)):
            if i < 3:  # Show top 3
                print(f"  {cls}: {prob:.4f}")
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        prediction = "Unknown"
        return render_template("result.html", prediction=prediction, advice=["Error occurred during prediction"])

    # Get disease stage information and stage-specific advice
    reported_symptoms = [s for s in selected_symptoms if s != "None"]
    stage_info = get_disease_stage_info(prediction, reported_symptoms)
    
    # Get precautions from fixed 4-symptom precautions (fallback)
    fallback_advice = fixed_precautions.get(prediction, ["Stay hydrated", "Rest", "Consult a doctor"])
    
    # Use stage-specific advice if available, otherwise use fallback
    advice_text = stage_info.get("prevention_advice", fallback_advice)
    
    # Store prediction in database
    try:
        user = User.query.get(session["user_id"])
        if user:
            new_prediction = Prediction(
                user_id=user.id,
                symptoms=reported_symptoms,
                predicted_disease=prediction,
                confidence_score=float(max(probabilities)) if 'probabilities' in locals() else None,
                precautions=advice_text
            )
            db.session.add(new_prediction)
            db.session.commit()
    except Exception as e:
        print(f"Error storing prediction: {e}")
        # Continue with the prediction even if storage fails

    return render_template("result.html", 
                         prediction=prediction, 
                         advice=advice_text,
                         stage_info=stage_info)

@app.route("/init-db")
def initialize_database():
    """Initialize database tables (for development only)"""
    try:
        init_db()
        return "Database initialized successfully!"
    except Exception as e:
        return f"Error initializing database: {e}"

@app.route("/api/dataset-accuracy")
def dataset_accuracy():
    """API endpoint to get dataset accuracy metrics"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Load training data
        df = pd.read_csv("model/Training.csv")
        
        # Get the fixed 4-symptom model data (simplified diseases)
        simple_diseases = [
            "Allergy", "Gastroenteritis", "Migraine", "Acne", 
            "Urinary tract infection", "Common Cold", "Fungal infection",
            "Drug Reaction", "GERD", "Bronchial Asthma"
        ]
        
        # Filter dataset for simple diseases
        df_filtered = df[df['Disease'].isin(simple_diseases)].copy()
        df_filtered.dropna(subset=["Disease"], inplace=True)
        df_filtered.fillna("None", inplace=True)
        
        # Clean symptom data
        symptom_cols = [f"Symptom_{i}" for i in range(1, 5)]
        for col in symptom_cols:
            if col in df_filtered.columns:
                df_filtered[col] = df_filtered[col].str.strip()
        
        # Prepare data for accuracy calculation
        X = df_filtered[symptom_cols]
        y = df_filtered["Disease"].str.strip()
        
        # Split data (same as training)
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Load the trained model and encoder
        model = joblib.load("model/fixed_4_symptom_model.pkl")
        le = joblib.load("model/fixed_4_symptom_encoder.pkl")
        
        # Encode test data
        X_test_encoded = X_test.copy()
        for col in symptom_cols:
            X_test_encoded[col] = le.transform(X_test_encoded[col])
        
        # Make predictions
        y_pred = model.predict(X_test_encoded)
        
        # Calculate accuracy metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get class-wise accuracy
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        # Disease distribution
        disease_counts = y.value_counts().to_dict()
        
        # Prediction confidence distribution
        probabilities = model.predict_proba(X_test_encoded)
        confidence_scores = np.max(probabilities, axis=1)
        
        # Prepare response data
        accuracy_data = {
            "overall_accuracy": round(accuracy * 100, 2),
            "total_samples": len(df_filtered),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "diseases_count": len(simple_diseases),
            "disease_distribution": disease_counts,
            "class_accuracy": {
                disease: round(class_report.get(disease, {}).get('f1-score', 0) * 100, 2)
                for disease in simple_diseases
                if disease in class_report
            },
            "confidence_stats": {
                "mean_confidence": round(np.mean(confidence_scores) * 100, 2),
                "median_confidence": round(np.median(confidence_scores) * 100, 2),
                "min_confidence": round(np.min(confidence_scores) * 100, 2),
                "max_confidence": round(np.max(confidence_scores) * 100, 2)
            },
            "model_info": {
                "type": "Random Forest",
                "n_estimators": model.n_estimators,
                "features_used": len(symptom_cols),
                "classes": simple_diseases
            }
        }
        
        return jsonify(accuracy_data)
        
    except Exception as e:
        print(f"Error calculating accuracy: {e}")
        return jsonify({"error": "Failed to calculate accuracy metrics"}), 500

@app.route("/api/model-metrics")
def model_metrics():
    """API endpoint to provide model accuracy, feature importances, and dataset distribution.
    Uses the latest saved RandomForest model and the current Training.csv.
    """
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Load dataset
        df = pd.read_csv("model/Training.csv")

        # Keep a consistent set of symptom columns used by the trained health model
        symptom_cols = [f"Symptom_{i}" for i in range(1, 16)]
        df = df.dropna(subset=["Disease"]).copy()
        df.fillna("None", inplace=True)
        for col in symptom_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # Load trained model and its label encoder
        rf_model = joblib.load("model/health_model.pkl")
        label_encoder = joblib.load("model/label_encoder.pkl")

        # Encode symptoms for model input
        X = df[symptom_cols].copy()
        for col in symptom_cols:
            X[col] = label_encoder.transform(X[col])
        y = df["Disease"].astype(str).str.strip()

        # Train/test split to compute accuracies matching training procedure
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Compute metrics
        train_accuracy = float(rf_model.score(X_train, y_train)) * 100.0
        test_accuracy = float(rf_model.score(X_test, y_test)) * 100.0

        # Feature importances
        importances = getattr(rf_model, "feature_importances_", None)
        feature_importances = []
        if importances is not None:
            feature_importances = [
                {"feature": symptom_cols[i], "importance": float(importances[i])}
                for i in range(len(symptom_cols))
            ]
            feature_importances.sort(key=lambda x: x["importance"], reverse=True)

        # Dataset distribution by disease
        disease_distribution = (
            y.value_counts().sort_values(ascending=False).to_dict()
        )

        return jsonify({
            "train_accuracy": round(train_accuracy, 2),
            "test_accuracy": round(test_accuracy, 2),
            "feature_importances": feature_importances,
            "disease_distribution": disease_distribution,
            "updated_at": datetime.utcnow().isoformat() + "Z"
        })
    except Exception as e:
        print(f"Error building model metrics: {e}")
        return jsonify({"error": "Failed to build model metrics"}), 500

@app.route("/download-report")
def download_report():
    """Generate and download a comprehensive prevention report PDF"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if not REPORTLAB_AVAILABLE:
        flash("PDF generation is not available. Please install reportlab package.", "error")
        return redirect(url_for("welcome"))
    
    try:
        # Get the latest prediction for the current user
        user = User.query.get(session["user_id"])
        if not user:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for("login"))
        
        if not user.is_active:
            flash("Your account is no longer active. Please contact support.", "error")
            return redirect(url_for("login"))
        
        # Get the most recent prediction
        latest_prediction = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).first()
        
        if not latest_prediction:
            flash("No prediction data found. Please complete a health survey first.", "error")
            return redirect(url_for("survey"))
        
        # Validate prediction data
        if not latest_prediction.symptoms or len(latest_prediction.symptoms) == 0:
            flash("Invalid prediction data. Please complete a new health survey.", "error")
            return redirect(url_for("survey"))
        
        if not latest_prediction.predicted_disease:
            flash("Prediction data is incomplete. Please complete a new health survey.", "error")
            return redirect(url_for("survey"))
        
        # Get disease stage information
        stage_info = get_disease_stage_info(latest_prediction.predicted_disease, latest_prediction.symptoms)
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Build the PDF content
        story = []
        
        # Title
        story.append(Paragraph("🩺 PREVENTO HEALTH REPORT", title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Paragraph(f"<b>Patient ID:</b> {user.username}", normal_style))
        if user.first_name and user.last_name:
            story.append(Paragraph(f"<b>Full Name:</b> {user.first_name} {user.last_name}", normal_style))
        if user.email:
            story.append(Paragraph(f"<b>Email:</b> {user.email}", normal_style))
        story.append(Paragraph(f"<b>Report ID:</b> {latest_prediction.id}", normal_style))
        story.append(Spacer(1, 20))
        
        # Prediction Results Section
        story.append(Paragraph("🔬 PREDICTION ANALYSIS", heading_style))
        
        # Symptoms table
        story.append(Paragraph("<b>Reported Symptoms:</b>", normal_style))
        symptoms_data = [['Symptom', 'Status', 'Severity']]
        for symptom in latest_prediction.symptoms:
            symptoms_data.append([symptom.replace('_', ' ').title(), 'Present', 'Reported'])
        
        symptoms_table = Table(symptoms_data)
        symptoms_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(symptoms_table)
        story.append(Spacer(1, 12))
        
        # Additional symptom information
        story.append(Paragraph(f"<b>Total Symptoms Reported:</b> {len(latest_prediction.symptoms)}", normal_style))
        story.append(Paragraph(f"<b>Analysis Date:</b> {latest_prediction.created_at.strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Spacer(1, 12))
        
        # Prediction result
        story.append(Paragraph(f"<b>AI Prediction:</b> {latest_prediction.predicted_disease}", normal_style))
        if latest_prediction.confidence_score:
            confidence_percentage = latest_prediction.confidence_score * 100
            confidence_level = "High" if confidence_percentage >= 80 else "Medium" if confidence_percentage >= 60 else "Low"
            story.append(Paragraph(f"<b>Confidence Score:</b> {confidence_percentage:.1f}% ({confidence_level} Confidence)", normal_style))
        
        # Disease Stage Information
        story.append(Spacer(1, 12))
        story.append(Paragraph("🏥 DISEASE STAGE ANALYSIS", heading_style))
        story.append(Paragraph(f"<b>Disease Stage:</b> {stage_info['stage'].title()} {stage_info['stage_icon']}", normal_style))
        story.append(Paragraph(f"<b>Stage Description:</b> {stage_info['stage_description']}", normal_style))
        # Show severity score as a percentage for clarity
        sev_raw = stage_info.get('severity_percentage', stage_info.get('severity_score'))
        sev_pct = int(round(sev_raw)) if sev_raw is not None else None
        if sev_pct is not None:
            story.append(Paragraph(f"<b>Severity Score:</b> {sev_pct}%", normal_style))
        else:
            story.append(Paragraph(f"<b>Severity Score:</b> N/A", normal_style))
        
        # Stage-specific color coding
        stage_colors = {
            "normal": "Green",
            "intermediate": "Orange", 
            "risky": "Red"
        }
        stage_color = stage_colors.get(stage_info['stage'], "Gray")
        story.append(Paragraph(f"<b>Risk Level:</b> {stage_color} - {stage_info['stage'].title()} Risk", normal_style))
        story.append(Spacer(1, 20))
        
        # Prevention Advice Section
        story.append(Paragraph("💡 STAGE-SPECIFIC PREVENTION & TREATMENT ADVICE", heading_style))
        
        # Use stage-specific advice if available
        if stage_info and stage_info.get('prevention_advice'):
            story.append(Paragraph(f"<b>Stage-Specific Recommendations for {latest_prediction.predicted_disease} ({stage_info['stage'].title()} Stage):</b>", normal_style))
            for i, advice in enumerate(stage_info['prevention_advice'], 1):
                story.append(Paragraph(f"{i}. {advice}", normal_style))
        elif latest_prediction.precautions:
            story.append(Paragraph(f"<b>General Recommendations for {latest_prediction.predicted_disease}:</b>", normal_style))
            for i, advice in enumerate(latest_prediction.precautions, 1):
                story.append(Paragraph(f"{i}. {advice}", normal_style))
        else:
            story.append(Paragraph("No specific precautions available for this condition.", normal_style))
        
        story.append(Spacer(1, 20))
        
        # General Health Tips
        story.append(Paragraph("🏥 GENERAL HEALTH RECOMMENDATIONS", heading_style))
        
        general_tips = [
            "Maintain a balanced diet rich in fruits, vegetables, and whole grains",
            "Stay hydrated by drinking at least 8 glasses of water daily",
            "Get adequate sleep (7-9 hours per night for adults)",
            "Exercise regularly for at least 30 minutes daily",
            "Practice good hygiene and wash hands frequently",
            "Avoid smoking and limit alcohol consumption",
            "Manage stress through relaxation techniques like meditation or yoga",
            "Keep up with regular medical checkups and vaccinations",
            "Monitor your health and report any new or worsening symptoms",
            "Follow your healthcare provider's recommendations"
        ]
        
        story.append(Paragraph("<b>General Health Guidelines:</b>", normal_style))
        for tip in general_tips:
            story.append(Paragraph(f"• {tip}", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Follow-up Recommendations
        story.append(Paragraph("📋 FOLLOW-UP RECOMMENDATIONS", heading_style))
        
        follow_up_tips = [
            "Schedule a consultation with your healthcare provider within 1-2 weeks",
            "Monitor your symptoms and note any changes or new symptoms",
            "Keep a symptom diary to track your condition over time",
            "Follow the specific recommendations provided above",
            "Return for re-evaluation if symptoms worsen or persist",
            "Consider seeking a second opinion if you have concerns about the diagnosis"
        ]
        
        for tip in follow_up_tips:
            story.append(Paragraph(f"• {tip}", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Disclaimer
        story.append(Paragraph("⚠️ IMPORTANT DISCLAIMER", heading_style))
        disclaimer_text = """
        This report is generated by an AI-powered medical assistant and is for informational purposes only. 
        It should not be considered as a substitute for professional medical advice, diagnosis, or treatment. 
        Always consult with a qualified healthcare provider for any medical concerns or before making 
        decisions about your health. In case of emergency, contact emergency services immediately.
        
        The AI prediction is based on the symptoms you reported and may not be 100% accurate. 
        Medical conditions can have similar symptoms, and professional medical evaluation is essential 
        for proper diagnosis and treatment.
        """
        story.append(Paragraph(disclaimer_text, normal_style))
        
        story.append(Spacer(1, 20))
        
        # Footer
        footer_text = f"Report generated by Prevento AI Health Assistant • {datetime.now().strftime('%Y')}"
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=prevento_health_report_{user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return response
        
    except Exception as e:
        print(f"Error generating report: {e}")
        flash("Error generating report. Please try again.", "error")
        return redirect(url_for("welcome"))

@app.route("/report-preview")
def report_preview():
    """Preview the health report before downloading"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    try:
        # Get the latest prediction for the current user
        user = User.query.get(session["user_id"])
        if not user:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for("login"))
        
        if not user.is_active:
            flash("Your account is no longer active. Please contact support.", "error")
            return redirect(url_for("login"))
        
        # Get the most recent prediction
        latest_prediction = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).first()
        
        if not latest_prediction:
            flash("No prediction data found. Please complete a health survey first.", "error")
            return redirect(url_for("survey"))
        
        # Validate prediction data
        if not latest_prediction.symptoms or len(latest_prediction.symptoms) == 0:
            flash("Invalid prediction data. Please complete a new health survey.", "error")
            return redirect(url_for("survey"))
        
        if not latest_prediction.predicted_disease:
            flash("Prediction data is incomplete. Please complete a new health survey.", "error")
            return redirect(url_for("survey"))
        
        # Get disease stage information
        stage_info = get_disease_stage_info(latest_prediction.predicted_disease, latest_prediction.symptoms)
        
        # Prepare data for preview
        report_data = {
            'user': user,
            'prediction': latest_prediction,
            'stage_info': stage_info,
            'generated_at': datetime.now(),
            'report_id': latest_prediction.id
        }
        
        return render_template("report_preview.html", **report_data)
        
    except Exception as e:
        print(f"Error generating report preview: {e}")
        flash("Error generating report preview. Please try again.", "error")
        return redirect(url_for("welcome"))

@app.route("/my-reports")
def my_reports():
    """View all user's previous health reports"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    try:
        user = User.query.get(session["user_id"])
        if not user or not user.is_active:
            session.clear()
            flash("Your account is no longer active. Please contact support.", "error")
            return redirect(url_for("login"))
        
        # Get all predictions for the user, ordered by most recent first
        predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()
        
        return render_template("my_reports.html", user=user, predictions=predictions)
        
    except Exception as e:
        print(f"Error loading reports: {e}")
        flash("Error loading your reports. Please try again.", "error")
        return redirect(url_for("welcome"))

if __name__ == "__main__":
    # Initialize database on first run
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    app.run(debug=True)
