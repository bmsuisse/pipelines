from typing import List, Union, Generator, Iterator, Optional, AsyncGenerator
from pydantic import BaseModel
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.string import StrOutputParser
import logging
from pprint import pprint

logger = logging.getLogger(__name__)


class Pipeline:
    class Valves(BaseModel):
        OPENAI_API_KEY: str

    def __init__(self):
        self.debug = False
        self.name = "Langchain Pipeline"
        self.valves = self.Valves(**{"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "mykey")})


    async def on_startup(self):
        print(f"on_startup:{__name__}")
        os.environ["OPENAI_API_KEY"] = self.valves.OPENAI_API_KEY


    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")


    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called before the OpenAI API request is made. You can modify the form data before it is sent to the OpenAI API.
        print(f"inlet: {__name__}")
        if self.debug:
            print(f"inlet: {__name__} - body:")
            pprint(body)
            print(f"inlet: {__name__} - user:")
            pprint(user)
        return body


    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called after the OpenAI API response is completed. You can modify the messages after they are received from the OpenAI API.
        print(f"outlet: {__name__}")
        if self.debug:
            print(f"outlet: {__name__} - body:")
            pprint(body)
            print(f"outlet: {__name__} - user:")
            pprint(user)
        return body


    async def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous pipe function that streams responses
        """
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True,)
        prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}. Also explain me why it is funny in detail.")
        chain = prompt | llm | StrOutputParser()
        
        return chain.astream({"topic": user_message})
