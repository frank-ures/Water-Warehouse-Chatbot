import json
import os

def create_assistant(client):
    assistant_file_path = 'assistant.json'
    
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Create the assistant WITHOUT file_search tools initially
        assistant = client.beta.assistants.create(
            instructions="""
            The assistant, Water Warehouse Customer Support Assistant, has been
            programmed to provide potential customers with basic information on the business's offering.
            Keep responses short with only necessary information.
            You are knowledgeable about water filtration systems, alkaline water, and related products.
            """,
            model="gpt-4-1106-preview",
            tools=[]  # No tools for now to avoid vector store issues
        )
        print(f"Created assistant ID: {assistant.id}")
        
        # Save the assistant ID
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")
        assistant_id = assistant.id
    
    return assistant_id

def upload_knowledge_file(client):
    """For now, return None to disable file upload"""
    print("Knowledge file upload disabled temporarily to avoid vector store issues")
    return None

def create_message_with_file(client, thread_id, user_input, file_id):
    """Create message with file attachment - fallback to regular message"""
    print("File attachment disabled, creating regular message instead")
    return create_regular_message(client, thread_id, user_input)

def create_regular_message(client, thread_id, user_input):
    """Create regular message without file attachment"""
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        return message
    except Exception as e:
        print(f"Error creating regular message: {e}")
        return None



'''almost worked
import json
import os

def create_assistant(client):
    assistant_file_path = 'assistant.json'
    
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Create the assistant
        assistant = client.beta.assistants.create(
            instructions="""
            The assistant, Water Warehouse Customer Support Assistant, has been
            programmed to provide potential customers with basic information on the business's offering.
            Keep responses short with only necessary information.
            A document has been provided with information on Water Warehouse's offering and pricing.
            """,
            model="gpt-4-1106-preview",
            tools=[
                {
                    "type": "file_search"
                }
            ]
        )
        print(f"Created assistant ID: {assistant.id}")
        
        # Save the assistant ID
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")
        
        assistant_id = assistant.id
    
    return assistant_id

def upload_knowledge_file(client):
    """Upload knowledge file once and return file ID"""
    knowledge_file_path = 'knowledge_file.json'
    
    # Check if we already have a file ID stored
    if os.path.exists(knowledge_file_path):
        with open(knowledge_file_path, 'r') as file:
            file_data = json.load(file)
            file_id = file_data['file_id']
            print(f"Using existing knowledge file ID: {file_id}")
            return file_id
    
    # Upload the knowledge file
    try:
        file = client.files.create(
            file=open("knowledge.txt", "rb"),
            purpose='assistants'
        )
        print(f"Uploaded knowledge file ID: {file.id}")
        
        # Save the file ID
        with open(knowledge_file_path, 'w') as file_obj:
            json.dump({'file_id': file.id}, file_obj)
        
        return file.id
    except Exception as e:
        print(f"Error uploading knowledge file: {e}")
        return None

def create_message_with_file(client, thread_id, user_input, file_id):
    """Create message with file attachment"""
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
            attachments=[
                {
                    "file_id": file_id,
                    "tools": [{"type": "file_search"}]
                }
            ]
        )
        return message
    except Exception as e:
        print(f"Error creating message with file: {e}")
        return None

def create_regular_message(client, thread_id, user_input):
    """Create regular message without file attachment"""
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        return message
    except Exception as e:
        print(f"Error creating regular message: {e}")
        return None
        '''






'''
import json
import os

def create_assistant(client):
    assistant_file_path = 'assistant.json'
    
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Create the assistant
        assistant = client.beta.assistants.create(
            instructions="""
            The assistant, Water Warehouse Customer Support Assistant, has been
            programmed to provide potential customers with basic information on the business's offering.
            Keep responses short with only necessary information.
            A document has been provided with information on Water Warehouse's offering and pricing.
            """,
            model="gpt-4-1106-preview",
            tools=[
                {
                    "type": "file_search"
                }
            ]
        )
        print(f"Created assistant ID: {assistant.id}")
        
        # Save the assistant ID
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")
        
        assistant_id = assistant.id
    
    return assistant_id

def upload_knowledge_file(client):
    """Upload knowledge file once and return file ID"""
    knowledge_file_path = 'knowledge_file.json'
    
    # Check if we already have a file ID stored
    if os.path.exists(knowledge_file_path):
        with open(knowledge_file_path, 'r') as file:
            file_data = json.load(file)
            file_id = file_data['file_id']
            print(f"Using existing knowledge file ID: {file_id}")
            return file_id
    
    # Upload the knowledge file
    try:
        file = client.files.create(
            file=open("knowledge.txt", "rb"),
            purpose='assistants'
        )
        print(f"Uploaded knowledge file ID: {file.id}")
        
        # Save the file ID
        with open(knowledge_file_path, 'w') as file_obj:
            json.dump({'file_id': file.id}, file_obj)
        
        return file.id
    except Exception as e:
        print(f"Error uploading knowledge file: {e}")
        return None
    
def create_message_with_file(client, thread_id, user_input, file_id):
    """Create message with file attachment"""   
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
            attachments=[
                {
                    "file_id": file_id,
                    "tools": [{"type": "file_search"}]
                }
            ]
        )
        return message
    except Exception as e:
        print(f"Error creating message with file: {e}")
        return None

def create_regular_message(client, thread_id, user_input):
    """Create regular message without file attachment"""
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        return message
    except Exception as e:
        print(f"Error creating regular message: {e}")
        return None
        '''




'''
def create_assistant(client):
    assistant_file_path = 'assistant.json'
    
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Create the assistant
        assistant = client.beta.assistants.create(
            instructions="""
            The assistant, Water Warehouse Customer Support Assistant, has been
            programmed to provide potential customers with basic information on the business's offering.
            Keep responses short with only necessary information.
            A document has been provided with information on Water Warehouse's offering and pricing.
            """,
            model="gpt-4-1106-preview",
            tools=[
                {
                    "type": "file_search"
                }
            ]
        )
        print(f"Created assistant ID: {assistant.id}")
        
        # Save the assistant ID
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")
        
        assistant_id = assistant.id
    
    return assistant_id
    

def upload_knowledge_file(client):
    """Upload knowledge file once and return file ID"""
    knowledge_file_path = 'knowledge_file.json'
    
    # Check if we already have a file ID stored
    if os.path.exists(knowledge_file_path):
        with open(knowledge_file_path, 'r') as file:
            file_data = json.load(file)
            file_id = file_data['file_id']
            print(f"Using existing knowledge file ID: {file_id}")
            return file_id
    
    # Upload the knowledge file
    try:
        file = client.files.create(
            file=open("knowledge.txt", "rb"),
            purpose='assistants'
        )
        print(f"Uploaded knowledge file ID: {file.id}")
        
        # Save the file ID
        with open(knowledge_file_path, 'w') as file_obj:
            json.dump({'file_id': file.id}, file_obj)
        
        return file.id
    except Exception as e:
        print(f"Error uploading knowledge file: {e}")
        return None


def create_message_with_file(client, thread_id, user_input, file_id):
    """Create message with file attachment"""   
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
            attachments=[
                {
                    "file_id": file_id,
                    "tools": [{"type": "file_search"}]
                }
            ]
        )
        return message
    except Exception as e:
        print(f"Error creating message with file: {e}")
        return None

def create_regular_message(client, thread_id, user_input):
    """Create regular message without file attachment"""
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        return message
    except Exception as e:
        print(f"Error creating regular message: {e}")
        return None
'''