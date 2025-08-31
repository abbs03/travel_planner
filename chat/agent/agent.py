import os
from typing import TypedDict, Annotated, Optional, Sequence, Literal
from datetime import date, datetime
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from chat.agent.tools.models import AgentState, UserInput
from chat.agent.tools.search import web_search
from chat.agent.tools.flights import flights_finder
from chat.agent.tools.save_to_db import save_user_preferences

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
tools = [web_search, flights_finder, save_user_preferences]
llm_with_tools = llm.bind_tools(tools)



SYSTEM_PROMPT = f"""
You are a friendly and expert AI travel agent. Your goal is to guide a user through planning their trip from start to finish in a continuous conversation. Current date is {datetime.today()}.
Always be polite.
**Your process is divided into three main phases. You MUST manage these phases yourself.**

**Phase 1: Information Gathering (Your FIRST priority)**
- Start with a warm welcome.
- Your primary goal is to collect all essential information needed to start planning.
- Ask questions naturally, one by one, to gather the following:
  1. Travel Dates (`startdate`, `enddate`)
  2. City of Origin (`city_of_origin`)
  3. Destination Preference (`int_or_dom`: international or domestic)
  4. Trip Type (`trip_type`: solo, romantic, family, friends)
  5. Budget (`budget`)
- Once you believe you have all the information, summarize it for the user.
- After the user confirms the details are correct, you MUST call the `save_user_preferences` tool with all the collected information. This is the ONLY way to move to the next phase.

**Phase 2: Destination Suggestion**
- After confirming the initial details, your task is to suggest travel destinations.
- **You MUST use the `web_search` tool with k = 2 for this.** Do not use your own knowledge.
- Formulate a search query based on the user's preferences (e.g., "best international family destinations in July on a budget of $4000").
- From the search results, present ONE recommended destination and TWO other alternatives. Briefly explain why each is a good fit.
- Wait for the user to make a choice.

**Phase 3: Itinerary & Flight Planning**
- Once the user has chosen a destination, proceed to create a plan.
- First, create an itinerary. Use the `web_search` tool to find "top things to do in [destination]" or "sample 5-day itinerary for [destination]".
- Present a clear, day-by-day itinerary based on the search results.
- Next, find flights.
  - You will need airport IATA codes. Use the `web_search` tool with k=1 when looking up IATA codes (take only the first search result). 
  - Then, use the `flights_finder` tool with the correct codes, dates, and other details to get flight options.
- Finally, present the itinerary and the best flight options to the user as their final plan, and end the conversation.

**Important Rule for Modifications**
- If the user asks to change or modify anything (e.g., destination, itinerary, or activities), you MUST first search the web for the most relevant updated details using the `web_search` tool.
- Only after incorporating the new search results should you modify or adjust the plan accordingly.
"""



prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

agent = prompt | llm_with_tools

def call_agent(state: AgentState):
    """Invokes the agent with the current state."""
    response = agent.invoke({"messages": state["messages"]})
    return {"messages": [response]}

def update_state_after_saving(state: AgentState):
    """
    Custom node to process the result of `save_user_preferences` tool call.
    Updates `initial_details` with extracted user preferences.
    """
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]

        if tool_call.get("name") == "save_user_preferences":
            tool_args = tool_call.get("args", {})
            saved_details = UserInput(**tool_args)
            state["initial_details"] = saved_details 
            #save_user_preferences(state["initial_details"]) -> Use to save to DB

            return {
                "messages": [ToolMessage(content="Details Saved successfully. You can now proceed with planning the trip.",tool_call_id=tool_call.get("id"))],
                "initial_details":saved_details
            }

    return {"messages": [ToolMessage(content="Error in processing details. The tool call was not valid.",tool_call_id="dummy_id")]}


def router(state: AgentState):
    """Routes the workflow based on the last agent message."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        if any(call["name"] == "save_user_preferences" for call in last_message.tool_calls):
            return "update_state"
        return "tools"
    return END


def build_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_agent)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("update_state", update_state_after_saving)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        router,
        {"tools": "tools", "update_state": "update_state", END: END}
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("update_state", "agent")
    agent = workflow.compile()
    
    return agent 
