from agentic.common import Agent, AgentRunner
from agentic.tools import WeatherTool

weather_agent = Agent(
    name="Weather Agent",
    welcome="I can give you some weather reports! Just tell me which city.",
    instructions="You are a helpful assistant.",
    tools=[WeatherTool()],
    model="openai/gpt-4o-mini"
)

if __name__ == "__main__":
    AgentRunner(weather_agent).repl_loop()