
from typing import Any

from mcp_server.models.user_info import UserCreate
from mcp_server.tools.users.base import BaseUserServiceTool


class CreateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "add_user"

    @property
    def description(self) -> str:
        return "Creates a new user in the User Management System with the provided details."

    @property
    def input_schema(self) -> dict[str, Any]:
        return UserCreate.model_json_schema()

    async def execute(self, arguments: dict[str, Any]) -> str:
        # 1. Validate arguments with `UserCreate.model_validate`
        # 2. Call user_client add user and return its results (it is async, don't forget to await)
        user_create = UserCreate.model_validate(arguments)
        return await self._user_client.add_user(user_create)
