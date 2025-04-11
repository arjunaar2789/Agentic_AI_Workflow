# langgraph_agent_with_persistence.py
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq.chat_models import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import TypedDict, Annotated
import operator

tool = TavilySearchResults(max_results=5)

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
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        msg = self.model.invoke(messages)
        return {"messages": [msg]}

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

# Initialize the model + persistence
prompt ='''You are an expert research assistant with advanced information retrieval skills. Your primary goal is to provide comprehensive, accurate, and well-structured information through strategic search engine utilization.

When responding to queries:
- Begin by breaking complex questions into smaller, manageable components
- Conduct targeted searches using precise keywords and phrases
- Present information in a clear, organized format (bullet points for key findings, numbered lists for sequential steps)
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

model = ChatGroq(model="llama3-70b-8192")
with SqliteSaver.from_conn_string(':memory:') as memory:
    abot = Agent(model, [tool], system=prompt, checkpointer=memory)
    messages = [HumanMessage(content="What is the weather in Madurai")]
    thread = {'configurable': {'thread_id': '1'}}
    for event in abot.graph.stream({'messages': messages}, thread):
        for v in event.values():
            print(v['messages'][0].content)
    messages=[HumanMessage(content='What about in Chennai?')]
    thread={'configurable':{'thread_id':'1'}}
    for event in abot.graph.stream({'messages': messages}, thread):
        for v in event.values():
            print(v['messages'][0].content)