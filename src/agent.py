from datetime import datetime
from typing import Annotated
from numpy.ma.mrecords import fromtextfile
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from src.largelm import get_llm
from src.utilities.helper import create_tool_node_with_fallback
from tools import  (lookup_policy,
                    fetch_all_complaints_made_by_customer,
                    fetch_customer_information_from_customer_id,
                    fetch_list_of_all_products_sold_to_customer,
                    fetch_all_interactions_for_customer)
                    # update_complaint,
                    # record_interaction_for_customer
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

def get_agent_graph():

    primary_assistant_prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system",
            "You are a helpful customer support assistant for Example.com. "
            " Use the provided tools to search for Customer, Sales Information, Inventory Information, Complaint retrieval"
            # "Use the update tool to record the complaint the user tells and always record all the interaction with customer using record_interaction_for_customer tool"
            "You are also to look at company policy using lookup_policy tool to check on company policy when policy related questions arise"
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
    ).partial(time=datetime.now)

    zeroshottools = [lookup_policy,
                 fetch_all_complaints_made_by_customer,
                 fetch_customer_information_from_customer_id,
                 fetch_list_of_all_products_sold_to_customer,
                 fetch_all_interactions_for_customer]
                #  update_complaint,
                #  record_interaction_for_customer]
    LLM = get_llm()
    zero_shot_runnable = primary_assistant_prompt | LLM.bind_tools(zeroshottools)

    builder = StateGraph(State)

    # Define nodes: these do the work
    builder.add_node("assistant", Assistant(zero_shot_runnable))
    builder.add_node("tools", create_tool_node_with_fallback(zeroshottools))
    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # The checkpointer lets the graph persist its state
    # this is a complete memory for the entire graph.
    memory = MemorySaver()
    zeroshotgraph = builder.compile(checkpointer=memory)

    return zeroshotgraph

