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
            context["slot_id"] = slots[0]["slot_id"]

        appointment = result_data.get("appointment")
        if appointment:
            context["appointment_id"] = appointment.get("appointment_id")


    def _fill_args_from_context(self, step, context):
        if step.tool == "schedule_appointment":
            step.args.setdefault("patient_id", context.get("patient_id"))
            step.args.setdefault("slot_id", context.get("slot_id"))

        if step.tool == "send_confirmation":
            step.args.setdefault("patient_id", context.get("patient_id"))
            step.args.setdefault("appointment_id", context.get("appointment_id"))
            step.args.setdefault("email", context.get("email", ""))
            step.args.setdefault("phone", context.get("phone", ""))

    def run(self, user_message):
        plan = self.planner.create_plan(user_message)
        execution_log = []
        context = {}

        for step in plan.steps:
            if step.tool == "ask_user":
                return {
                    "status": "need_more_info",
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
                    "error": result.error,
                    "original_plan": plan.model_dump(),
                    "revised_plan": revised_plan.model_dump(),
                    "execution_log": execution_log
                }
            self._update_context(context, step.name, result.data or {})

        return {
            "status": "completed",
            "plan": plan.model_dump(),
            "execution_log": execution_log
        }