import asyncio
import os
import warnings
import io
import contextlib

from agent.clients.custom_mcp_client import CustomMCPClient
from agent.clients.mcp_client import MCPClient
from agent.clients.dial_client import DialClient
from agent.models.message import Message, Role

# Suppress asyncgen cleanup warnings that occur when MCP connections fail
warnings.filterwarnings("ignore", message=".*asynchronous generator.*", category=RuntimeWarning)


async def main():
    # 1. DialClient handles AI model interactions and integrates with MCP clients
    # 2. Create empty list to save tools from MCP Servers
    tools: list[dict] = []

    # 3. Create empty dict where key is tool name and value is MCPClient or CustomMCPClient instance
    tool_name_client_map: dict[str, MCPClient | CustomMCPClient] = {}

    # 4. Create UMS MCPClient with URL http://localhost:8006/mcp
    try:
        print("Connecting to UMS MCP server...")
        ums_client = await MCPClient.create("http://localhost:8006/mcp")
        ums_tools = await ums_client.get_tools()
        tools.extend(ums_tools)
        for tool in ums_tools:
            tool_name_client_map[tool["function"]["name"]] = ums_client
        print(f"✓ Connected to UMS server. Found {len(ums_tools)} tools.")
    except BaseException as e:
        # Catch all exceptions including BaseExceptionGroup
        if type(e).__name__ == 'BaseExceptionGroup':
            print(f"✗ Failed to connect to UMS MCP server: Connection error")
        else:
            print(f"✗ Failed to connect to UMS MCP server: {type(e).__name__}: {e}")

    # 5. Collect tools and dict is already done in step 4

    # 6. Do steps 4 and 5 for remote MCP server
    remote_client = None
    try:
        print("Connecting to remote MCP server...")
        remote_client = await CustomMCPClient.create("https://remote.mcpservers.org/fetch/mcp")
        remote_tools = await remote_client.get_tools()
        tools.extend(remote_tools)
        for tool in remote_tools:
            tool_name_client_map[tool["function"]["name"]] = remote_client
        print(f"✓ Connected to remote server. Found {len(remote_tools)} tools.")
    except BaseException as e:
        # Catch all exceptions including BaseExceptionGroup
        if remote_client:
            await remote_client.disconnect()
        if type(e).__name__ == 'BaseExceptionGroup':
            print(f"✗ Failed to connect to remote MCP server: Connection error")
        else:
            print(f"✗ Failed to connect to remote MCP server: {type(e).__name__}: {e}")

    # Check if any tools were found
    if not tools:
        print("\n✗ No MCP servers available. Please ensure at least one server is running.")
        print("   - UMS MCP server should be running on http://localhost:8006/mcp")
        print("   - Or configure the remote MCP server endpoint")
        return

    print(f"\n✓ Total tools available: {len(tools)}\n")

    # 7. Create DialClient with endpoint
    api_key = os.getenv('DIAL_API_KEY', '')
    dial_client = DialClient(
        api_key=api_key,
        endpoint="https://ai-proxy.lab.epam.com",
        tools=tools,
        tool_name_client_map=tool_name_client_map
    )

    # 8. Create array with Messages and add System message with instructions
    messages: list[Message] = [
        Message(
            role=Role.SYSTEM,
            content="You are a helpful assistant. Use the available tools to help handle user requests. "
                   "When asked to search for information about a person, use the search_users tool. "
                   "If the user asks about checking if a person exists as a user, search for them and create them if needed using the create_user tool."
        )
    ]

    # 9. Create simple console chat
    print("💬 Welcome to the MCP Agent Chat! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add user message to history
        messages.append(Message(role=Role.USER, content=user_input))

        # Get AI response
        ai_response = await dial_client.get_completion(messages)

        # Add AI response to history
        messages.append(ai_response)

if __name__ == "__main__":
    # Suppress stderr during asyncio.run() cleanup to avoid showing MCP library's internal cleanup errors
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            asyncio.run(main())
    except Exception as e:
        # Re-raise if it's not an MCP-related cleanup error
        if "Attempted to exit cancel scope" not in str(e) and "asynchronous generator" not in str(e):
            raise


# Check if Arkadiy Dobkin present as a user, if not then search info about him in the web and add him