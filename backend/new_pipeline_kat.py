# Message generation pipeline with category

# TODO: Flask

import openai

openai.api_key = "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"

MODEL = "gpt-3.5-turbo"


def literacy_level_analysis(message):
    '''
    Function for Literacy Level Analysis
    '''
    system_message = f"You are a literacy assistant that answers in one word. Your job is to estimate the literacy level of messages. Is it elementary, middleschool, highschool or higher-education level?"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=50
    )
    literacy_level = response['choices'][0]['message']['content'].strip(
    ).lower()
    print(f"Literacy level: {literacy_level}")
    return literacy_level


def grammar_edit(message):
    '''
    Function for editing grammar
    '''
    system_message = "You are a grammer assistant. Your job is to correct any grammatical errors in the messages."
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=100
    )
    corrected_message = response['choices'][0]['message']['content'].strip()
    print(f"Corrected message: {corrected_message}")
    return corrected_message


def urgency_classification(message):
    '''
    Function for classifying urgency
    '''
    system_message = f"""
    Your are an urgency clasifier.
    Classify the urgency of the following medical messages. Use the following classifications, answer with the letter and the description: 
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
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=50
    )
    urgency = response['choices'][0]['message']['content'].strip().lower()
    print(f"Urgency level: {urgency}")
    return urgency


def apply_literacy_level_grammar(message, literacy_level):
    '''
    Function for applying literacy level
    '''
    system_message = f"You are a literacy assistant. Your job is to adjust the messages to a '{literacy_level}' literacy level while keeping everything else (tone, person) unchanged."
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=100
    )
    adjusted_message = response['choices'][0]['message']['content'].strip()
    return adjusted_message


def categorize_input(samples, new_message):
    # Extract categories from samples
    sample_categories = set(sample['category'] for sample in samples)
    possible_categories = ', '.join(sample_categories)

    # Print received messages
    print(f"Received message: {new_message}")

    messages = []

    system_message = f"You are a doctor. Your job is to categorize messages sent to you from patients. You answer must be one from this list of possible categories: {possible_categories}. You should only respond with one category."
    messages.append(
        {"role": "system", "content": system_message})

    for sample in samples:
        messages += [
            {"role": "user", "content": sample["message"]},
            {"role": "assistant",
                "content": f"{sample['category']}"},
        ]

    messages.append({"role": "user", "content": new_message})

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=50
    )

    category = response['choices'][0]['message']['content'].strip()

    print(f"Message intially categorized as: {category}")

    # Check that the outputted category is a valid category from the samples
    if category not in sample_categories:
        print("Category not found in samples. Defaulting to 'Prognosis'.")
        category = "Prognosis"

    print(f"Message categorized as: {category}")

    return category


def generate_response(samples, message, category, literacy_level, urgency):
    sample_messages = [
        sample for sample in samples if sample['category'] == category]

    system_message = f"""You are the doctor that the patient will come see. Your job is to generate a short (ideally less than 150 characters), empathetic, and medically-accurate messages to patient messages in the category {category} and urgency level {urgency}."""

    messages = [{"role": "system", "content": system_message}]

    for sample in sample_messages:
        messages.append({"role": "user", "content": sample['message']})
        messages.append({"role": "assistant", "content": sample['response']})

    # Add the current message
    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=450
    )

    # print(response)

    reply = response['choices'][0]['message']['content']
    print(f"Original generated response: {reply}")

    samples.append(
        {"message": message, "category": category, "response": reply})

    return reply, samples


# Step 1: Collect sample inputs and categories
samples = [
    {"message": "Just wanted to make sure that you got my reply from yesterday regarding all of my symptoms are the same - nothing different and all of the previous epidurals worked great.  Pain pretty bad so hope apt will be soon.",
        "category": "Risk factors for disease", "response": "Good morning. I notified Dr Smith and he will call you this afternoon."},
    {"message": "I meant 311lbs not 211lbs geez. I also have multiple spine fractures. I am willing to try anything you have to offer to get to a healthy weight! Talk to you soon.", "category": "Risk factors for disease",
        "response": "I am going to take do you down 50 mL x 11 hrs. This will decrease your calories and help with safe weight loss. If you have increased the rate from the original let me know and I can adjust that for you!"},
    {"message": "Good morning. I wanted to confirm if Dr. Smith has reviewed my result. How does it look like?", "category": "Interpretation of Test Results",
        "response": "fibroscan demonstrates changes consistent with a moderate amount of fat deposition within the liver supporting a diagnosis of fatty liver disease.  The good news is that he does not appear to have any significant fibrosis in the liver.  As a result, I think we can have him work on weight loss to see if his liver enzymes improve.  If they do, then no additional evaluation would be warranted.  If they do not improve over time, then we may consider a biopsy in the future.  He should work on weight loss as we discussed in clinic and plan to repeat his liver enzymes in 3 months. Our scheduler will contact you to arrange your follow up appointment. Please contact our office with any liver related questions as needed. Thanks"},
    {"message": "Have you received results from biopsy from July 19", "category": "Interpretation of Test Results",
        "response": "Your biopsy was negative. Please call our office to schedule a consult to discuss your plan of care."},
    {"message": "I just read the x-ray report from my visit.  I’m concerned with the Cardiomegaly.  Is the enlarged heart due to the stomach being in my chest?", "category": "Interpretation of Test Results",
        "response": "Thank you for your note. Abnormal position of the stomach would be unlikely to cause enlarged heart.  Pursuing with cardiologist or PCP would be appropriate."},
    {"message": "Good morning. I have noticed since Sunday that I has ptosis  on the right side it is not worse but it is not better. I am asymptomatic otherwise, but I get tired easy. What do you think?",
        "category": "Prognosis", "response": "Any concern for any neurologic symptoms?  I may need to see him too to make sure its not anything else going on."},
    {"message": "Hope you're doing well. I called yesterday about my  cold which has now turned into a sinus infection. My temp is up and I have bright orange drainage. I'm coughing. My ears are also  congested. I'm hoping you will be able to prescribe me something without an office visit since you know my history with these.",
        "category": "Prognosis", "response": "I have called in a prescription to your pharmacy. Please go to urgent care or schedule a visit if you do not start to feel better in a few days."},
    {"message": "Do you have my lab results?", "category": "Post Test Care",
        "response": "I noticed that chemistry tests were also run at that time and the calcium is minimally high.  This should be repeated to see if that continues or was simply a lab fluctuation."},
    {"message": "Did you see my results? Is it ok to continue meds as prescribed?", "category": "Post Test Care",
        "response": "Dr X reviewed your labs that were drawn on the 11th and says that you can continue on medication. Your labs are fine. Please take the Soriatane prior to your biggest meal each day."},
    {"message": "Since quitting the Sertraline an, I feel  more energy. I guess it is working. I would appreciate if you can send a refill prescription for Bupropion to my Pharmacy. Thank!",
        "category": "Med Management", "response": "Refill sent to pharmacy. You should be able to pick up this afternoon."},
    {"message": "I feel like I need a boost to my oxy meds. Is there one that I can adjust to help me? I'm struggling to get anything done each day.", "category": "Med Management",
        "response": "I really need to see you in person before making adjustments in your pain medication.  Both future appts you had scheduled with me were canceled. Please call my office to schedule a new appointment."},
    {"message": "She is having a scan of her abdomen tomorrow and we need to schedule an appointment for her to see you to discuss the results and some trouble she has been having.  Please ask someone to give me a call  to set up an appointment. Thank you",
        "category": "When to Follow Up", "response": "That works. I'll ask for a follow up in a couple of weeks"},
    {"message": "I have been treated by primary physician for bronchitis that has caused wheezing, chest tightness, and a horrible cough. I had a chest x-ray Friday and it was okay. I took levaquin for 7 days.  I added musinex to the normal medications. The cough has improved a little but it is still frequent. Is there any thing else I can do to get over this sickness?",
        "category": "When to Follow Up", "response": "I am sorry you do not feel well. It is possible that you had viral infection. There is no treatment for cough associated with viral respiratory infections, cough suppressants could provide some relief especially at night. Corticosteroids are usually not helpful. It might be important to consider testing for whooping cough."}
]

# samples = []


message = '''
How much epipnephrine can i take when i have anaphalaxis?
'''

# Step 2: Analyze Literacy Level
literacy_level = literacy_level_analysis(message)

# Step 3: Grammar Edit
message = grammar_edit(message)

# Step 4: Categorize Input
category = categorize_input(samples, message)

# Step 5: Urgency Classification
urgency = urgency_classification(message)

# Step 6: Generate Response
reply, _ = generate_response(
    samples, message, category, literacy_level, urgency)

# Step 7: Apply Literacy Level Grammar
final_message = apply_literacy_level_grammar(reply, literacy_level)

print(f"Final response (after applying literacy level): {final_message}")
