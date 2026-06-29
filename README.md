# Patient Engagement AI Planning Agent

An autonomous healthcare workflow agent built with **Python**, **Flask**, **LangChain**, and **OpenAI**.

Unlike traditional chatbots that execute a single tool call, this project demonstrates an **Agent Planning** architecture that reasons about a user's goal, generates an execution plan, invokes multiple backend tools, and dynamically replans when failures occur.

---

## Features

- AI Planner that converts user goals into executable workflows
- Multi-step execution engine
- Dynamic replanning on failures
- Tool registry for extensible backend tools
- Patient registration workflow
- Appointment scheduling workflow
- Patient validation
- Notification service
- Business rule enforcement
- Flask REST API

---

## Architecture

```
                User Request
                     │
                     ▼
              Planner (LLM)
                     │
             Execution Plan
                     │
                     ▼
             Execution Engine
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 Patient Tools  Appointment Tools  Notification Tools
                     │
                     ▼
              Business Logic
                     │
                     ▼
          Store / Database Layer
```

---

## Project Structure

```
PatientEngagement-AI-Agent/

app/
│
├── agent/
│   ├── planner.py
│   ├── executor.py
│   ├── agent_service.py
│   └── plan_models.py
│
├── tools/
│   ├── patient_tools.py
│   ├── appointment_tools.py
│   ├── notification_tools.py
│   └── tool_registry.py
│
├── schemas/
│   ├── patient_schema.py
│   ├── appointment_schema.py
│   └── notification_schema.py
│
├── prompts/
│
└── app.py

config.py
store.py
requirements.txt
README.md
```

---

## Example Workflow

User:

> Register me and schedule a primary care appointment next week after 5 PM.

The planner generates:

1. Validate patient
2. Search existing patient
3. Register patient (if needed)
4. Find appointment slots
5. Schedule appointment
6. Send confirmation

Each step is executed independently by the execution engine.

If any step fails, the planner automatically creates a revised plan.

---

## Planner

The planner is responsible for:

- Understanding user intent
- Creating execution plans
- Selecting backend tools
- Respecting business rules
- Requesting missing information
- Replanning after failures

Example plan:

```json
{
  "goal": "Register patient and schedule appointment",
  "steps": [
    {
      "tool": "validate_patient"
    },
    {
      "tool": "search_patient"
    },
    {
      "tool": "register_patient"
    },
    {
      "tool": "find_appointments"
    },
    {
      "tool": "schedule_appointment"
    },
    {
      "tool": "send_confirmation"
    }
  ]
}
```

---

## Execution Engine

The execution engine:

- Executes one tool at a time
- Collects execution results
- Maintains workflow context
- Propagates outputs to downstream steps
- Triggers replanning when necessary

---

## Current Tools

### Patient

- validate_patient
- search_patient
- register_patient
- update_patient

### Appointment

- find_appointments
- schedule_appointment
- list_patient_appointments
- cancel_appointment

### Notification

- send_confirmation

---

## Business Rules

The agent enforces several healthcare-specific rules:

- Washington residents only
- Patients must be at least 18 years old
- Existing patients are searched before registration
- Patient validation occurs before registration
- Appointment availability is checked before scheduling
- Sensitive operations require explicit user input

---

## Technologies

- Python
- Flask
- LangChain
- OpenAI GPT-4o
- Pydantic
- REST APIs

---

## Future Enhancements

- Long-term agent memory
- Reflection and self-correction
- Human approval workflow
- Multi-agent collaboration
- Conversation history
- Observability and tracing
- MCP tool integration
- Authentication and authorization

---

## Running

Install dependencies

```bash
pip install -r requirements.txt
```

Start the server

```bash
python app.py
```

Example request

```bash
curl -X POST http://127.0.0.1:5050/agent/chat \
-H "Content-Type: application/json" \
-d '{
  "message":"My name is John Smith, my DOB is 01/01/1980, I live in WA, my email is john@example.com, my phone is 2065551111. Register me and schedule a primary care appointment next week after 5 PM."
}'
```

Example output
```json
{
  "execution_log": [
    {
      "result": {
        "data": {
          "age": 46,
          "state": "WA",
          "valid": true
        },
        "error": null,
        "success": true
      },
      "step": {
        "args": {
          "dob": "01/01/1980",
          "full_name": "John Smith",
          "state": "WA"
        },
        "name": "Validate Patient",
        "reason": "To ensure the patient's information is valid and meets the requirements.",
        "status": "pending",
        "tool": "validate_patient"
      }
    },
    {
      "result": {
        "data": {
          "found": false,
          "patient": null
        },
        "error": null,
        "success": true
      },
      "step": {
        "args": {
          "dob": "01/01/1980",
          "full_name": "John Smith"
        },
        "name": "Search Patient",
        "reason": "To check if the patient is already registered.",
        "status": "pending",
        "tool": "search_patient"
      }
    },
    {
      "result": {
        "data": {
          "available": true,
          "slots": [
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-1-1",
              "specialty": "primary care",
              "start_time": "2026-06-29T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-1-2",
              "specialty": "primary care",
              "start_time": "2026-06-29T18:00:00"
            },
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-2-1",
              "specialty": "primary care",
              "start_time": "2026-06-30T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-2-2",
              "specialty": "primary care",
              "start_time": "2026-06-30T18:00:00"
            },
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-3-1",
              "specialty": "primary care",
              "start_time": "2026-07-01T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-3-2",
              "specialty": "primary care",
              "start_time": "2026-07-01T18:00:00"
            },
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-4-1",
              "specialty": "primary care",
              "start_time": "2026-07-02T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-4-2",
              "specialty": "primary care",
              "start_time": "2026-07-02T18:00:00"
            },
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-5-1",
              "specialty": "primary care",
              "start_time": "2026-07-03T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-5-2",
              "specialty": "primary care",
              "start_time": "2026-07-03T18:00:00"
            },
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-6-1",
              "specialty": "primary care",
              "start_time": "2026-07-04T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-6-2",
              "specialty": "primary care",
              "start_time": "2026-07-04T18:00:00"
            },
            {
              "location": "Seattle Clinic",
              "provider": "Dr. Smith",
              "slot_id": "SLOT-7-1",
              "specialty": "primary care",
              "start_time": "2026-07-05T17:30:00"
            },
            {
              "location": "Bellevue Clinic",
              "provider": "Dr. Lee",
              "slot_id": "SLOT-7-2",
              "specialty": "primary care",
              "start_time": "2026-07-05T18:00:00"
            }
          ]
        },
        "error": null,
        "success": true
      },
      "step": {
        "args": {
          "days_ahead": 7,
          "specialty": "primary care"
        },
        "name": "Find Appointments",
        "reason": "To find available primary care appointment slots for next week.",
        "status": "pending",
        "tool": "find_appointments"
      }
    },
    {
      "result": {
        "data": {
          "created": true,
          "patient": {
            "dob": "01/01/1980",
            "email": "john@example.com",
            "full_name": "John Smith",
            "patient_id": "PAT-00001",
            "phone": "2065551111",
            "state": "WA"
          }
        },
        "error": null,
        "success": true
      },
      "step": {
        "args": {
          "dob": "01/01/1980",
          "email": "john@example.com",
          "full_name": "John Smith",
          "phone": "2065551111",
          "state": "WA"
        },
        "name": "Register Patient",
        "reason": "To register the patient since they are not found in the system.",
        "status": "pending",
        "tool": "register_patient"
      }
    },
    {
      "result": {
        "data": {
          "appointment": {
            "appointment_id": "APT-00001",
            "patient_id": "PAT-00001",
            "reason": "General appointment",
            "slot_id": "SLOT-1-1",
            "status": "scheduled"
          },
          "scheduled": true
        },
        "error": null,
        "success": true
      },
      "step": {
        "args": {
          "patient_id": "PAT-00001",
          "slot_id": "SLOT-1-1"
        },
        "name": "Schedule Appointment",
        "reason": "To schedule a primary care appointment for the patient.",
        "status": "pending",
        "tool": "schedule_appointment"
      }
    }
  ],
  "plan": {
    "goal": "Register John Smith and schedule a primary care appointment",
    "steps": [
      {
        "args": {
          "dob": "01/01/1980",
          "full_name": "John Smith",
          "state": "WA"
        },
        "name": "Validate Patient",
        "reason": "To ensure the patient's information is valid and meets the requirements.",
        "status": "pending",
        "tool": "validate_patient"
      },
      {
        "args": {
          "dob": "01/01/1980",
          "full_name": "John Smith"
        },
        "name": "Search Patient",
        "reason": "To check if the patient is already registered.",
        "status": "pending",
        "tool": "search_patient"
      },
      {
        "args": {
          "days_ahead": 7,
          "specialty": "primary care"
        },
        "name": "Find Appointments",
        "reason": "To find available primary care appointment slots for next week.",
        "status": "pending",
        "tool": "find_appointments"
      },
      {
        "args": {
          "dob": "01/01/1980",
          "email": "john@example.com",
          "full_name": "John Smith",
          "phone": "2065551111",
          "state": "WA"
        },
        "name": "Register Patient",
        "reason": "To register the patient since they are not found in the system.",
        "status": "pending",
        "tool": "register_patient"
      },
      {
        "args": {
          "patient_id": "PAT-00001",
          "slot_id": "SLOT-1-1"
        },
        "name": "Schedule Appointment",
        "reason": "To schedule a primary care appointment for the patient.",
        "status": "pending",
        "tool": "schedule_appointment"
      }
    ]
  },
  "status": "completed"
}

```

---

## Why This Project?

Most AI chatbot projects demonstrate a single LLM response or a single tool invocation.

This project focuses on **Agentic AI**, where an LLM reasons about a user's goal, creates an execution plan, orchestrates multiple backend services, and adapts dynamically when the workflow changes. This architecture more closely resembles production AI systems used for enterprise workflow automation than a traditional chatbot.
