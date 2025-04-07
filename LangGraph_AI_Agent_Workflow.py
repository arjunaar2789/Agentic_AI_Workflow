from dotenv import load_dotenv
_=load_dotenv()
from langgraph.graph import StateGraph,END
import operator
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage,SystemMessage,HumanMessage,ToolMessage
from langchain_groq.chat_models import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
tool=TavilySearchResults(max_results=5,depth='advanced')

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage],operator.add] # this is a langchain state which adds any message by the help of operator module

class Agent:

    def __init__(self,model,tools,system=''):
        self.system=system #initializing the system by matching it to the attribute
        graph=StateGraph(AgentState) #defining the state graph
        graph.add_node('llm',self.call_groq) #adding the node for LLM
        graph.add_node('action',self.take_action) #adding the node for action
        graph.add_conditional_edges(
            'llm',
            self.exists_action,
            {True:'action',False:END}
        ) #a conditional edge which is the place where a decision is made to take action or proceed to end
        graph.add_edge('action','llm') #adding an edge between the action and to llm if any action is to be taken
        graph.set_entry_point('llm') #the initialisation for the the stategraph which starts with the llm
        self.graph=graph.compile() #compiling the graph
        self.tools={t.name: t for t in tools} #defining the tools
        self.model=model.bind_tools(tools) #creating the model by combining with the tools

    def exists_action(self,state:AgentState): #defining a function to check the presence of action
        result=state['messages'][-1] #gets the last message in the list
        return len(result.tool_calls)>0 #if there is any tool then it returns True and goes into the action loop

    def call_groq(self,state:AgentState):
        messages=state['messages'] #this defines the messages in the list
        if self.system:
            messages=[SystemMessage(content=self.system)]+messages
        message=self.model.invoke(messages) #invoking the model with the messages
        return {'messages':[message]}

    def take_action(self,state:AgentState):
        tool_calls=state['messages'][-1].tool_calls #getting the last tool name in the list
        results=[]
        for t in tool_calls:
            print(f'Calling: {t}')
            if not t['name'] in self.tools:  #checking for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                result=self.tools[t['name']].invoke(t['args']) #if the tool is there then we invoke it
            results.append(ToolMessage(tool_call_id=t['id'],name=t['name'],content=str(result))) #appending the result that we get from calling the tool
        print('Back to model!')
        return {'messages':results} #mapping the result to the messages in dictionary format

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

model=ChatGroq(model='llama-3.3-70b-versatile')
abot=Agent(model,[tool],system=prompt)
messages = [HumanMessage(content="Can you list the number of states in India with it's latest map?")]
result = abot.graph.invoke({"messages": messages})
print(result['messages'][-1].content)