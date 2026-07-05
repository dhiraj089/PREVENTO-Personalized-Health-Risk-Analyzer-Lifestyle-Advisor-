#!/usr/bin/env python3
"""
Disease Stage Classification and Prevention System for Prevento
This module handles disease stage classification (Normal, Intermediate, Risky) 
and provides stage-specific prevention recommendations.
"""

import json
from typing import Dict, List, Tuple, Optional

class DiseaseStageClassifier:
    """Classifies diseases into stages and provides stage-specific prevention advice"""
    
    def __init__(self):
        self.disease_stages = self._load_disease_stages()
        self.stage_preventions = self._load_stage_preventions()
        self.symptom_severity_mapping = self._load_symptom_severity()
    
    def _load_disease_stages(self) -> Dict[str, Dict]:
        """Define disease stages based on symptom combinations and severity"""
        return {
            "Allergy": {
                "normal": {
                    "symptoms": ["continuous_sneezing", "watering_from_eyes"],
                    "description": "Mild allergic reaction with basic symptoms",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["continuous_sneezing", "watering_from_eyes", "shivering", "chills"],
                    "description": "Moderate allergic reaction with additional symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["continuous_sneezing", "watering_from_eyes", "shivering", "chills", "skin_rash", "breathlessness"],
                    "description": "Severe allergic reaction requiring immediate attention",
                    "severity_score": 3
                }
            },
            "Gastroenteritis": {
                "normal": {
                    "symptoms": ["stomach_pain", "diarrhoea"],
                    "description": "Mild gastrointestinal upset",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["stomach_pain", "diarrhoea", "vomiting", "nausea"],
                    "description": "Moderate gastrointestinal infection",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["stomach_pain", "diarrhoea", "vomiting", "nausea", "high_fever", "fatigue"],
                    "description": "Severe gastrointestinal infection with systemic symptoms",
                    "severity_score": 3
                }
            },
            "Migraine": {
                "normal": {
                    "symptoms": ["headache"],
                    "description": "Mild headache episode",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["headache", "fatigue", "nausea"],
                    "description": "Moderate migraine with associated symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["headache", "fatigue", "nausea", "vomiting", "high_fever"],
                    "description": "Severe migraine with systemic symptoms",
                    "severity_score": 3
                }
            },
            "Acne": {
                "normal": {
                    "symptoms": ["skin_rash"],
                    "description": "Mild skin irritation",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["skin_rash", "itching", "blackheads"],
                    "description": "Moderate acne with multiple symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["skin_rash", "itching", "blackheads", "blister", "nodal_skin_eruptions"],
                    "description": "Severe acne with inflammatory symptoms",
                    "severity_score": 3
                }
            },
            "Urinary tract infection": {
                "normal": {
                    "symptoms": ["stomach_pain"],
                    "description": "Mild urinary discomfort",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["stomach_pain", "fatigue", "nausea"],
                    "description": "Moderate UTI with systemic symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["stomach_pain", "fatigue", "nausea", "high_fever", "vomiting"],
                    "description": "Severe UTI with high fever and systemic symptoms",
                    "severity_score": 3
                }
            },
            "Common Cold": {
                "normal": {
                    "symptoms": ["cough", "fatigue"],
                    "description": "Mild cold symptoms",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["cough", "fatigue", "headache", "continuous_sneezing"],
                    "description": "Moderate cold with multiple symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["cough", "fatigue", "headache", "continuous_sneezing", "high_fever", "breathlessness"],
                    "description": "Severe cold with respiratory complications",
                    "severity_score": 3
                }
            },
            "Fungal infection": {
                "normal": {
                    "symptoms": ["itching"],
                    "description": "Mild fungal infection",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["itching", "skin_rash", "dischromic _patches"],
                    "description": "Moderate fungal infection with skin changes",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["itching", "skin_rash", "dischromic _patches", "nodal_skin_eruptions", "blister"],
                    "description": "Severe fungal infection with inflammatory symptoms",
                    "severity_score": 3
                }
            },
            "Drug Reaction": {
                "normal": {
                    "symptoms": ["skin_rash"],
                    "description": "Mild drug reaction",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["skin_rash", "itching", "fatigue"],
                    "description": "Moderate drug reaction with systemic symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["skin_rash", "itching", "fatigue", "high_fever", "breathlessness", "vomiting"],
                    "description": "Severe drug reaction requiring immediate medical attention",
                    "severity_score": 3
                }
            },
            "GERD": {
                "normal": {
                    "symptoms": ["stomach_pain", "acidity"],
                    "description": "Mild acid reflux",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["stomach_pain", "acidity", "indigestion", "ulcers_on_tongue"],
                    "description": "Moderate GERD with additional symptoms",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["stomach_pain", "acidity", "indigestion", "ulcers_on_tongue", "vomiting", "chest_pain"],
                    "description": "Severe GERD with complications",
                    "severity_score": 3
                }
            },
            "Bronchial Asthma": {
                "normal": {
                    "symptoms": ["cough", "fatigue"],
                    "description": "Mild asthma symptoms",
                    "severity_score": 1
                },
                "intermediate": {
                    "symptoms": ["cough", "fatigue", "breathlessness", "chest_pain"],
                    "description": "Moderate asthma with breathing difficulties",
                    "severity_score": 2
                },
                "risky": {
                    "symptoms": ["cough", "fatigue", "breathlessness", "chest_pain", "high_fever", "vomiting"],
                    "description": "Severe asthma attack requiring emergency care",
                    "severity_score": 3
                }
            }
        }
    
    def _load_stage_preventions(self) -> Dict[str, Dict[str, List[str]]]:
        """Define stage-specific prevention and treatment recommendations"""
        return {
            "Allergy": {
                "normal": [
                    "Avoid known allergens",
                    "Use over-the-counter antihistamines",
                    "Keep windows closed during high pollen seasons",
                    "Use air purifiers in your home",
                    "Wash hands frequently to remove allergens"
                ],
                "intermediate": [
                    "Take prescribed antihistamines as directed",
                    "Use nasal saline sprays to reduce congestion",
                    "Apply cold compress to reduce eye irritation",
                    "Avoid outdoor activities during peak pollen times",
                    "Consider allergy shots if symptoms persist",
                    "Monitor symptoms and seek medical advice if they worsen"
                ],
                "risky": [
                    "Seek immediate medical attention",
                    "Use emergency epinephrine if prescribed",
                    "Avoid all known allergens completely",
                    "Have emergency contact information readily available",
                    "Consider carrying an allergy alert bracelet",
                    "Follow up with an allergist for comprehensive treatment"
                ]
            },
            "Gastroenteritis": {
                "normal": [
                    "Stay hydrated with clear fluids",
                    "Eat bland foods (BRAT diet: bananas, rice, applesauce, toast)",
                    "Get plenty of rest",
                    "Avoid dairy products temporarily",
                    "Wash hands frequently to prevent spread"
                ],
                "intermediate": [
                    "Increase fluid intake with electrolyte solutions",
                    "Eat small, frequent meals of bland foods",
                    "Avoid spicy, fatty, or acidic foods",
                    "Take over-the-counter anti-nausea medication if needed",
                    "Monitor for signs of dehydration",
                    "Consider probiotics to restore gut health"
                ],
                "risky": [
                    "Seek immediate medical attention",
                    "Monitor for signs of severe dehydration",
                    "Avoid all solid foods until symptoms improve",
                    "Use oral rehydration solutions",
                    "Watch for signs of blood in stool or vomit",
                    "Consider hospitalization for IV fluids if needed"
                ]
            },
            "Migraine": {
                "normal": [
                    "Rest in a quiet, dark room",
                    "Apply cold compress to head or neck",
                    "Stay hydrated",
                    "Avoid bright lights and loud noises",
                    "Practice relaxation techniques"
                ],
                "intermediate": [
                    "Take prescribed migraine medication as directed",
                    "Use over-the-counter pain relievers if approved by doctor",
                    "Apply ice packs to head and neck",
                    "Stay in a completely dark, quiet room",
                    "Avoid triggers like certain foods or stress",
                    "Consider acupuncture or massage therapy"
                ],
                "risky": [
                    "Seek immediate medical attention",
                    "Do not drive or operate machinery",
                    "Take emergency migraine medication if prescribed",
                    "Monitor for signs of stroke or other complications",
                    "Keep emergency contact information readily available",
                    "Consider hospitalization for severe cases"
                ]
            },
            "Acne": {
                "normal": [
                    "Wash face twice daily with gentle cleanser",
                    "Avoid touching or picking at pimples",
                    "Use non-comedogenic moisturizers",
                    "Keep hair clean and away from face",
                    "Change pillowcases regularly"
                ],
                "intermediate": [
                    "Use over-the-counter acne treatments with benzoyl peroxide or salicylic acid",
                    "Apply spot treatments to individual pimples",
                    "Use oil-free makeup and skincare products",
                    "Avoid excessive sun exposure",
                    "Consider seeing a dermatologist for prescription treatments",
                    "Maintain a consistent skincare routine"
                ],
                "risky": [
                    "Seek immediate dermatological consultation",
                    "Avoid all harsh skincare products",
                    "Do not pick or squeeze inflamed lesions",
                    "Consider prescription medications like antibiotics or retinoids",
                    "Monitor for signs of infection or scarring",
                    "Follow dermatologist's treatment plan strictly"
                ]
            },
            "Urinary tract infection": {
                "normal": [
                    "Drink plenty of water to flush bacteria",
                    "Increase vitamin C intake",
                    "Drink cranberry juice (unsweetened)",
                    "Urinate frequently and completely",
                    "Wipe from front to back after using toilet"
                ],
                "intermediate": [
                    "Take prescribed antibiotics as directed",
                    "Use over-the-counter pain relievers for discomfort",
                    "Apply heating pad to lower abdomen",
                    "Avoid caffeine, alcohol, and spicy foods",
                    "Take probiotics to restore healthy bacteria",
                    "Monitor symptoms and complete full course of antibiotics"
                ],
                "risky": [
                    "Seek immediate medical attention",
                    "Do not delay antibiotic treatment",
                    "Monitor for signs of kidney infection (fever, back pain)",
                    "Stay well hydrated",
                    "Avoid sexual activity until symptoms resolve",
                    "Consider hospitalization for severe cases"
                ]
            },
            "Common Cold": {
                "normal": [
                    "Get plenty of rest",
                    "Drink warm fluids like tea or soup",
                    "Use saline nasal sprays",
                    "Gargle with warm salt water",
                    "Use a humidifier to moisten air"
                ],
                "intermediate": [
                    "Take over-the-counter cold medications as directed",
                    "Use decongestants for nasal congestion",
                    "Take cough suppressants if needed",
                    "Apply vapor rub to chest and throat",
                    "Increase vitamin C and zinc intake",
                    "Monitor for signs of secondary infection"
                ],
                "risky": [
                    "Seek medical attention if symptoms worsen",
                    "Monitor for signs of pneumonia or bronchitis",
                    "Watch for high fever or difficulty breathing",
                    "Avoid contact with others to prevent spread",
                    "Consider prescription medications if needed",
                    "Rest completely and avoid physical exertion"
                ]
            },
            "Fungal infection": {
                "normal": [
                    "Keep affected area clean and dry",
                    "Use over-the-counter antifungal creams",
                    "Wear loose, breathable clothing",
                    "Change socks and underwear frequently",
                    "Avoid sharing personal items"
                ],
                "intermediate": [
                    "Apply prescription antifungal medications",
                    "Use antifungal powders in shoes and socks",
                    "Wash affected areas with antifungal soap",
                    "Keep areas well-ventilated",
                    "Consider oral antifungal medications if prescribed",
                    "Monitor for signs of spreading or worsening"
                ],
                "risky": [
                    "Seek immediate medical attention",
                    "Do not delay treatment with prescription medications",
                    "Monitor for signs of secondary bacterial infection",
                    "Keep affected areas completely dry",
                    "Consider hospitalization for severe cases",
                    "Follow dermatologist's treatment plan strictly"
                ]
            },
            "Drug Reaction": {
                "normal": [
                    "Stop taking the medication immediately",
                    "Contact your doctor or pharmacist",
                    "Monitor symptoms closely",
                    "Keep a record of the reaction",
                    "Stay hydrated"
                ],
                "intermediate": [
                    "Seek medical attention promptly",
                    "Take antihistamines if prescribed",
                    "Apply cool compresses to affected areas",
                    "Avoid the medication and similar drugs",
                    "Carry a list of known drug allergies",
                    "Consider allergy testing"
                ],
                "risky": [
                    "Seek immediate emergency medical attention",
                    "Call emergency services if severe symptoms develop",
                    "Do not take any new medications without doctor approval",
                    "Monitor for signs of anaphylaxis",
                    "Carry emergency epinephrine if prescribed",
                    "Wear a medical alert bracelet"
                ]
            },
            "GERD": {
                "normal": [
                    "Eat smaller, more frequent meals",
                    "Avoid lying down for 2-3 hours after eating",
                    "Elevate head of bed by 6-8 inches",
                    "Avoid trigger foods (spicy, fatty, acidic)",
                    "Maintain healthy weight"
                ],
                "intermediate": [
                    "Take prescribed acid-reducing medications",
                    "Use over-the-counter antacids as needed",
                    "Avoid tight clothing around waist",
                    "Quit smoking and limit alcohol",
                    "Manage stress through relaxation techniques",
                    "Consider dietary modifications"
                ],
                "risky": [
                    "Seek immediate medical attention",
                    "Monitor for signs of complications (bleeding, difficulty swallowing)",
                    "Follow strict dietary restrictions",
                    "Take medications exactly as prescribed",
                    "Consider surgical evaluation if symptoms persist",
                    "Avoid all trigger foods and beverages"
                ]
            },
            "Bronchial Asthma": {
                "normal": [
                    "Use rescue inhaler as prescribed",
                    "Avoid known triggers (pollen, dust, smoke)",
                    "Monitor peak flow readings",
                    "Keep rescue inhaler readily available",
                    "Practice breathing exercises"
                ],
                "intermediate": [
                    "Take controller medications as prescribed",
                    "Use rescue inhaler before symptoms worsen",
                    "Monitor symptoms and peak flow daily",
                    "Avoid triggers and maintain clean environment",
                    "Consider allergy testing and treatment",
                    "Have an asthma action plan"
                ],
                "risky": [
                    "Seek immediate emergency medical attention",
                    "Use rescue inhaler immediately",
                    "Call emergency services if symptoms don't improve",
                    "Do not delay treatment",
                    "Monitor for signs of respiratory failure",
                    "Follow emergency asthma action plan"
                ]
            }
        }
    
    def _load_symptom_severity(self) -> Dict[str, int]:
        """Define severity scores for individual symptoms"""
        return {
            "high_fever": 3,
            "breathlessness": 3,
            "chest_pain": 3,
            "vomiting": 2,
            "nausea": 2,
            "fatigue": 1,
            "headache": 2,
            "cough": 1,
            "continuous_sneezing": 1,
            "watering_from_eyes": 1,
            "shivering": 2,
            "chills": 2,
            "skin_rash": 2,
            "itching": 1,
            "stomach_pain": 2,
            "diarrhoea": 2,
            "acidity": 1,
            "indigestion": 1,
            "ulcers_on_tongue": 2,
            "blackheads": 1,
            "blister": 2,
            "nodal_skin_eruptions": 3,
            "dischromic _patches": 2,
            "muscle_pain": 1
        }
    
    def classify_disease_stage(self, disease: str, symptoms: List[str]) -> Tuple[str, str, float]:
        """
        Classify the stage of a disease based on symptoms
        
        Args:
            disease: The predicted disease name
            symptoms: List of reported symptoms
            
        Returns:
            Tuple of (stage, description, severity_score)
        """
        if disease not in self.disease_stages:
            return "normal", "Unknown disease stage", 1
        
        disease_info = self.disease_stages[disease]
        symptom_set = set(symptoms)
        
        # Calculate continuous severity percentage based on symptoms
        if symptoms:
            per_symptom_max = 3  # max in mapping
            total_severity = sum(self.symptom_severity_mapping.get(symptom, 1) for symptom in symptoms)
            severity_percentage = (total_severity / (len(symptoms) * per_symptom_max)) * 100.0
        else:
            severity_percentage = 0.0
        
        # Determine stage based on symptom overlap and severity percentage
        best_match = "normal"
        best_score = 0
        
        for stage, stage_info in disease_info.items():
            stage_symptoms = set(stage_info["symptoms"])
            overlap = len(symptom_set.intersection(stage_symptoms))
            # score considers overlap; severity boosts if above stage's nominal threshold
            nominal_pct = (stage_info["severity_score"] / 3.0) * 100.0
            stage_score = overlap + (1 if severity_percentage >= nominal_pct else 0)
            
            if stage_score > best_score:
                best_score = stage_score
                best_match = stage
        
        # Override with severity-based classification using percentage thresholds
        # Make single-symptom cases less likely to be risky unless extremely severe
        if severity_percentage >= 75:
            if len(symptoms) >= 2 or severity_percentage >= 90:
                best_match = "risky"
            else:
                best_match = max(best_match, "intermediate")  # keep at least intermediate
        elif severity_percentage >= 40:
            best_match = "intermediate"
        
        stage_info = disease_info[best_match]
        # Return stage and continuous severity percentage
        return best_match, stage_info["description"], float(round(severity_percentage, 2))
    
    def get_stage_prevention(self, disease: str, stage: str) -> List[str]:
        """
        Get prevention and treatment recommendations for a specific disease stage
        
        Args:
            disease: The disease name
            stage: The disease stage (normal, intermediate, risky)
            
        Returns:
            List of prevention recommendations
        """
        if disease not in self.stage_preventions:
            return ["Consult a healthcare provider for personalized advice"]
        
        if stage not in self.stage_preventions[disease]:
            return ["Consult a healthcare provider for personalized advice"]
        
        return self.stage_preventions[disease][stage]
    
    def get_comprehensive_advice(self, disease: str, symptoms: List[str]) -> Dict:
        """
        Get comprehensive advice including stage classification and prevention
        
        Args:
            disease: The predicted disease name
            symptoms: List of reported symptoms
            
        Returns:
            Dictionary containing stage, description, severity, and prevention advice
        """
        stage, description, severity_pct = self.classify_disease_stage(disease, symptoms)
        prevention_advice = self.get_stage_prevention(disease, stage)
        
        return {
            "disease": disease,
            "stage": stage,
            "stage_description": description,
            # severity_score now represents a 0-100 percentage
            "severity_score": severity_pct,
            "severity_percentage": severity_pct,
            "symptoms": symptoms,
            "prevention_advice": prevention_advice,
            "stage_color": self._get_stage_color(stage),
            "stage_icon": self._get_stage_icon(stage)
        }
    
    def _get_stage_color(self, stage: str) -> str:
        """Get color code for stage display"""
        colors = {
            "normal": "#28a745",      # Green
            "intermediate": "#ffc107", # Yellow
            "risky": "#dc3545"        # Red
        }
        return colors.get(stage, "#6c757d")
    
    def _get_stage_icon(self, stage: str) -> str:
        """Get icon for stage display"""
        icons = {
            "normal": "✅",
            "intermediate": "⚠️",
            "risky": "🚨"
        }
        return icons.get(stage, "❓")

# Create global instance
disease_stage_classifier = DiseaseStageClassifier()

def get_disease_stage_info(disease: str, symptoms: List[str]) -> Dict:
    """
    Convenience function to get disease stage information
    
    Args:
        disease: The predicted disease name
        symptoms: List of reported symptoms
        
    Returns:
        Dictionary containing comprehensive disease stage information
    """
    return disease_stage_classifier.get_comprehensive_advice(disease, symptoms)

if __name__ == "__main__":
    # Test the disease stage classifier
    test_cases = [
        ("Allergy", ["continuous_sneezing", "watering_from_eyes"]),
        ("Gastroenteritis", ["stomach_pain", "diarrhoea", "vomiting", "high_fever"]),
        ("Migraine", ["headache", "fatigue", "nausea", "vomiting"]),
        ("Bronchial Asthma", ["cough", "breathlessness", "chest_pain", "high_fever"])
    ]
    
    print("Testing Disease Stage Classifier")
    print("=" * 50)
    
    for disease, symptoms in test_cases:
        result = get_disease_stage_info(disease, symptoms)
        print(f"\nDisease: {result['disease']}")
        print(f"Stage: {result['stage']} {result['stage_icon']}")
        print(f"Description: {result['stage_description']}")
        print(f"Severity Score: {result['severity_score']}")
        print(f"Symptoms: {', '.join(result['symptoms'])}")
        print("Prevention Advice:")
        for i, advice in enumerate(result['prevention_advice'], 1):
            print(f"  {i}. {advice}")
        print("-" * 30)
