import openai

openai.api_key = "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"

MODEL = "gpt-3.5-turbo"


def foo(message):
    # changing the cutoff date
    system_message = """
    You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4.0 architecture.
    Knowledge cutoff: 2023-05
    Current date: 2023-07-11
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
    response = response['choices'][0]['message']['content'].strip().lower()
    return response


response = print(foo("who's twitter's ceo"))
