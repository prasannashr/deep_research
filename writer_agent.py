from pydantic import BaseModel, Field
from agents import Agent

from model_utils import create_model_from_env

MODEL_NAME = create_model_from_env()

INSTRUCTIONS = """
You are a senior researcher tasked with writing a cohesive report for a research query.
You will be provided with the original query, and some research.
Generate a comprehensive report based on the research and the query.
Return only a valid JSON object matching the requested output schema. Do not use a
Markdown code fence and do not include any text before or after the JSON object.
The markdown_report field should contain a detailed report of approximately 800-1200 words.
"""


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


writer_agent = Agent(name="Writer Agent", instructions=INSTRUCTIONS, model=MODEL_NAME, output_type=ReportData)
