from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from app.configs.settings import settings

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    city: str
    weather_info: str
    packing_info: str
    next: str

def call_llm(system_prompt: str, user_prompt: str, model_name: str = "gpt-4o-mini", web_search: bool = False) -> str:
    llm = ChatOpenAI(model=model_name, api_key=settings.OPENAI_API_KEY)
    if web_search:
        llm.use_responses_api = True
        web_search_tools = {
            "type": "web_search"
        }
        llm = llm.bind_tools([web_search_tools])
    result = llm.invoke([("system", system_prompt), ("user", user_prompt)])
    return result.content

FAKE_WEATHER =  {
    "New York": "31°C, cloudy, light chance of rain",
    "London": "20°C, sunny, light chance of rain",
    "Paris": "25°C, sunny, light chance of rain",
}

def supervisor_node(state: State) -> dict:
    
    if not state.get('weather_info'):
        city = state["city"]
        ask = f"[Supervisor -> WeatherAgent] What's the weather in {city}"
        print(ask)
        return {"messages": [AIMessage(content=ask)], "next": "weather"}
    
    if not state.get("packing_info"):
        ask = (
            f"[Supervisor -> PackingAgent] The weather in {state['city']} is "
            f"'{state["weather_info"]}'. Given that, what should the traveler pack?"
        )
        print(ask)
        return {"messages": [AIMessage(content=ask)], "next": "packing"}
    
    final = (
        f"Final answer for {state["city"]}:\n"
        f" WeatherL {state["weather_info"]}\n"
        f" packing list: {state['packing_info']}"
    )
    print(final)
    return {"messages": [AIMessage(content=final)], "next": "done"}

def route_supervisor(state: State) -> str:
    return state["next"] # weather | packing | done

def weather_agent_node(state: State) -> dict:
    city = state["city"]
    result = call_llm(
        f"You are a weather expert. Answer in short just in one line.",
        f"What's the weather in {city}?",
        model_name="gpt-5-search-api",
        # web_search = True
    )
    # result = result[1]["text"]
    # result = "31°C, cloudy, light chance of rain"
    print(f"[WeatherAgent -> Supervisor] {result}")
    return {"messages": [AIMessage(content=result)], "weather_info": result}

def packing_agent_node(state: State) -> dict:
    weather = state["weather_info"]
    result = call_llm(
        f"You are a travel packing expert, suggest 3-5 items based on the weather given. Just return the list of items, no other text no reasoning.",
        f"Weather: {weather}. What should i pack?"
    )
    print(f"[PackingAgent -> Supervisor] {result}")
    return {"messages": [AIMessage(content=result)], "packing_info": result}

def build_graph():
    builder = StateGraph(State)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("weather_agent", weather_agent_node)
    builder.add_node("packing_agent", packing_agent_node)

    builder.add_edge(START, "supervisor")

    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {"weather": "weather_agent", "packing": "packing_agent", "done": END}
    )

    builder.add_edge("weather_agent", "supervisor")
    builder.add_edge("packing_agent", "supervisor")

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    question = "I am traveling to New York next week, What should I pack?"
    print(f"User asked: {question}\n")

    initial_state: State = {
        "messages": [HumanMessage(content=question)],
        "city": "New York",
        "weather_info": "",
        "packing_info": "",
        "next": ""
    }

    result = graph.invoke(initial_state)