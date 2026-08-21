import os
import requests
from dotenv import load_dotenv
import streamlit as st

# Load API key 
load_dotenv()
api_key = os.getenv("api_key")

def get_laws(jurisdiction, status, keyword):
    """
    Fetch the relevant AI laws based on the jurisdiction, status, and relevant content inputted by the user.
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
        "X-API-Key": api_key
    }

    # Send request
    response = requests.get(url, params=params, headers=headers)

    data = response.json()

    return data

if __name__ == "__main__":
    jurisdiction = input("Jurisdiction:")
    status = input("Status:")
    keyword = input("Key word:")
    laws = get_laws(jurisdiction, status, keyword)
    print(laws)