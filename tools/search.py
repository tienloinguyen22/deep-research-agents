import json
import os
import uuid
from ddgs import DDGS
from autogen_core.tools import FunctionTool
from nltk.tokenize import word_tokenize

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

    # only return 80 tokens for snippet to save context window
    summarize_results = [
      {
        "title": r["title"],
        "snippet": " ".join(word_tokenize(r["body"])[:50]),
        "url": r["href"],
      }
      for r in results
    ]

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
