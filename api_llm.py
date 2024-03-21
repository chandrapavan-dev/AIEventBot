import datetime
import os

from langchain.globals import set_debug
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

set_debug(True)

os.environ["OPENAI_API_KEY"] = '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'
os.environ["GOOGLE_API_KEY"] = 'AIzaSyAlBzc-Xypq5snm4F5pvkp9af6Oi4GMqZI'

model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)


# model = ChatGoogleGenerativeAI(model="gemini-pro")

class Event(BaseModel):
    meeting_name: str = Field(description="name of the meeting", )
    start_date: datetime.date = Field(description="date when the meeting should start")
    end_date: datetime.date = Field(description="date when the meeting should end")
    start_time: datetime.time = Field(description="time of when the meeting should start")
    end_time: datetime.time = Field(description="time of when the meeting should end")


# Set up a parser + inject instructions into the prompt template.
parser = JsonOutputParser(pydantic_object=Event)

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n If any details are missing in query, please respond with missing details",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


def query_llm(query: str):
    chain = prompt | model | parser
    return chain.invoke({"query": query})

# if __name__ == "__main__":
#     response = chain.invoke({"query": query})
