import asyncio
from pathlib import Path

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPImageSearchClient:
    def __init__(self):
        # Create server parameters for stdio connection
        self.server_params = StdioServerParameters(
            command="python",  # Executable
            args=["mcp-server/server.py"],  # Server script
            env=None,  # Optional environment variables
        )

    async def run(self):
        print("🚀 Starting MCP Python Client...")

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    print("📡 Connecting to MCP server...")

                    # Initialize the connection
                    await session.initialize()
                    print("✅ Connected to MCP server successfully!")

                    # List available tools
                    await self.list_tools(session)

                    # List and test resources
                    await self.list_and_test_resources(session)

                    print("\n✨ Client operations completed successfully!")

        except Exception as e:
            print(f"❌ Error running MCP client: {e}")
            raise

    async def list_tools(self, session: ClientSession):
        """List all available tools on the server."""
        print("\n📋 Listing available tools:")
        try:
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
        except Exception as e:
            print(f"  Error listing tools: {e}")

    async def list_and_test_resources(self, session: ClientSession):
        """List and test reading resources."""
        print("\n📄 Listing available resources:")
        try:
            resources = await session.list_resources()
            for resource in resources.resources:
                print(f"  - {resource.name}: {resource.description}")
                print(f"    URI: {resource.uri}")

            # Test reading a resource if available
            if resources.resources:
                first_resource = resources.resources[0]
                print(f"\n📖 Reading resource: {first_resource.name}")
                try:
                    content = await session.read_resource(first_resource.uri)
                    print(f"Resource content: {content}")
                except Exception as e:
                    print(f"  Error reading resource: {e}")
            else:
                print("  No resources available")

        except Exception as e:
            print(f"  Error listing resources: {e}")

    def extract_text_result(self, result) -> str:
        """Extract text content from a tool result object.

        This method attempts to extract the text content from the `content` attribute
        of the result object. If no text content is found, it falls back to converting
        the result to a string. If an error occurs during extraction, it returns "No result".

        Args:
            result: The result object returned by a tool, which may contain a `content` attribute
                    with text or other types of data.

        Returns:
            A string representing the extracted text content, or a fallback string if no text is found.
        """
        try:
            if hasattr(result, 'content') and result.content:
                for content_item in result.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        return content_item.text
                    elif hasattr(content_item, 'type') and content_item.type == "text":
                        return getattr(content_item, 'text', str(content_item))

            # Fallback: try to convert to string
            return str(result)
        except Exception:
            return "No result"

    async def fetch_metadata_with_agent(self, img_path: Path):
        # """Call the MCP tool and return a populated Metadata object."""
        # img_b64 = base64.b64encode(img_path.read_bytes()).decode()
        # response = client.call("search_image_metadata", image_b64=img_b64)
        # meta_dict = response["result"]          # plain dict from the server
        # return Metadata(**meta_dict)
        print(f"Fetching metadata for image: {img_path}")
        pass


async def main():
    """Entry point for the client."""
    client = MCPImageSearchClient()
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
