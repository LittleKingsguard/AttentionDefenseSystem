from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .supervisor import supervisor_node, supervisor_router
from .experts.git_expert import git_expert_node
from .experts.email_expert import email_expert_node
from .experts.a2a_expert import a2a_expert_node
from .drafter import drafter_node
from .human import human_approval, send_response, datalink_ingest_node

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("git_expert", git_expert_node)
    builder.add_node("email_expert", email_expert_node)
    builder.add_node("a2a_expert", a2a_expert_node)
    builder.add_node("drafter", drafter_node)
    builder.add_node("human_approval", human_approval)
    builder.add_node("send_response", send_response)
    builder.add_node("datalink_ingest", datalink_ingest_node)

    builder.set_entry_point("supervisor")

    builder.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "git_expert": "git_expert", 
            "email_expert": "email_expert", 
            "a2a_expert": "a2a_expert",
            "drafter": "drafter", 
            "FINISH": END
        }
    )

    builder.add_edge("git_expert", "supervisor")
    builder.add_edge("email_expert", "supervisor")
    builder.add_edge("a2a_expert", "supervisor")
    builder.add_edge("drafter", "human_approval")
    builder.add_edge("human_approval", "send_response")
    builder.add_edge("send_response", "datalink_ingest")
    builder.add_edge("datalink_ingest", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory, interrupt_before=["human_approval"])

graph = build_graph()

__all__ = ["graph", "AgentState"]
