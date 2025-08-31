import os
from typing import Optional

import serpapi
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from .models import FlightInput


@tool(args_schema=FlightInput)
def flights_finder(params: dict) -> dict:
    '''
    Finds flights using the Google Flights engine via the SerpApi service.
    Requires departure/arrival airport codes, dates, and other details.
    '''
    api_params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_flights',
        'hl': 'en',
        'gl': 'us', 
        'departure_id': params.departure_id,
        'arrival_id': params.arrival_id,
        'outbound_date': params.outbound_date,
        'return_date': params.return_date,
        'currency': params.currency,
        'adults': params.adults,
    }
    try:
        from serpapi import GoogleSearch
        search = GoogleSearch(api_params)
        results = search.get_dict()
        return results.get('best_flights', 'No flights found.')
    except Exception as e:
        return {"error": str(e)}
