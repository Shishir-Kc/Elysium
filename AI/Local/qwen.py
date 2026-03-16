from pickle import TRUE
from langchain_ollama.chat_models import ChatOllama

model = ChatOllama(
    model="qwen3.5:0.8b",
    reasoning=False,
)


def chat(msg: str):
    for chat in model.stream(msg):
        try:
            reasoning = chat.additional_kwargs["reasoning_content"]
        except:
            reasoning = None

        if reasoning:
            yield ("Reasoning", reasoning)
        content = chat.content
        yield ("Answer", content)


while True:
    for type, text in chat(msg=input(":>")):
        if type == "Reasoning":
            print(f"{text}", end="")

        print(text, end="", flush=True)

# while True:
#     chat(msg=input(":>"))
