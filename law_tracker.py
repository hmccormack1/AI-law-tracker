import os
import requests

from typing import List
from dotenv import load_dotenv


# Load API key
load_dotenv()
LAW_AI_TRACKER_API_KEY = os.getenv("LAW_AI_TRACKER_API_KEY")


def get_laws(jurisdiction: List[str], status: str, keyword: str, limit: int = 25, offset: int = 0):
    """
    Fetch the relevant AI laws based on the jurisdiction, status, and relevant content inputted by the user.
    Limit and offset control the chunk of data that is being fetched.

    Returns the parsed API response as a dict if the call succeeds, or None
    if something went wrong (bad API key, bad filters, network issue, etc).
    """

    # API endpoint URL
    url = "https://ai-law-tracker.com/api/v1/laws"

    # Query parameters
    params = {
        "jurisdiction": jurisdiction,
        "status": status,
        "q": keyword,
        "limit": limit,
        "offset": offset
    }

    headers = {
        "X-API-Key": LAW_AI_TRACKER_API_KEY
    }

    # Send request
    response = requests.get(url, params=params, headers=headers)

    # If the call didn't succeed (bad key, bad filters, rate limit, etc.),
    # stop here instead of trying to use a response that isn't real data.
    if response.status_code != 200:
        return None

    data = response.json()

    return data
