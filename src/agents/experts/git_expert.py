from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from ..state import AgentState, get_llm, tools

def git_expert_node(state: AgentState):
    llm = get_llm()
    if not llm:
        print("[WARNING] LLM not configured. Git Expert returning mock data.")
        return {"messages": [AIMessage(content="Mock git info found.", name="git_expert")], "sender": "git_expert"}
    agent = create_react_agent(llm, tools=tools, prompt="You are a Git Expert. Use tools to find information about code, commits, and defects.")
    invoke_msgs = [HumanMessage(content=f"Request: {state['incoming_message']}")] + list(state.get("messages", []))
    result = agent.invoke({"messages": invoke_msgs})
    final_msg = result["messages"][-1]
    return {"messages": [AIMessage(content=final_msg.content, name="git_expert")], "sender": "git_expert"}
