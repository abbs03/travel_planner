from agent import build_agent
from tools.models import AgentState
from langchain_core.messages import HumanMessage, AIMessage


if __name__ == "__main__":
    travel_agent = build_agent()

        
    state = AgentState(messages=[], initial_details=None)

    welcome_message = "Bot: Hello! I'm excited to help you plan your next trip"
    print(welcome_message)
    state['messages'].append(AIMessage(content=welcome_message))

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Bot: Goodbye! Have a great day.")
            break

        state["messages"].append(HumanMessage(content=user_input))
        state = travel_agent.invoke(state)
        print("Bot:", state["messages"][-1].content)