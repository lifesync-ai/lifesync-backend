# ai_planner/src/agents/parser.py
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. Define the schema we want the LLM to extract
class TargetEvent(BaseModel):
    activity: str = Field(..., description="The name of the activity, e.g., 'running', 'breakfast'")
    target_time: str = Field(..., description="The time mentioned in HH:MM format, e.g., '09:00', '11:00'")
    details: Optional[str] = Field(None, description="Any specific details, e.g., 'syrnyky'")

class ExtractedGoals(BaseModel):
    events: List[TargetEvent] = Field(..., description="List of all extracted activities")

# 2. Set up the LangChain parser & prompt with a concrete 1-shot example
parser = JsonOutputParser(pydantic_object=ExtractedGoals)

prompt_template = PromptTemplate(
    template="""You are a precise information extraction assistant. 
Your job is to parse the user's request and extract scheduling goals into JSON.

User Request: {user_query}

{format_instructions}

Example of expected output structure:
{{
  "events": [
    {{
      "activity": "run",
      "target_time": "09:00",
      "details": "outdoor"
    }},
    {{
      "activity": "breakfast",
      "target_time": "11:00",
      "details": "syrnyky"
    }}
  ]
}}

Return ONLY valid JSON matching the schema. Do not write any conversational intro or outro text.
""",
    input_variables=["user_query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 3. Define the runner function with defensive parsing
def extract_schedule_goals(raw_text: str) -> ExtractedGoals:
    llm = OllamaLLM(model="llama3", temperature=0.0)
    chain = prompt_template | llm | parser
    
    result = chain.invoke({"user_query": raw_text})
    
    # Normalizing step to handle minor LLM JSON structural deviations
    normalized_events = []
    
    # Extract the raw list of events regardless of how the LLM nested it
    raw_list = []
    if isinstance(result, list):
        raw_list = result
    elif isinstance(result, dict):
        raw_list = result.get("events", [])
        if not raw_list and "activity" in result:
            # The LLM returned a single event dictionary instead of a list
            raw_list = [result]

    # Map the extracted keys defensively to the exact fields Pydantic expects
    for item in raw_list:
        if not isinstance(item, dict):
            continue
            
        # Extract fields with loose fallbacks for different naming styles
        activity = item.get("activity") or item.get("activity_name") or item.get("task") or "Unknown"
        target_time = item.get("target_time") or item.get("time") or "00:00"
        details = item.get("details") or item.get("description")
        
        normalized_events.append(
            TargetEvent(
                activity=str(activity),
                target_time=str(target_time),
                details=str(details) if details else None
            )
        )
        
    return ExtractedGoals(events=normalized_events)