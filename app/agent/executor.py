from app.agent.plan_models import ToolResult


class Executor:

    def __init__(self, tools):
        self.tools = tools

    def execute(self, step):

        tool = self.tools.get(step.tool)

        if tool is None:
            return ToolResult(
                success=False,
                error=f"Unknown tool: {step.tool}"
            )

        try:
            result = tool(**step.args)

            return ToolResult(
                success=True,
                data=result
            )

        except Exception as ex:

            return ToolResult(
                success=False,
                error=str(ex)
            )