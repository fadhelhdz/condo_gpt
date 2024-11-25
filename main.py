import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

from prefix import SQL_PREFIX
from boilerplate import marker_boilerplate, holding_period_boilerplate, two_bed_holding_period_boilerplate, javascript_map_boilerplate, school_marker_format_boilerplate, building_marker_format_boilerplate

POSTGRES_USER = os.getenv["PG_USER"]
POSTGRES_PASSWORD = os.getenv["PG_PASSWORD"]
POSTGRES_PORT = os.getenv["PG_PORT"]
POSTGRES_DB = os.getenv["PG_DB"]

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