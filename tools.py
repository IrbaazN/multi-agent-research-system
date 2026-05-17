from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os, time
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets."""
    try:
        results = tavily.search(query=query, max_results=5)
        out = []
        for r in results["results"]:
            out.append(
                f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
            )
        return "\n----\n".join(out)
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    print(f">>> Scraping URL: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # FIX 4: retry up to 2 times, longer timeout (15s), proper fallback
    for attempt in range(2):
        try:
            resp = requests.get(url, timeout=15, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            if len(text) < 100:
                return f"Page at {url} had no readable content."
            return text[:4000]          # slightly more content for the writer
        except requests.exceptions.Timeout:
            if attempt == 0:
                time.sleep(2)
                continue
            return f"Could not scrape {url}: request timed out after 15s."
        except Exception as e:
            return f"Could not scrape {url}: {str(e)}"
