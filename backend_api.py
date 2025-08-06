from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

# In-memory store to keep track of org_name to org_id
org_store = {}

# Request body model
class OrgRequest(BaseModel):
    org_name: str

@app.post("/get-api-code")
def get_api_code(data: OrgRequest):
    org_name = data.org_name

    # Check if org already exists in store
    if org_name in org_store:
        org_id = org_store[org_name]
    else:
        # Generate a new org_id and store it
        org_id = str(uuid.uuid4())
        org_store[org_name] = org_id

    # Prepare API code snippets
    snippets = {
        "org_id": org_id,
        "create_user_code": f'''
import requests

url = "https://api.spintly.com/createUser"
payload = {{
    "org_id": "{org_id}",
    "user_name": "John Doe",
    "contact_no": "9876543210"
}}
response = requests.post(url, json=payload)
print(response.json())
''',
        "update_user_code": f'''
# Similar update code here using org_id: {org_id}
''',
        "delete_user_code": f'''
# Similar delete code here using org_id: {org_id}
''',
        "get_user_code": f'''
# Similar get user code here using org_id: {org_id}
'''
    }

    return snippets

@app.get("/")
def read_root():
    return {"message": "FastAPI backend is working!"}