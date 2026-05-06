from langchain_core.messages import HumanMessage, SystemMessage
from .state import AgentState, Route, get_llm

def supervisor_node(state: AgentState):
    llm = get_llm()
    if not llm:
        print("[WARNING] LLM not configured. Supervisor routing using mock fallback logic.")
        msg = state["incoming_message"].lower()
        if not state.get("messages"):
            if "ticket" in msg or "commit" in msg: return {"next": "git_expert", "topic": "Ticket-404"}
            else: return {"next": "email_expert", "topic": "General"}
        return {"next": "drafter"}

    supervisor_prompt = """You are a supervisor managing a conversation between these workers: 'git_expert', 'email_expert', 'drafter'.
Given the following user request and the conversation history, decide who should act next. 
- If the user is asking about code, commits, PRs, or defects and the 'git_expert' HAS NOT answered yet, route to 'git_expert'.
- If the user is asking about emails, schedules, or meetings and the 'email_expert' HAS NOT answered yet, route to 'email_expert'.
- If the experts have responded (even if they found no information), route to 'drafter' to write the final response. DO NOT route back to an expert that has already answered.
- If the message is just a greeting or statement that expects absolutely no feedback, route to 'FINISH'.
- IMPORTANT: "FINISH" is ONLY for messages that expect no feedback. If the user asked a question, you MUST route to 'drafter' to provide an answer, even if the experts could not find any relevant information.
"""
    messages = [SystemMessage(content=supervisor_prompt), HumanMessage(content=state["incoming_message"])] + list(state.get("messages", []))
    try:
        router = llm.with_structured_output(Route)
        decision = router.invoke(messages)
        return {"next": decision.next, "topic": decision.topic}
    except Exception as e:
        return {"next": "git_expert" if not state.get("messages") else "drafter", "topic": "General"}

def supervisor_router(state: AgentState):
    return state["next"]
