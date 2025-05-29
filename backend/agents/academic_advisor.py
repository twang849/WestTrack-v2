from agentic.common import Agent, AgentRunner
from agentic.tools import WebCrawler, uwo_tool

web_crawler = WebCrawler()

academic_advisor = Agent(
    name="Western University academic advisor",
    instructions="You help obtain information on courses at Western University. You use tools to obtain course details. Always include the information you retrieved in your response to the user.",
    tools=[web_crawler],
    memories=["When you get info for a course, immediately provide the requested information in the same turn without waiting a turn."]
)

if __name__ == "__main__":
    AgentRunner(academic_advisor).repl_loop()