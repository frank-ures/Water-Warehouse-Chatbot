import json
import os
import time

#################################
def test_vector_store_api(client):
    """Test if vector store API is available"""
    try:
        # Just try to list vector stores (doesn't create anything)
        stores = client.beta.vector_stores.list()
        print("Vector stores API is available!")
        return True
    except AttributeError as e:
        print(f"Vector stores API not available: {e}")
        return False
    except Exception as e:
        print(f"Other error with vector stores: {e}")
        return True  # API exists but other issue
    ##########################

def create_assistant(client):
###########################
    if not test_vector_store_api(client):
        print("Falling back to file attachment method")
        # Use the older method...
##############################
    assistant_file_path = 'assistant.json'
    
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
            return assistant_id
    
    # Create vector store first
    vector_store = client.beta.vector_stores.create(name="Water Warehouse Knowledge")
    print(f"Created vector store: {vector_store.id}")
    
    # Upload and add file to vector store
    try:
        file = client.files.create(
            file=open("knowledge.txt", "rb"),
            purpose='assistants'
        )
        print(f"Uploaded file: {file.id}")
        
        # Add file to vector store
        vector_store_file = client.beta.vector_stores.files.create(
            vector_store_id=vector_store.id,
            file_id=file.id
        )
        print(f"Added file to vector store")
        
        # Wait for file to be processed
        print("Waiting for file processing...")
        max_wait = 60  # 60 seconds max
        wait_time = 0
        
        while wait_time < max_wait:
            vector_store_file = client.beta.vector_stores.files.retrieve(
                vector_store_id=vector_store.id,
                file_id=file.id
            )
            
            if vector_store_file.status == 'completed':
                print("File processing completed!")
                break
            elif vector_store_file.status == 'failed':
                print(f"File processing failed: {vector_store_file}")
                raise Exception("File processing failed")
            
            time.sleep(2)
            wait_time += 2
        
        if wait_time >= max_wait:
            raise Exception("File processing timeout")
            
    except Exception as e:
        print(f"Error with vector store setup: {e}")
        # Create assistant without file search if upload fails
        assistant = client.beta.assistants.create(
            instructions="""
            You are the Water Warehouse Customer Support Assistant.
            Help customers with questions about water filtration systems, alkaline water, and related products.
            Keep responses short and helpful.
            """,
            model="gpt-4-1106-preview",
            tools=[]
        )
        print(f"Created assistant without vector store: {assistant.id}")
        
        with open(assistant_file_path, 'w') as file_obj:
            json.dump({'assistant_id': assistant.id}, file_obj)
        
        return assistant.id
    
    # Create assistant with vector store
    assistant = client.beta.assistants.create(
        instructions="""
        You are the Water Warehouse Customer Support Assistant.
        Use the provided knowledge base to answer questions about products, pricing, and services.
        Keep responses short with only necessary information.
        """,
        model="gpt-4-1106-preview",
        tools=[{"type": "file_search"}],
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        }
    )
    
    print(f"Created assistant with vector store: {assistant.id}")
    
    # Save assistant info
    with open(assistant_file_path, 'w') as file_obj:
        json.dump({
            'assistant_id': assistant.id,
            'vector_store_id': vector_store.id
        }, file_obj)
    
    return assistant.id

def upload_knowledge_file(client):
    """This is now handled in create_assistant"""
    return None

def create_message_with_file(client, thread_id, user_input, file_id):
    """Not needed with vector store setup"""
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


'''works without knowledge.txt
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
        '''



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