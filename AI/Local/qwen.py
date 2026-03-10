from langchain_ollama.chat_models import ChatOllama

model = ChatOllama(
    model="qwen3.5:0.8b",
    reasoning=True,
)
def chat():
 for chat in model.stream(" write a py code to print hello world form ml model !  "):
    try:
     reasoning =chat.additional_kwargs['reasoning_content']
    except:
     reasoning=None

    if reasoning:
        yield ("Reasoning",reasoning)
    content = chat.content
    yield ("Answer",content) 

for type,text in chat():
   if type == "Reasoning":
    print(f"\033[90m{text}\033[0m", end="") 

   print(text,end="",flush=True)