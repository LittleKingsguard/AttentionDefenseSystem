from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from ..state import AgentState, get_llm, tools

def a2a_expert_node(state: AgentState):
    llm = get_llm()
    if not llm:
        print("[WARNING] LLM not configured. A2A Expert returning mock data.")
        return {"messages": [AIMessage(content="Mock A2A info found.", name="a2a_expert")], "sender": "a2a_expert"}
        
    agent = create_react_agent(
        llm, 
        tools=tools, 
        prompt="You are an A2A Expert. Use tools to find information about past agent-to-agent messages, handshakes, and automated negotiations. Look for context from previous interactions between your agent and other agents."
    )
    
    invoke_msgs = [HumanMessage(content=f"Request: {state['incoming_message']}")] + list(state.get("messages", []))
    result = agent.invoke({"messages": invoke_msgs})
    final_msg = result["messages"][-1]
    
    return {"messages": [AIMessage(content=final_msg.content, name="a2a_expert")], "sender": "a2a_expert"}
