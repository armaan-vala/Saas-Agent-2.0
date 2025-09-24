import os
from groq import Groq
from dotenv import load_dotenv

# Load the .env file to get the API key
load_dotenv()

try:
    # Initialize the Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    print("Fetching available models from Groq...")

    # Get the list of models
    models_list = client.models.list()

    print("-" * 30)
    print("Available Models:")
    # Loop through the response and print the ID of each model
    for model in models_list.data:
        print(model.id)
    print("-" * 30)

except Exception as e:
    print(f"An error occurred: {e}")