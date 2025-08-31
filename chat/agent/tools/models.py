from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Literal, Optional
from langgraph.graph.message import add_messages
from datetime import date



class UserInput(BaseModel):
    """Initial user travel preferences."""
    startdate: Optional[date] = Field(description="The user stated Start date of the travel in yyyy-mm-dd format")
    enddate: Optional[date] = Field(description="The user stated End date of the travel in yyyy-mm-dd format")
    city_of_origin: Optional[str] = Field(description="City the user currently resides in", examples=['Chennai', 'Banglore'])
    int_or_dom: Optional[Literal["international", "domestic", "open"]] = Field(description="Choice of destination type of the user")
    trip_type: Optional[str] = Field(description="Type of Travel based on travel group", examples=['Family trip', 'romantic trip', 'solo trip', 'friends trip'])
    currency: Optional[str] = Field(description="Home currency of user from city of origin", default='USD')
    budget: Optional[int] = Field(description="Max Budget that can be spent")


class FlightInput(BaseModel):
    """Input for the flight search tool."""
    departure_id: str = Field(description='Departure airport IATA code')
    arrival_id: str = Field(description='Arrival airport IATA code')
    outbound_date: str = Field(description='Outbound date in YYYY-MM-DD format', examples=["2024-06-22"])
    return_date: str = Field(description='Return date in YYYY-MM-DD format.', examples=["2024-06-28"])
    adults: int = Field(1, description='Number of adults. Defaults to 1.')
    currency: str = Field(description="Local currency of the user")



class AgentState(TypedDict):
    """Agent state"""
    messages: Annotated[list, add_messages]
    initial_details: Optional[UserInput]
    chosen_destination: Optional[str]