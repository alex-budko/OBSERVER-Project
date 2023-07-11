from flask import Flask, request
import openai
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

openai.api_key = "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"

MODEL = "gpt-4.0"


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
    system_message = f"""
    Given the following patient's message to a doctor: '{message}'. Please analyze and categorize its literacy level, considering factors like grammar, vocabulary complexity, sentence structure, and possible regional linguistic influences. Use the U.S. school grade system for categorization.    
    Please provide only the classification level, such as "Elementary School", "Middle School", "High School", or "College Level", without any additional explanation or reasoning.
    """

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
    system_message = f"""
    You are a language AI tasked with assisting in medical communication. The following is a message from a patient to a doctor: "{message}". This message might contain grammatical, syntactical, or usage errors, and it may not be entirely clear. 
    """

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
    system_message = f"""Imagine you are the patient's personal healthcare provider (doctor), responding to a message from them in chat."""
    
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
    #  {"message": "Just wanted to make sure that you got my reply from yesterday regarding all of my symptoms are the same - nothing different and all of the previous epidurals worked great.  Pain pretty bad so hope apt will be soon.",
    #  "response": "Good morning. I notified Dr Smith and he will call you this afternoon."},
    # {"message": "I meant 311lbs not 211lbs geez. I also have multiple spine fractures. I am willing to try anything you have to offer to get to a healthy weight! Talk to you soon.",
    #     "response": "I am going to take do you down 50 mL x 11 hrs. This will decrease your calories and help with safe weight loss. If you have increased the rate from the original let meknow and I can adjust that for you!"},
    # {"message": "Good morning. I wanted to confirm if Dr. Smith has reviewed my result. How does it look like?",
    #     "response": "fibroscan demonstrates changes consistent with a moderate amount of fat deposition within the liver supporting a diagnosis of fatty liver disease.  The good news is that he does not appear to have any significant fibrosis in the liver.  As a result, I think we can have him work on weight loss to see if his liver enzymes improve.  If they do, then no additional evaluation would be warranted.  If they do not improve over time, then we may consider a biopsy in the future.  He should work on weight loss as we discussed in clinic and plan to repeat his liver enzymes in 3 months. Our scheduler will contact you to arrange your follow up appointment. Please contact our office with any liver related questions as needed. Thanks"},
    # {"message": "Have you received results from biopsy from July 19",
    #     "response": "Your biopsy was negative. Please call our office to schedule a consult to discuss your plan of care."},
    # {"message": "I just read the x-ray report from my visit.  I’m concerned with the Cardiomegaly.  Is the enlarged heart due to the stomach being in my chest?",
    #     "response": "Thank you for your note. Abnormal position of the stomach would be unlikely to cause enlarged heart.  Pursuing with cardiologist or PCP would be appropriate."},
    # {"message": "Good morning. I have noticed since Sunday that I has ptosis  on the right side it is not worse but it is not better. I am asymptomatic otherwise, but I get tired easy. What do you think?",
    #     "response": "Any concern for any neurologic symptoms?  I may need to see him too to make sure its not anything else going on."},
    # {"message": "Hope you're doing well. I called yesterday about my  cold which has now turned into a sinus infection. My temp is up and I have bright orange drainage. I'm coughing. My ears are also  congested. I'm hoping you will be able to prescribe me something without an office visit since you know my history with these.",
    #     "response": "I have called in a prescription to your pharmacy. Please go to urgent care or schedule a visit if you do not start to feel better in a few days."},
    # {"message": "Do you have my lab results?",
    #     "response": "I noticed that chemistry tests were also run at that time and the calcium is minimally high.  This should be repeated to see if that continues or was simply a lab fluctuation."},
    # {"message": "Did you see my results? Is it ok to continue meds as prescribed?",
    #     "response": "Dr X reviewed your labs that were drawn on the 11th and says that you can continue on medication. Your labs are fine. Please take the Soriatane prior to your biggest meal each day."},
    # {"message": "Since quitting the Sertraline an, I feel  more energy. I guess it is working. I would appreciate if you can send a refill prescription for Bupropion to my Pharmacy. Thank!",
    #     "response": "Refill sent to pharmacy. You should be able to pick up this afternoon."},
    # {"message": "I feel like I need a boost to my oxy meds. Is there one that I can adjust to help me? I'm struggling to get anything done each day.",
    #     "response": "I really need to see you in person before making adjustments in your pain medication.  Both future appts you had scheduled with me were canceled. Please call my officeto schedule a new appointment."},
    # {"message": "She is having a scan of her abdomen tomorrow and we need to schedule an appointment for her to see you to discuss the results and some trouble she has been having.  Please ask someone to give me a call  to set up an appointment. Thank you",
    #     "response": "That works. I'll ask for a follow up in a couple of weeks"},
    # {"message": "I have been treated by primary physician for bronchitis that has caused wheezing, chest tightness, and a horrible cough. I had a chest x-ray Friday and it was okay. I took levaquin for 7 days.  I added musinex to the normal medications. The cough has improved a little but it is still frequent. Is there any thing else I can do to get over this sickness?",
    #     "response": "I am sorry you do not feel well. It is possible that you had viral infection"}
]


original_message = "Mornin'. My leg has been feelin' weird lattely. I's scared of y'all doctors, do I still need to come in?"

# original_message = """Good morning, Doctor. I hope this message finds you well. Over the past week, I've observed a persistent, aberrant sensation in my left lower limb. It's predominantly a numbness interspersed with bouts of tingling, very akin to the sensations evoked by the classic "pins and needles."

# These symptoms have been isolated to my left leg, extending from the knee to the ankle and seem to be exacerbated when I engage in extended periods of sitting or standing. I've noted some relief upon elevating the leg or with light ambulation. No discernible swelling, color change, or temperature differences have been detected.

# Although I have refrained from self-diagnosis, my preliminary research suggests possibilities ranging from peripheral neuropathy to a potential circulation issue, but I am well aware of the limitations of self-evaluation and the broad differential this could entail.

# I am cognizant of the fact that this could be a symptom of a more complex underlying condition and therefore, despite my instinct to downplay this, I believe it's necessary to solicit your professional advice. Your insight would be much appreciated. Thank you."""

_, urgency = process_message(original_message)
