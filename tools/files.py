from autogen_core.tools import FunctionTool
import os
import uuid


async def read_file(file_path: str) -> str:
  with open(file_path, "r") as f:
    return f.read()


async def write_output_to_file(content: str) -> str:
  os.makedirs("output_results", exist_ok=True)
  file_path = f"./output_results/output_{uuid.uuid4()}.md"
  with open(file_path, "w") as f:
    f.write(content)
  return file_path


read_file_tool = FunctionTool(
  func=read_file,
  name="read_file",
  description=f"""Reads the content of a file.
  Use this tool when tasked with reading the content of a file.
  Input: A string file path (e.g., "./scrape_results/web_scrape_123.txt").
  Output: The content of the file.
  Example: read_file("./scrape_results/web_scrape_123.txt")""",
)
write_output_to_file_tool = FunctionTool(
  func=write_output_to_file,
  name="write_output_to_file",
  description=f"""Writes output to a file.
  Use this tool when tasked with writing the output to a file.
  Input: Content to write to a file.
  Output: The file path of the output file.
  Example: write_output_to_file("Content to write to a file")""",
)

