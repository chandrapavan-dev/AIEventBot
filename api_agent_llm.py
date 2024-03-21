import datetime
import json
import os
from typing import Type, Optional

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

# set_debug(True)

os.environ["OPENAI_API_KEY"] = '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'


# os.environ["GOOGLE_API_KEY"] = 'AIzaSyAlBzc-Xypq5snm4F5pvkp9af6Oi4GMqZI'


class EventInput(BaseModel):
    meeting_name: str = Field(description="name of the meeting")
    start_date: datetime.date = Field(description="date when the meeting should start")
    end_date: datetime.date = Field(description="date when the meeting should end")
    start_time: datetime.time = Field(description="time of when the meeting should start")
    end_time: datetime.time = Field(description="time of when the meeting should end")


class EventOutput(EventInput):
    output: str = Field(description="status of the event")


def parse(output):
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the Response function was invoked, return to the user with the function inputs
    if name == "Response":
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )


class CustomEventCreatorTool(BaseTool):
    name = "custom-event-creator-tool"
    description = "used for creating events in a online calendar"
    args_schema: Type[BaseModel] = EventInput

    def _run(
            self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        print(query)
        # TODO add code and validation to direct to create event function of a calender
        return "Event created Successfully"

    async def _arun(
            self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom-event-creator-tool does not support async yet")


if __name__ == "__main__":
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    # llm = ChatGoogleGenerativeAI(model="gemini-pro")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm_with_tools = llm.bind_functions([CustomEventCreatorTool, EventInput])

    tools = [CustomEventCreatorTool]

    agent = (
            {
                "input": lambda x: x["input"],
                # Format agent scratchpad from intermediate steps
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)

    query = "Create a meeting on 12th Jan 2024 from 10 pm to 11 pm on meeting topic Studing Gen AI "

    agent_executor.invoke(
        {"input": query},
        return_only_outputs=True,
    )
