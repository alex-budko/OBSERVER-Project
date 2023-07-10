from flask import Flask, request
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

openai.api_key = "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"

MODEL = "gpt-3.5-turbo"

def analyze_literacy_level(message):
    system_message = f"""
    Given the following patient's message to a doctor, please analyze and categorize its literacy level, considering factors like grammar, vocabulary complexity, sentence structure, and possible regional linguistic influences. Use the U.S. school grade system for categorization, where 1st grade represents basic literacy and a College level indicates a highly advanced literacy level.
    
    The message is: '{message}'. 

    Consider the following:
    - If the message uses simple sentences, basic vocabulary, and contains grammatical errors, you might categorize it as 'Elementary School' level.
    - If the message includes complex vocabulary, flawless grammar, and concepts indicative of higher education, it might be 'College level'.
    - If the message shows signs of regional dialect or slang, please mention it as well.
    """

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_message}],
        temperature=0.5,
        max_tokens=100
    )

    literacy_level = response['choices'][0]['message']['content'].strip()

    return literacy_level

def correct_grammar(message):
    system_message = f"""
    You are a language AI tasked with assisting in medical communication. The following is a message from a patient to a doctor: "{message}". This message might contain grammatical, syntactical, or usage errors, and it may not be entirely clear. 

    Your task is threefold:

    1. Correct the language errors: Fix any grammatical, spelling, punctuation, or syntactical errors in the message.
    2. Improve clarity and readability: Ensure the message is easily understandable, while preserving the original meaning and patient's tone. 
    3. Optimize for medical analysis: Make sure the language used and the structure of the message supports further analysis of its content, especially for determining the level of urgency and preparing for a doctor's response.

    Remember, accurate communication is paramount in a medical context.
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
        temperature=0.5,
        max_tokens=60
    )

    urgency = response['choices'][0]['message']['content'].strip()

    return urgency

def generate_response(samples, new_message, literacy_level):    
    system_message = f"""
        As an advanced language model, your mission is to generate a response to the patient's message below. This response should be tailored not only to be empathetic, clinically accurate, and confidential, but also to match the patient's literacy level and communication style. Keep in mind the following:

        - Clinical Accuracy: Base your response on current, evidence-based medical guidelines and practices.
        - Empathy and Compassion: Show understanding and kindness in your response. Acknowledge the patient's feelings, provide reassurance, and if necessary, offer comfort.
        - Strict Confidentiality: Your response should never include any personally identifiable information.
        - Adaptability: Mirror the patient's language style and complexity. If the patient uses simple language, respond with simple, clear language. If they use medical jargon, you can use similar language.
        - Clarity and Simplification: If complex medical concepts are involved, break them down into simpler, more understandable explanations.

        The patient's literacy level is estimated to be '{literacy_level}'.

        Now, generate a simulated response as if you are a doctor, maintaining the balance of medical accuracy, empathy, confidentiality, and appropriate literacy level.
        """

    messages = []

    messages = [{"role": "system", "content": system_message}]

    for sample in samples:
        messages.extend([
            {"role": "user", "content": sample['message']},
            {"role": "assistant", "content": sample['response']}
        ])

    messages.append({"role": "user", "content": new_message})

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=150
    )

    reply = response['choices'][0]['message']['content'].strip()

    print(f"\nGenerated response: {reply}")

    samples.append({"message": new_message, "response": reply})

    return reply, samples

# Step 1: Collect sample inputs and responses
samples = [
    {"message": "Just wanted to make sure that you got my reply from yesterday regarding all of my symptoms are the same - nothing different and all of the previous epidurals worked great.  Pain pretty bad so hope apt will be soon.",
        "response": "Good morning. I notified Dr Smith and he will call you this afternoon."},
    {"message": "I meant 311lbs not 211lbs geez. I also have multiple spine fractures. I am willing to try anything you have to offer to get to a healthy weight! Talk to you soon.",
        "response": "I am going to take do you down 50 mL x 11 hrs. This will decrease your calories and help with safe weight loss. If you have increased the rate from the original let meknow and I can adjust that for you!"},
    {"message": "Good morning. I wanted to confirm if Dr. Smith has reviewed my result. How does it look like?",
        "response": "fibroscan demonstrates changes consistent with a moderate amount of fat deposition within the liver supporting a diagnosis of fatty liver disease.  The good news is that he does not appear to have any significant fibrosis in the liver.  As a result, I think we can have him work on weight loss to see if his liver enzymes improve.  If they do, then no additional evaluation would be warranted.  If they do not improve over time, then we may consider a biopsy in the future.  He should work on weight loss as we discussed in clinic and plan to repeat his liver enzymes in 3 months. Our scheduler will contact you to arrange your follow up appointment. Please contact our office with any liver related questions as needed. Thanks"},
    {"message": "Have you received results from biopsy from July 19",
        "response": "Your biopsy was negative. Please call our office to schedule a consult to discuss your plan of care."},
    {"message": "I just read the x-ray report from my visit.  I’m concerned with the Cardiomegaly.  Is the enlarged heart due to the stomach being in my chest?",
        "response": "Thank you for your note. Abnormal position of the stomach would be unlikely to cause enlarged heart.  Pursuing with cardiologist or PCP would be appropriate."},
    {"message": "Good morning. I have noticed since Sunday that I has ptosis  on the right side it is not worse but it is not better. I am asymptomatic otherwise, but I get tired easy. What do you think?",
        "response": "Any concern for any neurologic symptoms?  I may need to see him too to make sure its not anything else going on."},
    {"message": "Hope you're doing well. I called yesterday about my  cold which has now turned into a sinus infection. My temp is up and I have bright orange drainage. I'm coughing. My ears are also  congested. I'm hoping you will be able to prescribe me something without an office visit since you know my history with these.",
        "response": "I have called in a prescription to your pharmacy. Please go to urgent care or schedule a visit if you do not start to feel better in a few days."},
    {"message": "Do you have my lab results?",
        "response": "I noticed that chemistry tests were also run at that time and the calcium is minimally high.  This should be repeated to see if that continues or was simply a lab fluctuation."},
    {"message": "Did you see my results? Is it ok to continue meds as prescribed?",
        "response": "Dr X reviewed your labs that were drawn on the 11th and says that you can continue on medication. Your labs are fine. Please take the Soriatane prior to your biggest meal each day."},
    {"message": "Since quitting the Sertraline an, I feel  more energy. I guess it is working. I would appreciate if you can send a refill prescription for Bupropion to my Pharmacy. Thank!",
        "response": "Refill sent to pharmacy. You should be able to pick up this afternoon."},
    {"message": "I feel like I need a boost to my oxy meds. Is there one that I can adjust to help me? I'm struggling to get anything done each day.",
        "response": "I really need to see you in person before making adjustments in your pain medication.  Both future appts you had scheduled with me were canceled. Please call my officeto schedule a new appointment."},
    {"message": "She is having a scan of her abdomen tomorrow and we need to schedule an appointment for her to see you to discuss the results and some trouble she has been having.  Please ask someone to give me a call  to set up an appointment. Thank you",
        "response": "That works. I'll ask for a follow up in a couple of weeks"},
    {"message": "I have been treated by primary physician for bronchitis that has caused wheezing, chest tightness, and a horrible cough. I had a chest x-ray Friday and it was okay. I took levaquin for 7 days.  I added musinex to the normal medications. The cough has improved a little but it is still frequent. Is there any thing else I can do to get over this sickness?",
        "response": "I am sorry you do not feel well. It is possible that you had viral infection"}]

def process_message(original_message):
    literacy_level = analyze_literacy_level(original_message)
    print("Literacy Level: ", literacy_level)
    corrected_message = correct_grammar(original_message)
    urgency = classify_urgency(corrected_message)
    print("Urgency: ", urgency)
    response = generate_response(samples, corrected_message, literacy_level)

    return response, urgency

original_message = ""
final_message, urgency = process_message(original_message)