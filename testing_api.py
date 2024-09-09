from openai import OpenAI

# init client and connect to localhost server
client = OpenAI(
    api_key="<generated_api_key>",
    base_url="https://3511-82-713-192-232.ngrok-free.app/" # ngrok prublic URL / Localhost IP:PORT
)

# call API
chat_completion = client.chat.completions.create(
    messages=[
            {"role": "system", "content": "You are a python coder!"},
            {"role": "user", "content": "Write a timer decorator."}
    ],
)

# print the top "choice"
print(chat_completion.choices[0].message.content)
