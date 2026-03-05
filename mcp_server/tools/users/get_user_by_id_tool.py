from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class GetUserByIdTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "get_user_by_id"

    @property
    def description(self) -> str:
        return "Retrieves detailed information about a user from the User Management System by user_id."

    @property
    def input_schema(self) -> dict[str, Any]:
        # Provide tool params Schema. This tool applies user `id` (number) as a parameter and it is required
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The unique identifier of the user to retrieve."
                }
            },
            "required": ["id"]
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        # 1. Get int `id` from arguments
        # 2. Call user_client get_user and return its results (it is async, don't forget to await)
        user_id = arguments["id"]
        return await self._user_client.get_user(user_id)