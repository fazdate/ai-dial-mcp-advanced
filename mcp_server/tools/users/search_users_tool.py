from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        return "Searches for users in the User Management System based on provided criteria such as name, surname, email, and gender."

    @property
    def input_schema(self) -> dict[str, Any]:
        # Provide tool params Schema:
        # - name: str
        # - surname: str
        # - email: str
        # - gender: str
        # None of them are required (see UserClient.search_users method)
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The first name of the user to search for."
                },
                "surname": {
                    "type": "string",
                    "description": "The last name of the user to search for."
                },
                "email": {
                    "type": "string",
                    "description": "The email address of the user to search for."
                },
                "gender": {
                    "type": "string",
                    "description": "The gender of the user to search for."
                }
            },
            "required": []
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        # Call user_client search_users (with `**arguments`) and return its results (it is async, don't forget to await)
        return await self._user_client.search_users(**arguments)