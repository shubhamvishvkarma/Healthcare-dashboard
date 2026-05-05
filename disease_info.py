# Disease Information Database with Symptoms and Recommendations
# This file contains comprehensive medical information for various conditions

DISEASE_DATABASE = {
    "Asthma": {
        "symptoms": [
            "Shortness of breath",
            "Chest tightness or pain",
            "Wheezing sound when breathing",
            "Difficulty sleeping due to breathing problems",
            "Coughing fits, especially at night or during exercise"
        ],
        "risk_level": "Moderate",
        "management": [
            "Use prescribed inhalers regularly",
            "Avoid known triggers",
            "Monitor peak flow measurements",
            "Keep rescue inhaler accessible",
            "Regular follow-up with pulmonologist"
        ],
        "lifestyle": [
            "Maintain regular physical activity",
            "Avoid air pollutants and allergens",
            "Manage stress effectively",
            "Keep home dust-free",
            "Avoid smoking and secondhand smoke"
        ]
    },
    "Diabetes": {
        "symptoms": [
            "Increased thirst and frequent urination",
            "Fatigue and weakness",
            "Blurred vision",
            "Slow-healing cuts or sores",
            "Tingling or numbness in hands/feet"
        ],
        "risk_level": "High",
        "management": [
            "Regular blood glucose monitoring",
            "Follow prescribed medication regimen",
            "Maintain balanced diet with portion control",
            "Exercise 150 minutes per week",
            "Regular eye and foot examinations"
        ],
        "lifestyle": [
            "Consume whole grains and vegetables",
            "Reduce sugar and processed foods",
            "Maintain healthy weight",
            "Manage stress through meditation",
            "Get adequate sleep (7-9 hours)"
        ]
    },
    "Hypertension": {
        "symptoms": [
            "Often asymptomatic in early stages",
            "Headaches",
            "Shortness of breath",
            "Nosebleeds",
            "Dizziness or fatigue"
        ],
        "risk_level": "High",
        "management": [
            "Monitor blood pressure regularly",
            "Take prescribed antihypertensive medications",
            "Limit sodium intake to <2300mg/day",
            "Maintain healthy weight",
            "Regular cardiovascular exercise"
        ],
        "lifestyle": [
            "Reduce salt consumption",
            "Exercise 30 minutes daily",
            "Eat heart-healthy foods",
            "Limit alcohol consumption",
            "Manage stress effectively"
        ]
    },
    "Heart Disease": {
        "symptoms": [
            "Chest pain or discomfort",
            "Shortness of breath",
            "Pain in neck, jaw, or throat",
            "Fatigue",
            "Cold sweat"
        ],
        "risk_level": "Critical",
        "management": [
            "Immediate medical consultation",
            "Cardiac testing (ECG, Echocardiogram)",
            "Medication management (Statins, Beta-blockers)",
            "Cardiac rehabilitation program",
            "Regular cardiology follow-ups"
        ],
        "lifestyle": [
            "Avoid strenuous activities without clearance",
            "Follow heart-healthy diet (DASH diet)",
            "Quit smoking immediately",
            "Manage stress and anxiety",
            "Monitor weight and blood pressure"
        ]
    },
    "Arthritis": {
        "symptoms": [
            "Joint pain and stiffness",
            "Reduced range of motion",
            "Redness and warmth around joints",
            "Swelling",
            "Pain worse in morning or after activity"
        ],
        "risk_level": "Moderate",
        "management": [
            "Anti-inflammatory medications",
            "Physical therapy and exercises",
            "Hot/cold therapy",
            "Weight management to reduce joint stress",
            "Regular rheumatology consultations"
        ],
        "lifestyle": [
            "Low-impact exercises (swimming, walking)",
            "Maintain healthy weight",
            "Use assistive devices when needed",
            "Apply heat therapy before activity",
            "Manage nutrition for inflammation"
        ]
    },
    "COPD": {
        "symptoms": [
            "Chronic cough",
            "Shortness of breath",
            "Sputum production",
            "Wheezing",
            "Chest tightness"
        ],
        "risk_level": "High",
        "management": [
            "Smoking cessation mandatory",
            "Bronchodilator medications",
            "Pulmonary rehabilitation",
            "Oxygen therapy if needed",
            "Annual influenza vaccination"
        ],
        "lifestyle": [
            "Complete smoking cessation",
            "Avoid air pollution",
            "Light to moderate exercise",
            "Balanced nutrition",
            "Controlled breathing techniques"
        ]
    },
    "Obesity": {
        "symptoms": [
            "Excess body weight",
            "Shortness of breath",
            "Fatigue",
            "Joint pain",
            "Sleep apnea"
        ],
        "risk_level": "High",
        "management": [
            "Comprehensive diet plan",
            "Regular exercise program",
            "Behavioral therapy",
            "Medical nutrition therapy",
            "Consider bariatric surgery if needed"
        ],
        "lifestyle": [
            "Balanced, calorie-controlled diet",
            "Regular physical activity (150 min/week)",
            "Portion control and mindful eating",
            "Reduce sugary drinks",
            "Sleep 7-9 hours nightly"
        ]
    },
    "Liver Disease": {
        "symptoms": [
            "Jaundice (yellowing of skin/eyes)",
            "Abdominal pain",
            "Swelling in abdomen and legs",
            "Fatigue",
            "Dark urine"
        ],
        "risk_level": "Critical",
        "management": [
            "Avoid alcohol completely",
            "Hepatology consultation",
            "Liver function tests",
            "Dietary modifications (low sodium, low protein)",
            "Monitor for complications"
        ],
        "lifestyle": [
            "Complete alcohol avoidance",
            "Low-sodium diet",
            "Adequate rest",
            "Avoid hepatotoxic medications",
            "Regular medical monitoring"
        ]
    },
    "Thyroid Disorder": {
        "symptoms": [
            "Fatigue or increased energy",
            "Weight changes",
            "Temperature sensitivity",
            "Hair loss",
            "Mood changes"
        ],
        "risk_level": "Moderate",
        "management": [
            "Thyroid function tests (TSH, T3, T4)",
            "Hormone replacement therapy",
            "Regular endocrinology follow-ups",
            "Medication adherence",
            "Periodic lab monitoring"
        ],
        "lifestyle": [
            "Maintain consistent medication timing",
            "Adequate iodine intake",
            "Manage stress",
            "Regular exercise",
            "Balanced nutrition"
        ]
    },
    "Kidney Disease": {
        "symptoms": [
            "Fatigue",
            "Swelling in feet and ankles",
            "Shortness of breath",
            "Changes in urination",
            "Loss of appetite"
        ],
        "risk_level": "High",
        "management": [
            "Regular renal function monitoring",
            "Blood pressure control",
            "Dietary modifications (low sodium, controlled protein)",
            "Nephrology consultation",
            "Monitor fluid intake"
        ],
        "lifestyle": [
            "Low-sodium diet",
            "Controlled protein intake",
            "Limit potassium and phosphorus",
            "Adequate hydration",
            "Regular blood pressure monitoring"
        ]
    },
    "Cancer": {
        "symptoms": [
            # General / सामान्य लक्षण
            "अचानक वजन कम होना (Unexplained weight loss)",
            "लगातार थकान और कमजोरी (Persistent fatigue and weakness)",
            "बुखार जो ठीक न हो (Unexplained fever that doesn't resolve)",
            "त्वचा में बदलाव — पीलापन, लालिमा या गहरे धब्बे (Skin changes — yellowing, redness, or dark spots)",
            "घाव जो भरे नहीं (Sores that do not heal)",
            # Type-specific / प्रकार-विशेष लक्षण
            "गांठ या सूजन जो बढ़ती रहे (Lump or swelling that keeps growing)",
            "लगातार खांसी या आवाज में बदलाव (Persistent cough or change in voice)",
            "मल या मूत्र में खून (Blood in stool or urine)",
            "निगलने में कठिनाई (Difficulty swallowing)",
            "असामान्य रक्तस्राव या स्राव (Unusual bleeding or discharge)",
            "पाचन में बदलाव — दस्त, कब्ज या पेट दर्द (Digestive changes — diarrhea, constipation, or abdominal pain)",
            "सिरदर्द, दौरे या दृष्टि में बदलाव (Headaches, seizures, or vision changes — brain cancer)"
        ],
        "risk_level": "Critical",
        "management": [
            # Diagnosis / निदान
            "तुरंत ऑन्कोलॉजिस्ट से परामर्श लें (Immediate oncologist consultation)",
            "बायोप्सी और हिस्टोपैथोलॉजी जांच (Biopsy and histopathology examination)",
            "CT स्कैन, MRI, PET स्कैन से स्टेजिंग (Staging via CT scan, MRI, PET scan)",
            "ट्यूमर मार्कर रक्त परीक्षण (Tumor marker blood tests — CEA, CA-125, PSA, AFP)",
            # Treatment / उपचार
            "कीमोथेरेपी — कैंसर कोशिकाओं को नष्ट करने के लिए दवाएं (Chemotherapy — drugs to destroy cancer cells)",
            "रेडिएशन थेरेपी — उच्च-ऊर्जा किरणों से ट्यूमर का उपचार (Radiation therapy — high-energy beams to treat tumor)",
            "सर्जरी — ट्यूमर को शल्य चिकित्सा से हटाना (Surgery — surgical removal of tumor)",
            "इम्यूनोथेरेपी — प्रतिरक्षा प्रणाली को मजबूत करना (Immunotherapy — boosting the immune system)",
            "टार्गेटेड थेरेपी — विशिष्ट कैंसर जीन को लक्षित करना (Targeted therapy — targeting specific cancer genes)",
            "हार्मोन थेरेपी (स्तन/प्रोस्टेट कैंसर के लिए) (Hormone therapy — for breast/prostate cancer)",
            "बोन मैरो ट्रांसप्लांट (रक्त कैंसर के लिए) (Bone marrow transplant — for blood cancers)",
            "दर्द प्रबंधन और पैलिएटिव केयर (Pain management and palliative care)"
        ],
        "lifestyle": [
            # Prevention / रोकथाम
            "धूम्रपान और तंबाकू से पूरी तरह बचें (Completely avoid smoking and tobacco)",
            "शराब का सेवन सीमित या बंद करें (Limit or stop alcohol consumption)",
            "संतुलित आहार — फल, सब्जियां, साबुत अनाज (Balanced diet — fruits, vegetables, whole grains)",
            "प्रसंस्कृत और लाल मांस कम खाएं (Reduce processed and red meat intake)",
            "नियमित व्यायाम — सप्ताह में 150 मिनट (Regular exercise — 150 minutes per week)",
            "स्वस्थ वजन बनाए रखें (Maintain healthy body weight)",
            "धूप से बचाव — सनस्क्रीन और सुरक्षात्मक कपड़े (Sun protection — sunscreen and protective clothing)",
            # During Treatment / उपचार के दौरान
            "पोषण विशेषज्ञ से आहार योजना लें (Get a diet plan from a nutritionist)",
            "मानसिक स्वास्थ्य के लिए काउंसलिंग और सपोर्ट ग्रुप (Counseling and support groups for mental health)",
            "पर्याप्त नींद और आराम (Adequate sleep and rest)",
            "नियमित फॉलो-अप और स्क्रीनिंग जांच (Regular follow-up and screening checkups)",
            "HPV और हेपेटाइटिस B टीकाकरण (HPV and Hepatitis B vaccination for prevention)"
        ]
    }
}

def get_disease_info(disease_name):
    """
    Get comprehensive information about a disease.
    
    Args:
        disease_name (str): Name of the disease
        
    Returns:
        dict: Disease information including symptoms, management, and lifestyle recommendations
    """
    return DISEASE_DATABASE.get(disease_name, None)

def get_all_diseases():
    """Get list of all diseases in database"""
    return list(DISEASE_DATABASE.keys())

def format_disease_info(disease_name):
    """
    Format disease information for display.
    
    Args:
        disease_name (str): Name of the disease
        
    Returns:
        str: Formatted disease information
    """
    disease_info = get_disease_info(disease_name)
    if not disease_info:
        return f"Information for {disease_name} not found."
    
    formatted = f"""
    ### {disease_name}
    
    **Risk Level:** {disease_info['risk_level']}
    
    #### Symptoms (लक्षण)
    """
    for symptom in disease_info['symptoms']:
        formatted += f"\n- {symptom}"
    
    formatted += f"\n\n#### Management & Treatment (उपचार)\n"
    for mgmt in disease_info['management']:
        formatted += f"\n- {mgmt}"
    
    formatted += f"\n\n#### Lifestyle Recommendations (जीवनशैली सुझाव)\n"
    for lifestyle in disease_info['lifestyle']:
        formatted += f"\n- {lifestyle}"
    
    return formatted
