from app.agent.planner import Planner
from app.agent.executor import Executor


class AgentService:
    def __init__(self, tools):
        self.planner = Planner()
        self.executor = Executor(tools)

    def _update_context(self, context, step_name, result_data):
        context[step_name] = result_data

        patient = result_data.get("patient")
        if patient:
            context["patient_id"] = patient.get("patient_id")
            context["email"] = patient.get("email")
            context["phone"] = patient.get("phone")

        slots = result_data.get("slots")
        if slots:
            context["selected_slot"] = slots[0]
            context["slot_id"] = context["selected_slot"]["slot_id"]

        appointment = result_data.get("appointment")
        if appointment:
            context["appointment_id"] = appointment.get("appointment_id")


    def _fill_args_from_context(self, step, context):
        if step.tool == "schedule_appointment":
            step.args.setdefault("patient_id", context.get("patient_id"))
            step.args.setdefault("slot_id", context.get("slot_id"))
            selected_slot = context.get("selected_slot") or {}
            step.args.setdefault("provider", selected_slot.get("provider", ""))
            step.args.setdefault("specialty", selected_slot.get("specialty", ""))
            step.args.setdefault("start_time", selected_slot.get("start_time", ""))
            step.args.setdefault("location", selected_slot.get("location", ""))

        if step.tool == "list_patient_appointments":
            step.args.setdefault("patient_id", context.get("patient_id"))

        if step.tool == "send_confirmation":
            step.args.setdefault("patient_id", context.get("patient_id"))
            step.args.setdefault("appointment_id", context.get("appointment_id"))
            step.args.setdefault("email", context.get("email", ""))
            step.args.setdefault("phone", context.get("phone", ""))

    def _format_appointment(self, appointment):
        appointment_id = appointment.get("appointment_id", "")
        status = appointment.get("status", "")
        start_time = appointment.get("start_time") or "time not stored"
        provider = appointment.get("provider") or "provider not stored"
        location = appointment.get("location") or "location not stored"
        reason = appointment.get("reason") or "No reason provided"

        return (
            f"{appointment_id}: {status} with {provider} at {location} "
            f"on {start_time}. Reason: {reason}."
        )

    def _build_response(self, execution_log):
        if not execution_log:
            return "No steps were executed.", {}

        last_result = execution_log[-1]["result"]
        data = last_result.get("data") or {}

        appointments = data.get("appointments")
        if appointments is not None:
            if not appointments:
                return "I couldn't find any appointments for that patient.", {
                    "appointments": []
                }

            lines = [self._format_appointment(item) for item in appointments]
            return "Here are the patient's appointments:\n" + "\n".join(lines), {
                "appointments": appointments
            }

        appointment = data.get("appointment")
        if appointment:
            return self._format_appointment(appointment), {
                "appointment": appointment
            }

        return "The workflow completed successfully.", {}

    def run(self, user_message):
        plan = self.planner.create_plan(user_message)
        execution_log = []
        context = {}

        for step in plan.steps:
            if step.tool == "ask_user":
                return {
                    "status": "need_more_info",
                    "response": step.reason,
                    "message": step.reason,
                    "plan": plan.model_dump(),
                    "execution_log": execution_log
                }
            self._fill_args_from_context(step, context)
            result = self.executor.execute(step)

            execution_log.append({
                "step": step.model_dump(),
                "result": result.model_dump()
            })

            if not result.success:
                revised_plan = self.planner.replan(
                    user_message=user_message,
                    plan=plan,
                    failed_step=step.name,
                    error=result.error
                )

                return {
                    "status": "replanned",
                    "response": f"I hit an issue and created a revised plan: {result.error}",
                    "error": result.error,
                    "original_plan": plan.model_dump(),
                    "revised_plan": revised_plan.model_dump(),
                    "execution_log": execution_log
                }
            self._update_context(context, step.name, result.data or {})

        response, payload = self._build_response(execution_log)

        return {
            "status": "completed",
            "response": response,
            **payload,
            "plan": plan.model_dump(),
            "execution_log": execution_log
        }
