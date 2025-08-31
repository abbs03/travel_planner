from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Literal, Optional
from langgraph.graph.message import add_messages
from datetime import date
from .models import UserInput
from langchain_core.tools import tool

@tool(args_schema=UserInput)
def save_user_preferences(  startdate: Optional[date] = None,
    enddate: Optional[date] = None,
    city_of_origin: Optional[str] = None,
    int_or_dom: Optional[Literal["international", "domestic", "open"]] = None,
    trip_type: Optional[str] = None,
    currency: Optional[str] = "USD",
    budget: Optional[int] = None) -> str:
    """
    Use this tool to save the user's confirmed travel preferences.
    This action finalizes the information-gathering phase and allows the agent
    to proceed with destination suggestions and planning.
    """
    details = UserInput(
        startdate=startdate,
        enddate=enddate,
        city_of_origin=city_of_origin,
        int_or_dom=int_or_dom,
        trip_type=trip_type,
        currency=currency,
        budget=budget,
    )
    # Ideally Should be used to save in database
    #print(f"--- Preferences saved: {details.model_dump_json(indent=2)} ---")
    return "Successfully saved user preferences. You can now proceed with planning the trip."
