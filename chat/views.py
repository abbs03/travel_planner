from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from chat.agent.agent import build_agent
from chat.agent.tools.models import AgentState
from langchain_core.messages import HumanMessage, AIMessage


travel_agent = build_agent()
state = AgentState(messages=[], initial_details=None)

@csrf_exempt
def chat_api(request):
    global state
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("message")

        state["messages"].append(HumanMessage(content=user_input))
        state = travel_agent.invoke(state)
        bot_reply = state["messages"][-1].content

        return JsonResponse({"reply": bot_reply})
    



@csrf_exempt
def new_chat(request):
    global state
    state = AgentState(messages=[], initial_details=None)
    return redirect("index") 



def home(request):
    return render(request, "home.html")

def index(request):
    return render(request, "index.html")
