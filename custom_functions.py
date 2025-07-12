import json
import requests
import os
from openai import OpenAI
from assistant_instructions import assistant_instructions
from dotenv import load_dotenv, dotenv_values

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

# Init OpenAI Client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Add lead to Airtable
def create_lead(name="", company_name="", phone="", email=""):
  url = "https://api.airtable.com/v0/appRw37HqO4ENk5jn/Leads"
  headers = {
      "Authorization" : 'Bearer ' + dotenv_values().get('AIRTABLE_API_KEY'),
      "Content-Type": "application/json"
  }
  data = {
      "records": [{
          "fields": {
              "Name": name,
              "Phone": phone,
              "Email": email,
              "CompanyName": company_name,
          }
      }]
  }
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200:
    print("Lead created successfully.")
    return response.json()
  else:
    print(f"Failed to create lead: {response.text}")

# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # If no assistant.json is present, create a new assistant using the below specifications

    # To change the knowledge document, modifiy the file name below to match your document
    # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
    file = client.files.create(file=open("knowledge.docx", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(
        # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
        instructions=assistant_instructions,
        model="gpt-4o",
        tools=[
            {
                "type": "file_search"  # This adds the knowledge base as a tool
            },
            {
                "type": "function",  # This adds the lead capture as a tool
                "function": {
                    "name": "create_lead",
                    "description":
                    "Capture lead details and save to Airtable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the lead."
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the lead."
                            },
                            "email": {
                                "type": "string",
                                "description": "Email of the lead."
                            },
                            "company_name": {
                                "type": "string",
                                "description": "CompanyName of the lead."
                            }
                        },
                        "required": ["name", "email", "company_name"]
                    }
                }
            }
        ],
        tool_resources={
            "file_search": {
                "vector_store_ids": []
            }
        })

    # Create a vector store and add the file to it
    vector_store = client.vector_stores.create(
        name="Knowledge Base",
        file_ids=[file.id]
    )

    # Update the assistant to use the vector store
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        }
    )

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id