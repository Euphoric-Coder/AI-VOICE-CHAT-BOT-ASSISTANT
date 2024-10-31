import openai

# Initialize the OpenAI API with your API key
openai.api_key = "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"

from openai import OpenAI

client = OpenAI(
    api_key="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"
)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about recursion in programming."},
    ],
)

print(completion.choices[0].message)
