## Agentic AI Workflow with Persistence

This project demonstrates an advanced AI agent built using the LangGraph framework, integrating the ReAct prompting strategy and Tavily for precise information retrieval. The agent is designed to perform tasks autonomously, maintain context across interactions, and provide coherent, contextually relevant responses.

# Features

Agentic Workflow
Implements a graph-based agent architecture using LangGraph, enabling the AI to autonomously reason, act, and adapt to dynamic contexts. This structure supports complex task execution far beyond traditional single-turn models.

Persistent Memory (SQLite-based)
Conversations are preserved across threads using an SQLite backend, enabling the agent to maintain contextual coherence and remember previous interactions — crucial for multi-step reasoning and user-specific dialogues.

ReAct Framework Integration
The agent operates on the ReAct (Reasoning + Acting) paradigm. It generates intermediate thoughts and tool invocations, resulting in grounded, explainable decision-making with significantly reduced hallucination.

LangGraph + Tavily Integration
LangGraph enables the construction of flexible, state-aware agent workflows, while Tavily provides real-time information retrieval for up-to-date and verifiable responses.

Flask-based API + HTML UI
The system features a lightweight, extensible Flask backend (app.py) as the agent’s interface layer. A minimal HTML frontend (index.html) facilitates easy testing and deployment in local and cloud environments.

# Repository Structure
The repository is organized as follows:​
```
├── app.py                     # Backend server (Flask)
├── index.html                # UI for the chat interface
├── langgraph_agent_module.py # Core logic for LangGraph Agent
├── README.md

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
   python app.py
   ```
# Usage
Once the agent runs, you can interact with it through the local host link in any browser (Chrome, Firefox, Edge, etc.). This multi-functional agent has persistence in place, which has the memory of the prompts given earlier in a specific thread. You can choose between various threads by starting a new chat. 



