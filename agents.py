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

def _extract_first_url(search_text: str):
    urls = re.findall(r'https?://[^\s\)\]\"\']+', search_text)
    for u in urls:
        if "wikipedia" not in u and ".pdf" not in u:
            return u.rstrip(".,;)")
    return urls[0].rstrip(".,;)") if urls else None

def build_search_agent():
    llm = _make_llm()
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
            class _Msg:
                def __init__(self, text): self.content = text
            return {"messages": [_Msg(scraped)]}
    return DirectScraper()

def build_writer_chain():
    llm = _make_llm()
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
    return writer_prompt | llm | StrOutputParser()

def build_critic_chain():
    llm = _make_llm()
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
    return critic_prompt | llm | StrOutputParser()
