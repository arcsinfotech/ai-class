import os
import subprocess

from langchain.agents import create_agent
from langchain.tools import tool

from app.configs.settings import settings

MODEL = "gpt-5-mini"
WORKING_DIR = os.getcwd()

def _safe_path(rel_path: str) -> str:
    full = os.path.abspath(os.path.join(WORKING_DIR, rel_path))
    if not full.startswith(os.path.abspath(WORKING_DIR)):
        raise ValueError("Refusing to access a path outside the working directory.")
    return full

@tool
def list_files(path: str = ".") -> str:
    """List files and folders inside the working directory (or a subfolder of it)."""
    target = _safe_path(path)
    if not os.path.isdir(target):
        return f"ERROR: '{path}' is not a folder."
    entries = os.listdir(target)
    result = "\n".join(entries) if entries else "(empty folder)"
    print(result)
    return result

@tool
def read_file(path: str) -> str:
    """Read the full text content of a file in the working directory."""
    full = _safe_path(path)
    if not os.path.exists(full):
        parent = os.path.dirname(full) or WORKING_DIR
        if os.path.isdir(parent):
            siblings = os.listdir(parent)
            return (
                f"ERROR: '{path}' does not exist."
                f"files available in that folder: {siblings}."
                f"Call list_files again if you need to look elsewhere, then retry"
                f"read_file with the correct path."
            )
        return f"ERROR: '{path}' does not exist, and its parent folder was not found either."
    
    if os.path.isdir(full):
        return f"ERROR: '{path}' is a folder, not a file. Use list_files on it instead."
    
    with open(full, "r", encoding="utf-8") as f:
        return f.read()

@tool
def run_command(command: str) -> str:
    """Run a terminal/shell command inside the workign directory and return its output."""
    print(command)
    result = subprocess.run(
        command, shell=True, cwd=WORKING_DIR, capture_output=True, text=True, timeout=60
    )
    output = result.stdout + result.stderr
    print(output)
    return output.strip() or f"(command finished exit core {result.returncode}, no ouput)"

@tool
def write_file(path: str, content: str) -> str:
    """Create a new file, or Fully overwrite an existing file with new content.
    USe this for new files, or when the whole file should be replaced.
    for a small changes inside an existing file, don't use this tool."""
    full = _safe_path(path) # /test.py
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, 'w', encoding="utf-8") as f:
        f.write(content)
    return f"wrote {len(content)} characters to {path}"

SYSTEM_PROMPT = (
    "You are an autonomous coding agent. You work inside a single project folder.\n"
    "Rules:\n"
    "- If you are not 100% sure a file path/name is correct, call list_files "
    "first instead of guessing. If read_file returns an ERROR, read the error, "
    "look at the files it lists (or call list_files on another folder), and "
    "retry with the corrected path. Never give up after one failed read.\n"
    "- To change part of an existing file (fix a bug, add a function, add "
    "error handling, etc.), ALWAYS read_file first, then use edit_file with "
    "an exact old_text snippet copied from what you read. Do not retype the "
    "whole file.\n"
    "- Before editing, think about whether the text you want to change could "
    "appear more than once in the file with DIFFERENT meanings (e.g. the same "
    "word/value used in a comment, a data dictionary, a string, and an actual "
    "variable). If there's any doubt, call find_text first to see every "
    "occurrence with line numbers. If multiple occurrences are genuinely "
    "different things (not just the same edit repeated), tell the user what "
    "you found and ask which one(s) they mean, instead of silently guessing.\n"
    "- Only use write_file to create a brand-new file, or when the user "
    "explicitly wants the whole file replaced.\n"
    "- After making a change, briefly explain exactly what you changed, "
    "including the line(s), and mention any similar-looking spots you left "
    "unchanged and why.\n"
    "Be concise."
)

TOOLS = [list_files, read_file, write_file]

agent = create_agent(MODEL, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

def run_agent(history: list) -> list:
    response = agent.invoke({"messages": history})

    for msg in response["messages"][len(history):]:
        
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for call in tool_calls:
                print(f" -> running tool: {call["name"]}({call['args']})")
    
    final_message = response["messages"][-1]
    print(f"\nAgent: {final_message.content}")
    return response["messages"]


if __name__ == "__main__":
    conversation: list = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "end"]:
            break
        if user_input:
            conversation.append({"role": "user", "content": user_input})
            conversation = run_agent(conversation)
