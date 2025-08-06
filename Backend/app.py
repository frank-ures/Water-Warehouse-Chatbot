import os
from time import sleep
from packaging import version
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
import functions
from dotenv import load_dotenv

load_dotenv()
from flask_cors import CORS

# Version check
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

if current_version < required_version:
    raise ValueError("Error: OpenAI version is less than required")
else:
    print("OpenAI version is compatible")

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=OPENAI_API_KEY)
assistant_id = functions.create_assistant(client)

# Upload knowledge file once at startup
knowledge_file_id = functions.upload_knowledge_file(client)
print(f"Application started with assistant ID: {assistant_id}")
if knowledge_file_id:
    print(f"Knowledge file loaded: {knowledge_file_id}")

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "message": "Water Warehouse Chatbot API is running",
        "assistant_id": assistant_id,
        "knowledge_file": knowledge_file_id is not None
    })

@app.route('/start', methods=['GET'])
def start_conversation():
    print("Starting a new conversation...")
    try:
        thread = client.beta.threads.create()
        print(f"New thread created with ID: {thread.id}")
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        print(f"Error creating thread: {e}")
        return jsonify({"error": "Failed to create conversation"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')
    
    if not thread_id:
        print("Error: Missing thread_id")
        return jsonify({"error": "Missing thread_id"}), 400
    
    if not user_input:
        return jsonify({"error": "Missing message"}), 400
    
    print(f"Received message: {user_input} for thread ID: {thread_id}")
    
    try:
        # Check if this is the first message in the thread
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        is_first_message = len(messages.data) == 0
        
        if is_first_message and knowledge_file_id:
            # Create message with file attachment for first message
            message = functions.create_message_with_file(client, thread_id, user_input, knowledge_file_id)
        else:
            # Create regular message
            message = functions.create_regular_message(client, thread_id, user_input)
        
        if not message:
            return jsonify({"error": "Failed to create message"}), 500
        
        # Create and run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Wait for completion with timeout
        max_wait_time = 60  # 30 seconds timeout
        wait_time = 0
        
        while wait_time < max_wait_time:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            print(f"Run status: {run_status.status}")
            
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                print(f"Run failed: {run_status.last_error}")
                return jsonify({"error": "Assistant run failed"}), 500
            elif run_status.status == 'cancelled':
                print("Run was cancelled")
                return jsonify({"error": "Assistant run was cancelled"}), 500
            
            sleep(1)
            wait_time += 1
        
        if wait_time >= max_wait_time:
            print("Run timed out")
            return jsonify({"error": "Assistant response timed out"}), 500
        
        # Get the assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = None
        
        for message in messages.data:
            if message.role == "assistant":
                response = message.content[0].text.value
                break
        
        if response is None:
            response = "Sorry, I couldn't find a reply."
        
        print(f"Assistant response: {response}")
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'

    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
