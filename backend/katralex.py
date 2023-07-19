
import openai
from MessageReader import MessageReader
import subprocess
import csv

openai.api_key = "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"

MODEL = "gpt-3.5-turbo"


def literacy_level_analysis(message):
    '''
    Function for Literacy Level Analysis
    '''
    system_message = f"As an assistant trained in language understanding, your role is to provide a simple one-word analysis of the literacy level in the given text. The categories are: middle-school, high-school, or higher-education."
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
    system_message = "As a grammar-checking AI, your role is to identify and correct any grammatical errors in the given text. Please produce a corrected version of the text."
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
    system_message = f"As an AI assistant with language adjustment capabilities, your role is to modify the given message to suit a '{literacy_level}' literacy level. Be sure to maintain the same tone and perspective (first, second, third person) as the original text."
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

    system_message = f"As an AI medical assistant, you have the ability to categorize patient messages. Your job is to analyze the incoming message and assign it to one, and only one, of these potential categories: {possible_categories}."
    messages.append(
        {"role": "system", "content": system_message})

    for sample in samples:
        messages += [
            {"role": "user", "content": sample["message"]},
            {"role": "assistant",
                "content": f"{sample['category']}"},
            {"role": "assistant",
                "content": f"Chain of thought: {sample['chain']}"}
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


def generate_response(samples, message, category, urgency):
    sample_messages = [
        sample for sample in samples if sample['category'] == category]

    system_message = f"You're a personal physician whom the patient will consult. Your responsibility is to formulate concise (preferably under 150 characters), compassionate, and medically accurate responses to patient messages in the '{category}' category with a '{urgency}' urgency level, and to direct them to 'my' office offer 'my' help if necessary. Ask follow up questions if not enough information is provided. If the situation is very urgent or requires on-site evaluation, you should ask the patient to come in."

    messages = [{"role": "system", "content": system_message}]

    for sample in sample_messages:
        messages.append({"role": "user", "content": sample['message']})
        messages.append({"role": "assistant", "content": sample['response']})

    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=450
    )

    reply = response['choices'][0]['message']['content']
    print(f"Original generated response: {reply}")

    # samples.append(
    #     {"message": message, "category": category, "response": reply})

    return reply, samples

def generate_validation_responses(validation_set):
    responses = []

    # Create new csv file
    with open('responses.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["message", "category", "urgency", "literacy", "response"])

        for message in validation_set:
            print('here')
            # Step 2: Analyze Literacy Level
            literacy_level = literacy_level_analysis(message['message'])

            # Step 3: Grammar Edit
            message_edited = grammar_edit(message['message'])

            # Step 4: Categorize Input
            category = categorize_input(samples, message_edited)

            # Step 5: Urgency Classification
            urgency = urgency_classification(message_edited)

            # Step 6: Generate Response
            reply, _ = generate_response(samples, message_edited, category, urgency)

            # Step 7: Apply Literacy Level Grammar
            final_message = apply_literacy_level_grammar(reply, literacy_level)

            # Write row to csv file
            writer.writerow([message['message'], category, urgency, literacy_level, final_message])

            responses.append(final_message)

    return responses

message_reader = MessageReader()

# Call catego.py and wait for it to finish
subprocess.call(["python", "./catego.py"])

# Once catego.py is done, read the new csv file
message_reader.read_messages_from_csv('./new_csv.csv')
samples = message_reader.shot
responses = generate_validation_responses(message_reader.validation)

