import os
import asyncio
import nltk
from dotenv import load_dotenv
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from autogen_core.models import ModelInfo, ModelFamily
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import Swarm
from prompt import CRITIC_AGENT_DESCRIPTION, CRITIC_AGENT_PROMPT, PLANNER_AGENT_DESCRIPTION, PLANNER_AGENT_PROMPT, SEARCH_AGENT_DESCRIPTION, SEARCH_AGENT_PROMPT, WRITER_AGENT_DESCRIPTION, WRITER_AGENT_PROMPT
from tools.files import read_file_tool, write_output_to_file_tool
from tools.scrape import web_scrape_tool
from tools.search import web_search_tool
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console

nltk.download('punkt')
nltk.download('punkt_tab')

async def main():
  load_dotenv()
  print("Hello from deep-research-agents!")

  # init model & agents
  model_client = AzureAIChatCompletionClient(
    model="openai/gpt-4o",
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
  planner_agent = AssistantAgent(
    name="PlannerAgent",
    description=PLANNER_AGENT_DESCRIPTION,
    model_client=model_client,
    system_message=PLANNER_AGENT_PROMPT,
    handoffs=["SearchAgent", "WriterAgent", "CriticAgent"],
  )
  search_agent = AssistantAgent(
    name="SearchAgent",
    description=SEARCH_AGENT_DESCRIPTION,
    model_client=model_client,
    system_message=SEARCH_AGENT_PROMPT,
    tools=[read_file_tool, web_scrape_tool, web_search_tool],
    handoffs=["WriterAgent", "PlannerAgent"],
  )
  writer_agent = AssistantAgent(
    name="WriterAgent",
    description=WRITER_AGENT_DESCRIPTION,
    model_client=model_client,
    system_message=WRITER_AGENT_PROMPT,
    tools=[read_file_tool, write_output_to_file_tool],
    handoffs=["CriticAgent", "PlannerAgent"],
  )
  critic_agent = AssistantAgent(
    name="CriticAgent",
    description=CRITIC_AGENT_DESCRIPTION,
    model_client=model_client,
    system_message=CRITIC_AGENT_PROMPT,
    tools=[read_file_tool],
    handoffs=["WriterAgent", "PlannerAgent"],
  )

  # run team
  deep_research_team = Swarm(
    participants=[planner_agent, search_agent, writer_agent, critic_agent],
    termination_condition=TextMentionTermination("FINISHED")
  )

  # run
  await Console(deep_research_team.run_stream(task="AI Coding Tool effect on the software job market"))

  # close
  await model_client.close()


if __name__ == "__main__":
	asyncio.run(main())
