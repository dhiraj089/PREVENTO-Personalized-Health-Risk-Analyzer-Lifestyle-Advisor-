# 🩺 Prevento – Personalized Health Risk Analyzer & Disease Prediction System

Prevento is a machine learning-based healthcare application designed to predict the most probable disease based on user-reported symptoms. The system leverages the **Random Forest Classifier** to analyze symptom patterns and provide preliminary disease predictions, helping users seek timely medical attention.

## 📌 Project Overview

The objective of Prevento is to assist users in identifying potential diseases through symptom-based prediction using machine learning. The application provides an easy-to-use interface where users can enter their symptoms and receive a predicted disease along with personalized health recommendations.

## ✨ Features

- 🔍 Disease prediction based on symptoms
- 🤖 Machine Learning model using Random Forest Classifier
- 📝 User-friendly web interface built with Flask
- 💊 Personalized lifestyle and health recommendations
- 📊 Fast and accurate prediction results
- 📱 Easy to use for preliminary health assessment

## 🛠️ Technologies Used

- Python
- Flask
- Scikit-learn
- Pandas
- NumPy
- HTML
- CSS
- Joblib

## 🧠 Machine Learning Workflow

1. Data Collection and Preprocessing
2. Symptom Encoding and Feature Engineering
3. Model Training using Random Forest Classifier
4. Model Evaluation
5. Disease Prediction through Web Application

## 📂 Dataset

The model is trained on a medical dataset containing:

- 130+ symptoms
- 40+ diseases
- Binary symptom encoding (Present/Absent)

The dataset is preprocessed by handling missing values, encoding categorical data, and splitting it into training and testing datasets.

## 📈 Model Performance

The model is evaluated using:

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix

The Random Forest algorithm provides high prediction accuracy while reducing overfitting through ensemble learning.

## 🚀 How It Works

1. User enters the symptoms.
2. The application preprocesses the input.
3. The trained Random Forest model predicts the most likely disease.
4. The predicted result and health guidance are displayed to the user.

## 📁 Project Structure

```
Prevento/
│── app.py
│── model.joblib
│── training.csv
│── templates/
│── static/
│── README.md
```

## 🎯 Future Improvements

- Add demographic and medical history features
- Include laboratory test reports
- Deploy on cloud platforms
- Mobile application support
- AI-powered health chatbot
- Real-time doctor consultation integration

## ⚠️ Disclaimer

This project is intended for educational and research purposes only. The predictions are not a substitute for professional medical diagnosis or treatment. Users should always consult qualified healthcare professionals for medical advice.
