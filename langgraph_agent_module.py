# langgraph_agent_module.py
import os
import operator
import sqlite3 # Required for explicit connection
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage, HumanMessage, AIMessage
from langchain_groq.chat_models import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables
load_dotenv()

# --- Agent Definition ---
tool = TavilySearchResults(max_results=3) 
tools = [tool]

prompt ='''You are an expert research assistant with advanced information retrieval skills. Your primary goal is to provide comprehensive, accurate, and well-structured information through strategic search engine utilization.

When responding to queries:
- Begin by breaking complex questions into smaller, manageable components
- Conduct targeted searches using precise keywords and phrases
- Include relevant statistics, examples, and authoritative sources to support your answers
- Maintain a professional yet conversational tone throughout your responses
- Specify the reliability and recency of information when possible

DO:
- Use multiple search queries when a topic requires exploring different angles
- Indicate when information might be incomplete or when multiple perspectives exist
- Provide contextual background before diving into technical details
- Synthesize information from multiple sources into coherent insights
- Ask clarifying questions when the initial query is ambiguous

DON'T:
- Make unsupported claims or present opinions as facts
- Conduct unnecessary searches when you already have sufficient information
- Rush to conclusions before gathering comprehensive data

When handling multi-step research tasks, outline your approach before proceeding, explaining which aspects you'll investigate first and why. If the initial search doesn't yield satisfactory results, refine your search strategy and explain your reasoning.

Structure your final responses with clear headings, concise summaries, and detailed explanations appropriate to the complexity of the question.'''

model = ChatGroq(model="llama3-70b-8192").bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self, model, tools, checkpointer, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_model)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges("llm", self.has_action, {True: "action", False: END})
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def has_action(self, state: AgentState):
        return len(state["messages"][-1].tool_calls) > 0

    def call_model(self, state: AgentState):
        messages = state["messages"]

        print(f"DEBUG: Calling model with: {messages}")
        response = None  # Initialize response
        try:
            # Invoke the model
            response = self.model.invoke(messages)
            print(f"DEBUG: Raw model response object: {response}")  # Log the raw response
            if isinstance(response, str):
                print(f"DEBUG: Model returned a string, wrapping in AIMessage.")
                response = AIMessage(content=response)
            elif not hasattr(response, 'type'):  # Basic check for BaseMessage structure
                print(f"WARNING: Unexpected response type from model: {type(response)}. Wrapping in AIMessage.")
                response = AIMessage(content=str(response))
            # --- END CHECK ---

        except Exception as e:
            print(f"ERROR: Model invocation failed: {e}")
            response = AIMessage(content=f"Sorry, I encountered an error processing that: {e}")

        messages_to_return = []
        if response:
            messages_to_return = [response]
        else:
            print("ERROR: No response generated in call_model!")
            messages_to_return = [AIMessage(content="Error: Could not generate response.")]

        print(f"DEBUG: call_model returning: {messages_to_return}")

        return {"messages": messages_to_return}

    def take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for t in tool_calls:
            if t["name"] not in self.tools:
                result = "Invalid tool"
            else:
                result = self.tools[t["name"]].invoke(t["args"])
            results.append(ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result)))
        return {"messages": results}

db_file = "agent_memory.sqlite"

conn = sqlite3.connect(db_file, check_same_thread=False)

# Instantiate SqliteSaver directly using the connection
memory = SqliteSaver(conn=conn)

abot_agent = Agent(model, tools, system=prompt, checkpointer=memory) # Pass tools list here

def close_db_connection():
    print("Closing database connection.")
    if conn:
        conn.close()
