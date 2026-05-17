from langgraph.prebuilt import create_react_agent      # FIX 1: correct import
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import os, time

load_dotenv()

def _make_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=2048,          # FIX 2: was 800 — too low for agent loops
    )

llm = _make_llm()

# FIX 3: retry wrapper for Groq rate-limit errors (429 / connection reset)
def _invoke_with_retry(fn, *args, retries=3, wait=8, **kwargs):
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = str(e).lower()
            if attempt < retries - 1 and ("rate" in msg or "429" in msg or "connection" in msg or "timeout" in msg):
                time.sleep(wait * (attempt + 1))
            else:
                raise

def build_search_agent():
    agent = create_react_agent(
        model=llm,
        tools=[web_search],
        prompt="You can ONLY use the tool: web_search. Always call it once and return the results."
    )
    class WrappedAgent:
        def invoke(self, inp):
            return _invoke_with_retry(agent.invoke, inp)
    return WrappedAgent()

def build_reader_agent():
    agent = create_react_agent(
        model=llm,
        tools=[scrape_url],
        prompt="You can ONLY use the tool: scrape_url. Pick ONE URL from the search results and scrape it."
    )
    class WrappedAgent:
        def invoke(self, inp):
            return _invoke_with_retry(agent.invoke, inp)
    return WrappedAgent()

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
