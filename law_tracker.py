import os
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_laws(jurisdiction, status, keyword):
    """
    Fetch the relevant AI laws based on the jurisdiction, status, and relevant content inputted by the user.

    Returns the parsed API response as a dict if the call succeeds, or None
    if something went wrong (bad API key, bad filters, network issue, etc).
    """

    # API endpoint URL
    url = "https://ai-law-tracker.com/api/v1/laws"

    # Query parameters
    params = {
        "jurisdiction": jurisdiction,
        "status": status,
        "q": keyword
    }

    headers = {
        "X-API-Key": API_KEY
    }

    # Send request
    response = requests.get(url, params=params, headers=headers)

    # If the call didn't succeed (bad key, bad filters, rate limit, etc.),
    # stop here instead of trying to use a response that isn't real data.
    if response.status_code != 200:
        return None

    data = response.json()

    return data

if __name__ == "__main__":
    jurisdiction = input("Jurisdiction:")
    status = input("Status:")
    keyword = input("Key word:")
    laws = get_laws(jurisdiction, status, keyword)

    if laws is None:
        print("Something went wrong fetching laws. Check your API key and filters.")
    else:
        print(laws)