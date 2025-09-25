from autogen_core.tools import FunctionTool


async def read_file(file_path: str) -> str:
  with open(file_path, "r") as f:
    return f.read()


file_read_tool = FunctionTool(
  func=read_file,
  name="read_file",
  description=f"""Reads the content of a file.
  Use this tool when tasked with reading the content of a file.
  Input: A string file path (e.g., "./scrape_results/web_scrape_123.txt").
  Output: The content of the file.
  Example: read_file("./scrape_results/web_scrape_123.txt")""",
)

