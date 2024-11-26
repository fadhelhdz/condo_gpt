import re
import ast

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit

def query_as_list(db, query):
    res = db.run(query)
    return ast.literal_eval(res)[0]
    


def setup_tools(db, llm):
    addresses = query_as_list(db, "SELECT address FROM core_condobuilding")
    alt_names = query_as_list(db, "SELECT alt_name FROM core_condobuilding")
    vector_db = FAISS.from_texts(alt_names + addresses, OpenAIEmbeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k":5})
    description = """Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is a valid proper nouns. Use the most similar to the search"""
    retriever_tool = create_retriever_tool(
        retriever, 
        name="search_proper_nouns", 
        description=description)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()
    tools.append(retriever_tool)

    return tools