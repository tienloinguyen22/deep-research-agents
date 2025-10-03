import json
import os
from textwrap import dedent
import uuid
from ddgs import DDGS
from autogen_core.tools import FunctionTool
from nltk.tokenize import word_tokenize
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from autogen_core.models import ModelInfo, ModelFamily, SystemMessage, UserMessage
from dotenv import load_dotenv

load_dotenv()

summarize_model_client = AzureAIChatCompletionClient(
  model="openai/gpt-4.1-mini",
  endpoint="https://models.github.ai/inference",
  credential=AzureKeyCredential(os.environ["PERSONAL_GITHUB_TOKEN"]),
  model_info=ModelInfo(
    vision=False,
    function_calling=True,
    json_output=True,
    family=ModelFamily.GPT_4,
    structured_output=True,
  ),
)

async def summarize_result(content: str) -> str:
  """Summarize a result using OpenAI."""
  result = await summarize_model_client.create([
    SystemMessage(content=dedent(f"""Summarize the provided text in a clear, concise manner, retaining all key information, main ideas, and critical details.
    Eliminate redundant phrases, excessive details, and verbose language while maintaining the original meaning and intent.
    Aim for a summary that is approximately 20-30% of the original length, unless otherwise specified, and ensure the tone remains neutral and professional.""")),
    UserMessage(content=content, source="user")
  ])
  print(result)
  assert isinstance(result.content, str)
  return result.content

async def web_search(query: str, max_results: int = 5) -> str:
  """Perform a web search using DuckDuckGo.

  Args:
    query (str): The search query (e.g., "AI impact on climate change").
    max_results (int): Maximum number of results to return (default: 5).

  Returns:
    str: A JSON string summarized results and file path for full data.
  """
  try:
    print(f"Searching DDG for: {query}")
    ddgs = DDGS()
    results = ddgs.text(query, max_results=max_results)

    # summarize the result
    summarize_results = []
    for r in results:
      summarize_body = await summarize_result(r["body"])
      r["body"] = summarize_body
      summarize_results.append({
        "title": r["title"],
        "snippet": " ".join(word_tokenize(summarize_body)[:50]),
        "url": r["href"],
      })

    # store the full result into a file for later reference
    os.makedirs("search_results", exist_ok=True)
    file_path = f"./search_results/web_search_{uuid.uuid4()}.json"
    with open(file_path, "w") as f:
      json.dump(results, f)

    return json.dumps({
      "summarize_results": summarize_results,
      "file_path": file_path
    })
  except Exception as e:
    return json.dumps({
      "error": f"Search failed: {str(e)}"
    })


web_search_tool = FunctionTool(
  func=web_search,
  name="web_search",
  description=f"""Performs a web search to find relevant information for a research query.
  Use this tool when tasked with gathering data from the internet, such as articles or papers.
  Input: A string query (e.g., "AI impact on climate change") and optional max_results (int, default 5).
  Output: A JSON string summarized results and file path for full data.
  Limitations: May hit rate limits; returns error if search fails.
  Example: web_search("AI impact on climate change", max_results=5)""",
)
