from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import os, time, re

load_dotenv()

def _make_llm(max_tokens=2048):
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=max_tokens,
    )

llm = _make_llm()

def _invoke_with_retry(fn, *args, retries=3, wait=8, **kwargs):
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = str(e).lower()
            retryable = any(k in msg for k in ("rate", "429", "connection", "timeout"))
            if attempt < retries - 1 and retryable:
                time.sleep(wait * (attempt + 1))
            else:
                raise

def _extract_first_url(search_text: str) -> str | None:
    """Pull the first URL out of search results so we don't send a wall of text to the LLM."""
    urls = re.findall(r'https?://[^\s\)\]\"\']+', search_text)
    # prefer non-wikipedia, non-pdf links
    for u in urls:
        if "wikipedia" not in u and ".pdf" not in u:
            return u.rstrip(".,;)")
    return urls[0].rstrip(".,;)") if urls else None

def build_search_agent():
    agent = create_react_agent(
        model=llm,
        tools=[web_search],
        prompt="Use the web_search tool once to find information, then return the results.",
    )
    class WrappedAgent:
        def invoke(self, inp):
            return _invoke_with_retry(agent.invoke, inp)
    return WrappedAgent()

def build_reader_agent():
    """
    Bypass the LLM agent entirely — llama-3.1-8b-instant hallucinates
    tools like 'brave_search'. Just extract the URL and call scrape_url directly.
    """
    class DirectScraper:
        def invoke(self, inp):
            messages = inp.get("messages", [])
            full_text = messages[-1][1] if messages else ""
            url = _extract_first_url(full_text)
            if not url:
                scraped = "No URL found to scrape."
            else:
                try:
                    scraped = scrape_url.invoke(url)
                except Exception as ex:
                    scraped = f"Scrape failed: {ex}"

            # Return an object with .content so app.py can do rr["messages"][-1].content
            class _Msg:
                def __init__(self, text): self.content = text
            return {"messages": [_Msg(scraped)]}

    return DirectScraper()

# Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}
Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])
writer_chain = writer_prompt | llm | StrOutputParser()

# Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:
Score: X/10
Strengths:
- ...
- ...
Areas to Improve:
- ...
- ...
One line verdict:
..."""),
])
critic_chain = critic_prompt | llm | StrOutputParser()
