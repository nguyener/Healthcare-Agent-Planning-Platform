import json
from langchain_openai import ChatOpenAI
from app.agent.plan_models import AgentPlan


class Planner:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def create_plan(self, user_message: str) -> AgentPlan:
        prompt = f"""
You are a healthcare workflow planning agent.

Return ONLY valid JSON. No markdown. No explanation.

Available tools and exact argument contracts:

validate_patient:
{{
  "full_name": "string",
  "dob": "MM/DD/YYYY",
  "state": "WA"
}}

search_patient:
{{
  "full_name": "string",
  "dob": "MM/DD/YYYY"
}}

register_patient:
{{
  "full_name": "string",
  "dob": "MM/DD/YYYY",
  "phone": "string",
  "email": "string",
  "state": "WA"
}}

update_patient:
{{
  "patient_id": "string",
  "phone": "string",
  "email": "string",
  "state": "WA"
}}

find_appointments:
{{
  "specialty": "primary care",
  "days_ahead": 7
}}

schedule_appointment:
{{
  "patient_id": "value returned from search_patient or register_patient",
  "slot_id": "value returned from find_appointments",
  "reason": "string"
}}

cancel_appointment:
{{
  "appointment_id": "string"
}}

send_confirmation:
{{
  "patient_id": "string",
  "appointment_id": "string",
  "email": "string",
  "phone": "string",
  "message": "string"
}}

ask_user:
{{
  "message": "question to ask user"
}}

Rules:
- Use ONLY the tool names listed above.
- Use ONLY the exact argument names shown above.
- Use full_name, never name.
- Use state, never address.
- Use slot_id, never appointment_time.
- Use patient_id, never patient_name.
- Use dob format MM/DD/YYYY.
- Always validate_patient before register_patient.
- Always search_patient before register_patient.
- For scheduling, always call find_appointments before schedule_appointment.
- Do not invent placeholder values like "available_time_from_find_appointments".
- If patient_id or slot_id must come from a previous step, leave it out of args. The executor will fill it from context.
- Only use ask_user when required information is missing.
- If ask_user is needed, it must be the first and only step.
- Do not insert ask_user in the middle of a plan.
- Patient must be over 18.
- Patient must live in WA.
- Do not delete patient records.

JSON format:
{{
  "goal": "short goal",
  "steps": [
    {{
      "name": "short_step_name",
      "tool": "tool_name",
      "reason": "why this step is needed",
      "args": {{}}
    }}
  ]
}}

User request:
{user_message}
"""
        response = self.llm.invoke(prompt)
        data = json.loads(response.content)
        return AgentPlan(**data)

    def replan(self, user_message: str, plan: AgentPlan, failed_step: str, error: str) -> AgentPlan:
        prompt = f"""
Return ONLY valid JSON. No markdown.

The previous plan failed.

User request:
{user_message}

Previous plan:
{plan.model_dump()}

Failed step:
{failed_step}

Error:
{error}

Use this JSON format:
{{
  "goal": "short goal",
  "steps": [
    {{
      "name": "step name",
      "tool": "tool name",
      "reason": "why this step is needed",
      "args": {{}}
    }}
  ]
}}
"""
        response = self.llm.invoke(prompt)
        data = json.loads(response.content)
        return AgentPlan(**data)