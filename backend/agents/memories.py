from agentic.common import Agent, AgentRunner

agent = Agent(
	name="...",
	instructions="You are a helpful agent",
	memories = ["your favorite color is green”, “you are running on a Mac computer"]
)

if __name__ == "__main__":
    AgentRunner(agent).repl_loop()