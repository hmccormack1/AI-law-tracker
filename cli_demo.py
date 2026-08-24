"""
This file supports using the API through the command-line interface.
It is intended to enhance CLI support by performing slight parsing on
user input in the event that they enter values not acceptable for the
API call. 
"""

from law_tracker import get_laws


def format_jurisdiction(jurisdiction):
    """
    Convert a state name into the format expected by the API.
    For example, if the user inputs "North Carolina" this will
    get converted to north-carolina. Federal is the only special
    case which must get converted to us-federal.
    """

    #Make user input lowercase
    jurisdiction = jurisdiction.lower()

    if jurisdiction == "federal":
        return "us-federal"

    return jurisdiction.replace(" ", "-")


def choose_status():
    """
    Display status choices and return the selected API search value.
    """

    status_options = {
        "1": "",
        "2": "In Effect",
        "3": "Enacted",
        "4": "Proposed",
        "5": "Study phase",
        "6": "No state law",
    }

    print("\nChoose a law status:")
    print("1. Any status")
    print("2. In Effect")
    print("3. Enacted")
    print("4. Proposed")
    print("5. Study phase")
    print("6. No state law")

    choice = input("Enter a number from 1 to 6: ")

    return status_options.get(choice, "")


def main():
    print("AI Law Tracker CLI Demo")
    print("Search for laws related to artificial intelligence in a U.S. state or at the federal level.")

    jurisdiction_input = input("\nEnter the full name of a U.S. state, such as 'North Carolina', or enter 'Federal': ")
    jurisdiction = format_jurisdiction(jurisdiction_input)
    status = choose_status()

    print( "\nYou can optionally search for laws about a particular topic.")
    print("Examples include facial recognition, healthcare, employment, deepfakes, or data privacy.")
    print("Press Enter without typing anything if you want to include all topics.")

    keyword = input("Enter a topic or phrase: ")
    print("\nSearching for matching AI laws...\n")

    result = get_laws(jurisdiction=jurisdiction, status=status, keyword=keyword)

    if result is None:
        print("Something went wrong while fetching laws.")
        return

    laws = result["data"]

    if not laws:
        print("No matching laws were found.")
        print("Try choosing a different status or leaving the topic blank.")
        return

    print(f"Found {result['meta']['total']} matching law(s):\n")

    for law in laws:
        print(f"{law['identifier']}: {law['title']}")
        print(f"Jurisdiction: {law['jurisdiction']['name']}")
        print(f"Status: {law['status']}")
        print(f"Source: {law['official_url']}")
        print()


if __name__ == "__main__":
    main()