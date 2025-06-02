from agentic.common import Agent, AgentRunner
from agentic.tools import WebCrawler, UWOTool

from dotenv import load_dotenv

load_dotenv("../.env")

web_crawler = WebCrawler()
uwo_tool = UWOTool()

academic_advisor = Agent(
    name="Western University academic advisor",
    instructions="You help obtain information on courses at Western University. You use tools to obtain course details. Always include the information you retrieved in your response to the user.",
    tools=[web_crawler, uwo_tool],
    memories=["When you get info for a course, immediately provide the requested information in the same turn without waiting a turn."]
)

agent = AgentRunner(academic_advisor)

if __name__ == "__main__":
    agent.repl_loop()
    # print("Response: " + agent.turn("What can you do?"))
    # print("Response: " + agent.turn("What are breadth requirements at UWO?"))