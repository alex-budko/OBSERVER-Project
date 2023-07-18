from flask import Flask, request
import openai
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

openai.api_key = "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"

MODEL = "gpt-3.5-turbo"


def process_message(original_message):
    literacy_level = analyze_literacy_level(original_message)

    print("Literacy Level: ", literacy_level)
    corrected_message = correct_grammar(original_message)
    urgency = classify_urgency(corrected_message)

    print("Urgency: ", urgency)
    response = generate_response(samples, corrected_message)
    final_response = apply_literacy_level_grammar(response, literacy_level)

    print("Final Response: ", final_response)

    return final_response, urgency


def process_csv_file(filename):
    df = pd.read_csv(filename)

    if 'patient_message' not in df.columns:
        raise ValueError(
            "The provided CSV file must contain a 'patient_message' column.")

    for column in ['literacy_level', 'urgency_level', 'generated_response']:
        if column not in df.columns:
            df[column] = None

    for index, row in df.iterrows():
        patient_message = row['patient_message']
        literacy_level = analyze_literacy_level(patient_message)
        corrected_message = correct_grammar(patient_message)
        urgency = classify_urgency(corrected_message)
        response, _ = generate_response(
            samples, corrected_message, literacy_level)

        df.loc[index, 'literacy_level'] = literacy_level
        df.loc[index, 'urgency_level'] = urgency
        df.loc[index, 'generated_response'] = response

    df.to_csv(filename, index=False)


def analyze_literacy_level(message):
    system_message = f"""Analyze the literacy level of the following patient's message to a doctor: '{message}', based on grammar, vocabulary complexity, sentence structure, and regional linguistic influences. Categorize using the U.S. school grade system, and provide only the classification, e.g., 'Elementary School', 'Middle School', 'High School', or 'College Level', without further explanation."""

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_message}],
        temperature=0.1,
        max_tokens=60
    )

    literacy_level = response['choices'][0]['message']['content'].strip()
    literacy_level = literacy_level.split(":")[-1].strip()

    return literacy_level


def correct_grammar(message):
    system_message = f"""You are a language AI tasked with assisting in medical communication. The following is a message from a patient to a doctor: "{message}". This message might contain grammatical, syntactical, or usage errors."""

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
        ],
        temperature=0.5,
        max_tokens=200
    )

    corrected_message = response['choices'][0]['message']['content'].strip()

    return corrected_message


def classify_urgency(message):
    system_message = f"""
        Classify the urgency of the following medical message: "{message}". Use the following classifications: 
        R - immediate evaluation by a physician
        O - emergent, evaluation within 15 min
        Y - potentially unstable, evaluation within 60 min
        G - non-urgent, re-evaluation every 180 min
        B - minor injuries or complaints, re-evaluation every 240 min
        """
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
        ],
        temperature=0.1,
        max_tokens=60
    )

    urgency = response['choices'][0]['message']['content'].strip()

    return urgency


def generate_response(samples, new_message):
    system_message = f"""As an AI, please simulate the professional role of the patient's personal physician and interact appropriately with their chat messages. If a situation arises where an office visit is required, instruct them to visit 'my' office."""
    messages = []

    messages.append({"role": "system", "content": system_message})

    for sample in samples:
        messages.extend([
            {"role": "user", "content": sample['message']},
            {"role": "assistant", "content": sample['response']}
        ])

    messages.append({"role": "user", "content": new_message})

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=150
    )

    reply = response['choices'][0]['message']['content'].strip()

    print(f"\nGenerated response: {reply}")

    samples.append({"message": new_message, "response": reply})

    return reply


def apply_literacy_level_grammar(message, literacy_level):
    system_message = f"Assistant, please adjust the following message to a '{literacy_level}' literacy level. Ensure that all the concepts of the message persist. Limit the response to 250 characters"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=250
    )
    adjusted_message = response['choices'][0]['message']['content'].strip()
    return adjusted_message

samples = [
    {"message": "I will be visiting my parents out of town for the holidays from December 10th to January 2nd. Is it preferable to schedule my next appointment before I leave, or should we wait until I return?",
     "response": "It's great that you're thinking ahead. If your health allows, I would suggest scheduling your next appointment in my office before you leave to ensure continuity of care. If you'd prefer to wait until after your trip, we can certainly arrange that as well."},
    
    {"message": "I'll be tied up with school exams from April 20th to May 5th. Can we plan my follow-up visit either before or after my exams?",
     "response": "Of course, let's take your exam schedule into account. I suggest we schedule your follow-up visit in my office before your exams begin. This way, we can address any health concerns you may have and allow you to focus on your studies."},
    
    {"message": "Due to a work project, I'm likely to be occupied from September 1st to 15th. Would it be best to book my next consultation before this period?",
     "response": "I understand your work commitments and we should avoid scheduling your consultation during that busy period. Let's schedule your next visit in my office before September 1st. This way, we can ensure any health issues don't interfere with your work project."},
    
    {"message": "I've been having issues with my right ankle for a while. I've been seeing a physiotherapist for a couple of months and recently started feeling a sharp pain radiating up my leg. I wake up with this pain that fades once I start moving around. Additionally, I'm experiencing frequent numbness in my toes. I've been taking over-the-counter pain relievers, but I'm unsure if it's time to consider other treatment options or to revisit physiotherapy.",
     "response": "The symptoms you're describing indicate that we may need to re-evaluate your condition. It could be that physiotherapy alone is not sufficient or that your condition has changed. Please come into my office for an appointment at your earliest convenience so we can reassess your symptoms and modify your treatment plan as necessary."},
    
    {"message": "I have an appointment scheduled with Dr. X on November 15th. However, my chronic migraines have been increasingly affecting my ability to perform daily tasks. I've been managing with ibuprofen and rest, but I'm not sure if it's enough. Can you suggest a short-term treatment plan to help alleviate my symptoms until my appointment?",
     "response": "I understand how debilitating chronic migraines can be. Until your scheduled appointment with Dr. X, let's try to manage your symptoms more effectively. You might benefit from combining ibuprofen with a medication specifically designed for migraines, such as a triptan. However, if your symptoms worsen, please come in to see me sooner."},
    
    {"message": "I've been under treatment for my high blood pressure and have been maintaining a balanced diet and regular exercise. However, in the past week, I've noticed an unusual increase in my readings. I've been diligent with my medication, but I'm unsure if this is a cause for concern.",
     "response": "Blood pressure can fluctuate due to various factors, but a sustained increase could be cause for concern. I would recommend you monitor your blood pressure daily for a week and keep a log. If the readings continue to be higher than normal, please come into my office for an earlier appointment to reassess your treatment."},
    
    {"message": "I've been experiencing frequent and severe heartburn and occasional difficulty swallowing. My diet is rich in spicy foods and carbonated drinks. I've also been consuming alcohol more frequently. My work schedule often leads to late-night meals, and I tend to lie down soon after eating. I've gained a considerable amount of weight in the past year and have become more sedentary. Could these factors be contributing to my symptoms? Are these symptoms indicative of a possible digestive disorder like gastroesophageal reflux disease (GERD)?",
     "response": "Your symptoms and lifestyle could indeed be contributing to a condition like GERD. I suggest you come into my office for an appointment to discuss potential lifestyle modifications and further evaluations."},
    
    {"message": "I've been dealing with persistent lower back pain for several months now. My job involves long hours of sitting, and I rarely take breaks to stretch or move around. My daily physical activity is minimal, and I've gained weight over the past year. I've also been lifting heavy objects at home without using proper form. My stress levels have been high, and my sleep quality has deteriorated. Could these lifestyle factors be contributing to my back pain? Could I be at risk of developing chronic back issues or conditions like a herniated disc?",
     "response": "Your lifestyle factors could be contributing to your back pain and might increase your risk of developing chronic back conditions. I recommend you come into my office for an appointment so we can evaluate your situation and discuss appropriate interventions."},
    
    {"message": "I've been experiencing persistent and troubling changes in my bowel habits. I often feel bloated and gassy. My diet is low in fiber and high in processed foods. I've also been consuming more alcohol and less water than usual. My sedentary lifestyle and high-stress job have made it difficult to maintain regular physical activity. I have a family history of colon cancer. Could these factors be contributing to my symptoms? Could my current lifestyle and family history be increasing my risk for conditions like Irritable Bowel Syndrome (IBS) or colon cancer?",
     "response": "Your lifestyle factors, combined with your family history, could be contributing to your symptoms and possibly increase your risk for conditions like IBS or colon cancer. It's important that you come into my office for an appointment at your earliest convenience for a thorough evaluation and necessary tests."}
]

patient_messages = [
    "Hey, my head hurts. What should I do?",
]

for message in patient_messages:
    print(f"Patient Message: {message}\n")
    response, urgency = process_message(message)

