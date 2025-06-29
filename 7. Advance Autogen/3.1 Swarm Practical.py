import asyncio
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.teams import Swarm
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination,HandoffTermination
from dotenv import load_dotenv
import os
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import HandoffMessage


# Load API key
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Model client
model_client = OpenAIChatCompletionClient(model='gpt-4o', api_key=api_key)


def refund_flight (flight_id:str)->str:
    """
    Refund a flight ticket.
    """
    return f"Flight {flight_id} has been refunded."

# Termination condition
termination_condition = HandoffTermination(target='user') | TextMentionTermination("TERMINATE")

# Agent 1
travel_agent= AssistantAgent(
    name="travel_agent",
    model_client=model_client,
    handoffs=['flight_refunder','user'],
    system_message='''You are a travel agent. THe flight_refunder is in charge of refunding flights.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is done'''
)

# Agent 2
flight_refunder= AssistantAgent(
    name="flight_refunder",
    model_client=model_client,
    handoffs=['travel_agent','user'],
    tools=[refund_flight],
    system_message='''You are an agent that specialized in refunding flights.
    You only need flight PNR number to refund a flight
    You have the ability to refund the flight using the refund_flight tool.
    If you need information from the user,you must first send your message, then you can handoff to the user.
    when the transaction is complete, handoff to the travel agent to finalize. '''
)

team = Swarm(participants=[travel_agent, flight_refunder],termination_condition=termination_condition)


task = 'Can you help me with the refund of my flight?'




async def run_team_stream()->None:
    task_result = await Console(team.run_stream(task=task))

    last_message = task_result.messages[-1]
    print("Last Message is ---->",last_message)

    while isinstance(last_message,HandoffMessage) and last_message.target == 'user':
        print(last_message.type)
        print("Last Message is ---->",last_message)
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source='user',target=last_message.source,content=user_message))
        )
        last_message = task_result.messages[-1]

if __name__ == "__main__":
    asyncio.run(run_team_stream())
