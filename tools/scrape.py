import json
import os
import random
import re
from typing import Optional
from urllib.parse import urlparse
import uuid
import requests
from bs4 import BeautifulSoup
import newspaper
from nltk.tokenize import word_tokenize
from autogen_core.tools import FunctionTool

user_agents = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
  "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

headers = {
  "User-Agent": random.choice(user_agents),
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5"
}

news_domains = [
  "news", "article", "blog", "story", "post", "cnn.com", "bbc.com",
  "nytimes.com", "theguardian.com", "reuters.com", "apnews.com"
]

elements = ["p", "h1", "h2", "h3", "article"]

def save_text(url: str, text: str) -> str:
  # store the full result into a file for later reference
  os.makedirs("scrape_results", exist_ok=True)
  file_path = f"./scrape_results/web_scrape_{uuid.uuid4()}.txt"
  with open(file_path, "w") as f:
    f.write(text)

  return file_path


async def web_scrape(
  url: str,
  max_return_tokens: int = 300,
  use_newspaper: Optional[bool] = None
) -> str:
  """Scrape text content from a URL using either newspaper4k or BeautifulSoup.

  Args:
    url (str): The URL to scrape (e.g., "https://example.com/article").
    max_return_tokens (int): Maximum tokens of the scraped text (default: 300 tokens).
    use_newspaper (bool): Whether to use newspaper4k to scrape the text (default: False).

  Returns:
    str: A JSON string containing the extracted text (up to max_return_tokens tokens) or an error message and file path for full data.
  """
  try:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    path = parsed_url.path.lower()

    # heuristic check if we should use newspaper4k
    if use_newspaper is None:
      use_newspaper = any(keyword in domain or keyword in path for keyword in news_domains)

    # Newspaper4k scraper
    if use_newspaper:
      article = newspaper.Article(url, language='en')
      article.download()
      article.parse()
      text = article.text
      file_path = save_text(url, text)
      return json.dumps({
        "text": " ".join(word_tokenize(text)[:max_return_tokens]) if text else "Error: No content extracted by newspaper4k.",
        "file_path": file_path
      })
    else:
      # BeautifulSoup scraper
      response = requests.get(url, headers=headers, timeout=15)
      response.raise_for_status()
      soup = BeautifulSoup(response.text, "html.parser")

      # Remove unwanted elements
      for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

      # Extract text from specified elements
      text_parts = []
      for tag in elements:
        for element in soup.find_all(tag):
          text = element.get_text(separator=" ", strip=True)
          if text:
            text_parts.append(text)

      # Clean and combine text
      combined_text = " ".join(text_parts)
      cleaned_text = re.sub(r'\s+', ' ', combined_text).strip()
      file_path = save_text(url, cleaned_text)
      return json.dumps({
        "text": " ".join(word_tokenize(cleaned_text)[:max_return_tokens]) if cleaned_text else "Error: No content extracted by BeautifulSoup.",
        "file_path": file_path
      })
  except requests.exceptions.Timeout:
    return "Error: Request timed out after 15 seconds."
  except requests.exceptions.HTTPError as e:
    return f"Error: HTTP error occurred: {str(e)}"
  except requests.exceptions.ConnectionError:
    return "Error: Failed to connect to the server."
  except Exception as e:
    return f"Error scraping URL: {str(e)}"


web_scrape_tool = FunctionTool(
  func=web_scrape,
  name="web_scrape",
  description=f"""Scrapes text content from a URL using either newspaper4k or BeautifulSoup.
  Use this tool when tasked with extracting text from a web page.
  Input: A string URL (e.g., "https://example.com/article") and optional max_return_tokens (int, default 300 tokens).
  Output: A JSON string containing the extracted text (up to max_return_tokens tokens) or an error message and file path for full data.
  Limitations: May hit rate limits; returns error if scraping fails.
  Example: web_scrape("https://example.com/article", max_return_tokens=500)""",
)

