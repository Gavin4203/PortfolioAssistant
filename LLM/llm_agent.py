import ollama

from Functions.file_exporting import markdown_to_file
from Functions.search import search_query

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
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
        self.user_name = "Gavin Higgins"

        self.system_instructions = (
            f"You are an expert, supportive career assistant helping {self.user_name} land job roles.\n\n"
            "When calling a tool, do not use a preamble. Just call the tool directly.\n\n"
            "CORE WORKFLOW RULES:\n"
            f"1. FACTUAL GROUNDING: Always look up {self.user_name}'s actual background, skills, and work history first using `search_query` before answering specific job questions, drafting cover letters, or building resumes.\n"
            f"   - When calling `search_query`, pass ONLY general portfolio terms like 'software engineering projects and work history'. NEVER include the employer's industry (like loans, finance, or healthcare) in the search query.\n"
            "   - AUDIT YOUR CLAIMS: Before writing, verify that every skill or industry you claim is literally written in the returned portfolio data, not copied from your search query or the job posting.\n"
            "2. DIRECT TONE: Write in a clear, natural, impact-driven tone using complete, grammatically full sentences (convert any resume bullet fragments into full prose sentences).\n"
            "3. NO PLACEHOLDERS: Never output bracketed placeholders like [Company Name] or [Current Company].\n\n"
            "OUTPUT FORMAT ROUTING:\n"
            "- **General Questions / Job-Fit Ratings:** Reply normally in chat after searching.\n"
            "- **Cover Letters:** Wrap the ENTIRE cover letter inside `<cover_letter>` and `</cover_letter>` tags using this structure:\n"
            "  <cover_letter>\n"
            "  Dear Hiring Manager,\n\n"
            "  [Paragraph 1: Hook connecting the role and company to the candidate's core strengths]\n\n"
            "  [Paragraph 2: Highlight exactly ONE relevant project or role from the search results. Name the organization and detail the specific tech stack used there.]\n\n"
            "  [Paragraph 3: Highlight a SECOND distinct project or role. Focus on transferable skills and close the letter.]\n\n"
            "  Sincerely,\n\n"
            f"  {self.user_name}\n"
            "  </cover_letter>\n\n"
            "- **Resumes:** Whenever the user asks to make, tailor, create, or update a resume, wrap the ENTIRE resume inside `<resume>` and `</resume>` tags using clean Markdown.\n"
            "  - Resume Rules:\n"
            "    1. Only include a contact info line under the name if a real phone/email/URL is explicitly present in the search results. If no contact info is found, omit the contact line completely.\n"
            "    3. Under SKILLS, list ONLY tools explicitly written in the portfolio.\n"
            "  <resume>\n"
            f"  # {self.user_name}\n\n"
            "  ## EDUCATION\n"
            "  **[Degree and Minor]** | [University] | [Dates]\n\n"
            "  ## EXPERIENCE\n"
            "  ### [Role Title] | [Organization] | [Dates]\n\n"
            "  - [Action-verb bullet point 1]\n"
            "  - [Action-verb bullet point 2]\n\n"
            "  ## PROJECTS\n"
            "  ### [Project Name] | [Dates]\n\n"
            "  - [Action-verb bullet point 1]\n"
            "  - [Action-verb bullet point 2]\n"
            "  - **Tech Stack:** [Technologies from portfolio]\n\n"
            "  ## SKILLS\n"
            "  - **[Category]:** [Comma-separated verified skills]\n"
            "  </resume>"
        )

        self.tools = [search_query]
        self.llm = ChatOllama(
            model=self.model,
            temperature=0,
            num_ctx=8192,       #Prevents Ollama's default 2048 token wrap-around
        )

        self.app = self.compile_workflow()

    def compile_workflow(self):

        # ToolNode will automatically execute
        # any tools requested will append its results to the State
        tool_node = ToolNode(self.tools)

        # give persistent memory
        memory = MemorySaver()

        # build the graph
        workflow = StateGraph(State)

        workflow.add_node("agent", self.agent_node)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "agent")

        workflow.add_conditional_edges("agent", tools_condition)

        workflow.add_edge("tools", "agent")

        return workflow.compile(checkpointer=memory)


    def agent_node(self, state: State):
        """Calls the LLM with the current conversation history and enforces tool ordering"""
        messages = state["messages"]

        # 1. Find messages generated after the most recent user prompt
        recent_messages = []
        for msg in reversed(messages):
            if msg.type == "human":
                break
            recent_messages.append(msg)

        # 2. Check if 'search_query' has succeeded this turn
        has_searched_this_turn = any(
            msg.type == "tool"
            and getattr(msg, "name", "") == "search_query"
            and not str(msg.content).startswith("Error")
            for msg in recent_messages
        )

        # 3. Bind search_query on Turn 1; unbind all tools on Turn 2+
        sys_msg = SystemMessage(content=self.system_instructions)
        if not has_searched_this_turn:
            active_llm = self.llm.bind_tools([search_query])
            response = active_llm.invoke([sys_msg] + messages)
        else:
            latest_user_request = next(
                (msg.content for msg in reversed(messages) if msg.type == "human"), ""
            )

            anchor_message = HumanMessage(
                content=(
                    f"REMINDER OF CURRENT USER REQUEST:\n{latest_user_request}\n\n"
                    "CRITICAL CHECKS BEFORE WRITING:\n"
                    "1. Keep each project and role from the portfolio separate—do not mix details or tech stacks between records.\n"
                    "2. Never copy HR boilerplate phrases like 'one or more programming languages and related tools' from the job description.\n"
                    "3. Do not use the pronoun 'I' or 'Our' in resume descriptions.\n"
                    "4. WRAP YOUR RESPONSE IN TAGS.\n"
                    "5. FOR RESUMES ONLY, Format EVERY description under EXPERIENCE and PROJECTS as a bulleted list starting with a dash ('- '). Do not write flat paragraphs."
                    "6. REMEMBER TO AUDIT YOUR CLAIMS"
                )
            )
            # Zero tools bound = Zero JSON risk! Pure prose generation.
            response = self.llm.invoke([sys_msg] + messages + [anchor_message])

            # 4. Deterministic Python Post-Processor for Cover Letters
            content = response.content
            cover_letter_match = re.search(
                r"<cover_letter>(.*?)</cover_letter>",
                content,
                flags=re.DOTALL | re.IGNORECASE,
            )

            resume_match = re.search(
                r"<resume>(.*?)</resume>",
                content,
                flags=re.DOTALL | re.IGNORECASE,
            )

            if cover_letter_match:
                letter_text = cover_letter_match.group(1).strip()
                markdown_to_file.export(letter_text, "cover_letter")
                response.content = f"{letter_text}"
            elif resume_match:
                resume_text = resume_match.group(1).strip()
                markdown_to_file.export(resume_text, "resume")
                response.content = f"{resume_text}"
            elif "dear " in content.lower() and "sincerely" in content.lower():
                # Fallback: If the LLM rewrote the letter but forgot <cover_letter> tags, catch it anyway!
                save_status = markdown_to_file.export(content, "cover_letter")
                response.content = f"{content}\n\n[{save_status}]"

        return {"messages": [response]}

    def speak_to_it(self, q, thread_id: str = "current_session"):
        config = {"configurable": {"thread_id": thread_id}}
        q_state = {
            "messages": [
                HumanMessage(content=q),
            ]
        }

        for event in self.app.stream(q_state, config=config, stream_mode="values"):
            last_message = event["messages"][-1]
            # print the class name and its contents
            print(f"{last_message.__class__.__name__}")
            print(f"{last_message.content}\n")
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                print(f"  -> Agent decided to call: {last_message.tool_calls}\n")