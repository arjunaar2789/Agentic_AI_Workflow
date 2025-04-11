## Agentic AI Workflow with Persistence

This project demonstrates an advanced AI agent built using the LangGraph framework, integrating the ReAct prompting strategy and Tavily for precise information retrieval. The agent is designed to perform tasks autonomously, maintain context across interactions, and provide coherent, contextually relevant responses.

# Features
Agentic Workflow: This enables the AI agent to perform tasks autonomously, make decisions, and adapt to changing contexts, moving beyond traditional request-response models.​

Persistent Memory: Maintains context over multiple interactions within a thread, ensuring coherent and contextually relevant responses.​

ReAct Framework Integration: Combines reasoning and acting by prompting the AI to generate both thought processes and actions interleaved. This approach enhances decision-making capabilities and reduces hallucinations by grounding responses in external information sources.​

LangGraph and Tavily Integration: Utilizes LangGraph for structured agent workflows and Tavily for precise information retrieval, enhancing the agent's ability to handle complex, multi-step processes efficiently.

# Repository Structure
The repository is organized as follows:​
```
Agentic_AI_Workflow/
├── langgraph_agent_with_persistence.py  # Main script implementing the agentic workflow with persistent memory
├── README.md                            # Project overview and documentation
```
# Getting Started

1. Clone the repository
   ```
   git clone https://github.com/arjunaar2789/Agentic_AI_Workflow.git
   cd Agentic_AI_Workflow
   ```
2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Set up environment variables
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
4. Running the Agent
   ```
   python langgraph_agent_with_persistence.py
   ```
# Usage
Once the agent is running, you can interact with it through the command-line interface. The agent will maintain context within each session, allowing for coherent multi-turn conversations.



