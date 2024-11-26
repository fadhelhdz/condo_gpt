import os
import re

import markdown

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from langgraph.prebuilt import create_react_agent

from markupsafe import Markup

from prefix import SQL_PREFIX
from boilerplate import marker_boilerplate, holding_period_boilerplate, two_bed_holding_period_boilerplate, javascript_map_boilerplate, school_marker_format_boilerplate, building_marker_format_boilerplate
from tools import setup_tools

POSTGRES_USER = os.getenv("PG_USER")
POSTGRES_PASSWORD = os.getenv("PG_PASSWORD")
POSTGRES_PORT = os.getenv("PG_PORT")
POSTGRES_DB = os.getenv("PG_DB")

connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"

db = SQLDatabase.from_uri(connection_string)

llm = ChatOpenAI(model="gpt-4o-mini")

prefix = SQL_PREFIX.format(
    table_names=db.get_usable_table_names(),
    holding_period_boilerplate = holding_period_boilerplate,
    two_bed_holding_period_boilerplate = two_bed_holding_period_boilerplate,

    marker_boilerplate = marker_boilerplate,
    javascript_map_boilerplate = javascript_map_boilerplate,
    building_marker_format_boilerplate = building_marker_format_boilerplate,
    school_marker_format_boilerplate = school_marker_format_boilerplate,
)

system_message = SystemMessage(content=prefix)

tools = setup_tools(db, llm)

agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)

def print_sql(sql):
    print("""
    The SQL query is:
          
          {}

    """.format(sql))

def extract_and_remove_html(text):
    html_pattern = r"```html\s*([\s\S]*?)\s*```"

    match = re.search(html_pattern, text, re.IGNORECASE)

    if match:
        html_code = match.group(1).strip()
        text_without_html = re.sub(html_pattern, "", text, flags=re.IGNORECASE).strip()

        return Markup(html_code), text_without_html
    return None, text

def process_markdown(text):
    # Convert markdow to HTML
    html = markdown.markdown(text, extensions=["extra", "codehilite"])
    # Wrap the result in Markup to prevent auto-escaping
    return Markup(html)

def process_question(prompted_question , conversation_history):
    context = "\n".join(
        [f"Q: {entry['question']}\n A: {entry['answer']}"
         for entry in conversation_history]
    )
    consolidated_prompt = f"""
    Previous conversation:
    {context}

    New question: {prompted_question}
    Please answer the new question, taking into account the context from the previous conversation if relevant.
    """
    prompt = consolidated_prompt if conversation_history else prompted_question

    content = []

    for s in agent_executor.stream({"messages": HumanMessage(content=prompt)}):
        for msg in s.get("agent", {}).get ("messages", []):
            for call in msg.tool_calls:
                if sql := call.get("args", {}).get("query", None):
                    print(print_sql(sql))
            print(msg.content)
            html, stripped_text = extract_and_remove_html(msg.content)
            content.append(process_markdown(stripped_text))
            if html:
                content.append(html)

    return content        

# process_question("What is the most recent sale in the database") # for testing openai api