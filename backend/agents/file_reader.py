from agentic.common import Agent, AgentRunner
import os

def read_file(path):
    """
    Read the information from a text file with given path
    
    Args:
        path: the path to the text file
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level from agents/
    abs_path = os.path.join(base_dir, path)
    with open(abs_path, "r") as file:
        text = file.readlines()

    return text

file_reader = Agent(
    name="File Reader Agent",
    welcome="",
    instructions="You are a helpful assistant.",
    tools=[read_file],
    model="openai/gpt-4o-mini"
)

if __name__ == "__main__":
    print(os.getcwd())
    # print(read_file('agents/info.txt'))
    AgentRunner(file_reader).repl_loop()