from mcp.server.fastmcp import FastMCP
import navigator_mcp

def create_server():
    # Initialize FastMCP server safely inside a function wrapper
    mcp = FastMCP("CodeNavigator")

    # Expose your code functions explicitly as MCP tools
    mcp.tool()(navigator_mcp.list_code_files)
    mcp.tool()(navigator_mcp.read_multiple_files)
    mcp.tool()(navigator_mcp.write_doc_file)
    mcp.tool()(navigator_mcp.index_everything)
    mcp.tool()(navigator_mcp.ask_memory)
    mcp.tool()(navigator_mcp.apply_code_fix)
    mcp.tool()(navigator_mcp.web_search)
    mcp.tool()(navigator_mcp.capture_screen)
    mcp.tool()(navigator_mcp.create_new_file)
    
    return mcp

if __name__ == "__main__":
    server = create_server()
    server.run()