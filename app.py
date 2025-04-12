# app.py
import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv

# Import agent components from the module
# Make sure langgraph_agent_module.py is in the same directory
from langgraph_agent_module import abot_agent, HumanMessage, db_file

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'a-default-secret-key-change-me')

# --- Helper Function to Get Chat History ---
# (Same as before, needed to display conversation)
def get_chat_history(thread_id: str):
    """Retrieves the full message history for a given thread_id."""
    if not thread_id:
        return []
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = abot_agent.graph.get_state(config)
    # Ensure snapshot and messages exist
    if snapshot and snapshot.values and 'messages' in snapshot.values:
        return snapshot.values.get('messages', [])
    return []

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    # Get or create a unique ID for the conversation thread stored in the user's session
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())
        print(f"New session, thread_id: {session['thread_id']}")

    thread_id = session['thread_id']
    config = {"configurable": {"thread_id": thread_id}}

    if request.method == 'POST':
        user_input = request.form.get('message')
        if user_input:
            print(f"Input for thread {thread_id}: {user_input}")
            # Package the user input as a HumanMessage
            messages = [HumanMessage(content=user_input)]
            try:
                # Run the agent graph. The stream processes messages, calls tools, etc.
                # Persistence (saving state) happens automatically via the checkpointer.
                # We don't need to capture the output here if we reload history below.
                abot_agent.graph.invoke({'messages': messages}, config)
                print(f"Agent invoked for thread {thread_id}")
            except Exception as e:
                print(f"ERROR invoking agent for thread {thread_id}: {e}")
                # You could add an error message to the history here if needed
                # For simplicity, we just print the error server-side.

            # Redirect back to the same page (GET request) to display updated history
            return redirect(url_for('index'))

    # For GET requests (initial load or after POST redirect):
    # Retrieve the current chat history for this user's thread_id
    chat_history = get_chat_history(thread_id)
    print(f"Displaying history for thread {thread_id}, {len(chat_history)} messages")

    # Render the simple HTML template, passing the history
    return render_template('index.html', chat_history=chat_history)

@app.route('/clear')
def clear_session():
    # Remove the thread_id from the session to start a new conversation
    thread_id = session.pop('thread_id', None)
    if thread_id:
         print(f"Cleared session for thread_id: {thread_id}. History remains in DB.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    print(f"Agent checkpointer uses DB: {os.path.abspath(db_file)}")
    # host='0.0.0.0' makes it accessible on your network
    app.run(debug=True, host='0.0.0.0', port=5000)