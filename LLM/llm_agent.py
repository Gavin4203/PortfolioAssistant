import ollama

from Functions.cover_letter import cv
from Functions.search import search_query

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage

import re
import json
import uuid

from .State import State

class agent:
    def __init__(self):
        self.model = "llama3.1:8b"
        self.system_instructions = (
            "You are an advanced AI career assistant. Your goal is to help the user with resumes and cover letters, "
            "making their real skills shine without fabricating experience.\n"
            "You have access to system tools. To understand how to use the tools, you must look into docstrings.\n"
            "You will call tools, you will not be returning JSON that is used in the tools"
        )
        self.tools = [cv.md_to_odt, search_query]
        self.llm = ChatOllama(
            model=self.model,
            temperature=0.1,
            num_ctx=8192,       #Prevents Ollama's default 2048 token wrap-around
            repeat_penalty=1.15 #Stops the model from looping on \n or repeated phrases
        )
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.app = self.compile_workflow()

    def compile_workflow(self):

        # ToolNode will automatically execute
        # any tools requested will append its results to the State
        tool_node = ToolNode(self.tools)

        # build the graph
        workflow = StateGraph(State)

        workflow.add_node("agent", self.agent_node)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "agent")

        workflow.add_conditional_edges("agent", tools_condition)

        workflow.add_edge("tools", "agent")

        return workflow.compile()


    def agent_node(self, state: State):
        """Calls the LLM with the current conversation history"""
        response = self.llm_with_tools.invoke(state["messages"])

        return {"messages": [response]}

    def speak_to_it(self, q):
        q_state = {
            "messages": [
                SystemMessage(content=self.system_instructions),
                HumanMessage(content=q),
            ]
        }

        for event in self.app.stream(q_state, stream_mode="values"):
            last_message = event["messages"][-1]
            # print the class name and its contents
            print(f"{last_message.__class__.__name__}")
            print(f"{last_message.content}\n")
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                print(f"  -> Agent decided to call: {last_message.tool_calls}\n")