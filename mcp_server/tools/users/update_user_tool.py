from typing import Any

from mcp_server.models.user_info import UserUpdate
from mcp_server.tools.users.base import BaseUserServiceTool


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "update_user"

    @property
    def description(self) -> str:
        return "Updates an existing user's information in the User Management System based on the provided user ID and new details."

    @property
    def input_schema(self) -> dict[str, Any]:
        # Provide tool params Schema:
        # - id: number, required, User ID that should be updated.
        # - new_info: UserUpdate.model_json_schema()
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "The unique identifier of the user to be updated."
                },
                "new_info": UserUpdate.model_json_schema()
            },
            "required": ["id", "new_info"]
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        # 1. Get user `id` from `arguments`
        user_id = arguments["id"]
        # 2. Get `new_info` from `arguments` and create `UserUpdate` via pydentic `UserUpdate.model_validate`
        user = UserUpdate.model_validate(arguments["new_info"])
        # 3. Call user_client update_user and return its results (it is async, don't forget to await)
        return await self._user_client.update_user(user_id, user)