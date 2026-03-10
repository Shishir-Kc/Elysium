from langchain_groq.chat_models import ChatGroq
from langchain.agents import create_agent 
from Elysium_Config.Ai.config_groq import GROQ_API
from langchain_core.prompts import PromptTemplate
from AI.Tools.email import send_email
from langchain.tools import tool

@tool
def turn_light_on_off(state:bool):
    """
        AGRS;

            state : True equals light on Fasle equals light off

    
    """
    print(state)
    return{"light_is":state}

class Agent:
    def __init__(self):
        self.model = ChatGroq(
            api_key=GROQ_API,
            model='openai/gpt-oss-120b',
            streaming=True
        )
        self.system_prompt=f"you are an ai named Elysium shorter name is EL you must answer user querry using provided tools ! you are an Home Server/ Home AI Made by Shishir khatri" 
        self.agent =create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=[send_email,turn_light_on_off]
            )


        
    async def chat(self,user_message):
        response =  ''
        try:
            response = await  self.agent.ainvoke({
                'messages':user_message
            })

        except Exception as e:
            print(f"Somthing went Wrong! => {e}")

        print(f" Reasoning - > {response['messages'][1].additional_kwargs['reasoning_content']}")
        # print(f" Response -> {response['messages'][1].content}")
        # print(response)
        response =response['messages'][-1].content

        return response
