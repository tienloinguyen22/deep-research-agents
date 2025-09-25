import json
import os
import asyncio
import nltk
from dotenv import load_dotenv
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from autogen_core.models import ModelInfo, ModelFamily, UserMessage
from tools.search import web_search

nltk.download('punkt')
nltk.download('punkt_tab')

async def main():
  load_dotenv()
  print("Hello from deep-research-agents!")

  # # init model & agents
  # model_client = AzureAIChatCompletionClient(
  #   model="openai/gpt-4o",
  #   endpoint="https://models.github.ai/inference",
  #   credential=AzureKeyCredential(os.environ["PERSONAL_GITHUB_TOKEN"]),
  #   model_info=ModelInfo(
  #     vision=False,
  #     function_calling=True,
  #     json_output=True,
  #     family=ModelFamily.GPT_4,
  #     structured_output=True,
  #   ),
  # )

  # # test model
  # content = "What is the capital of Viet Nam?"
  # print("Question: ", content)

  # result = await model_client.create([UserMessage(content=content, source="user")])
  # print("Answer: ", result.content)
  # print("Cached: ", result.cached)
  # print("Finish Reason: ", result.finish_reason)
  # print("Thought: ", result.thought)
  # print("Usage: ", result.usage)
  # print("-"*80)

  # test search tool
  query = "AI in improving software engineer performance"
  print("Query: ", query)

  rawResults = await web_search(query)
  parsedResults = json.loads(rawResults)
  for result in parsedResults["summarize_results"]:
    print("Title: ", result["title"])
    print("Snippet: ", result["snippet"])
    print("URL: ", result["url"])
    print("-"*30)

  # # close
  # await model_client.close()


if __name__ == "__main__":
	asyncio.run(main())
