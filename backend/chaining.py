import openai
import pandas as pd
import os

openai.api_key = os.getenv("API_KEY")

df = pd.read_csv('./message_list.csv')

def generate_chain(message, category):
    system_message = f"""As demonstrated by Wei et al. (2022), the chain-of-thought (CoT) approach enables complex reasoning capabilities through intermediate reasoning steps:

    "Prompt:

    The odd numbers in this group add up to an even number: 4, 8, 9, 15, 12, 2, 1.
    A: Adding all the odd numbers (9, 15, 1) gives 25. The answer is False.
    The odd numbers in this group add up to an even number: 17,  10, 19, 4, 8, 12, 24.
    A: Adding all the odd numbers (17, 19) gives 36. The answer is True.
    The odd numbers in this group add up to an even number: 16,  11, 14, 4, 8, 13, 24.
    A: Adding all the odd numbers (11, 13) gives 24. The answer is True.
    The odd numbers in this group add up to an even number: 17,  9, 10, 12, 13, 4, 2.
    A: Adding all the odd numbers (17, 9, 13) gives 39. The answer is False.
    The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1. 
    A:

    Output: Adding all the odd numbers (15, 5, 13, 7, 1) gives 41. The answer is False." 

    So, apply this CoT approach to the following patient's message: '{message}', categorized as: '{category}'. Explain how this category was derived from the patient's message by outlining the reasoning steps in two sentences and limit it to (150 characters)."""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_message}],
        temperature=0.1,
        max_tokens=300
    )

    chain_of_thought = response['choices'][0]['message']['content'].strip()

    return chain_of_thought

df['Chain'] = df.apply(lambda row: generate_chain(row['Message'], row['Category']), axis=1)

df.to_csv('chaining_list.csv', index=False)
