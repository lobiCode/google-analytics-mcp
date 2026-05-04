#!/usr/bin/env python

# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entry point for the Google Analytics MCP server."""

import argparse
import asyncio
import os

import analytics_mcp.coordinator as coordinator
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server
import mcp.server.stdio
from mcp.server.streamable_http import streamable_http_server


def _init_options():
    return InitializationOptions(
        server_name=coordinator.app.name,
        server_version="1.0.0",
        capabilities=coordinator.app.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )


async def run_stdio_async():
    """Runs the MCP server over standard I/O."""
    print("Starting MCP Stdio Server:", coordinator.app.name)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await coordinator.app.run(read_stream, write_stream, _init_options())


async def run_streamable_http_async(host: str, port: int):
    """Runs the MCP server over streamable HTTP."""
    print(f"Starting MCP Streamable HTTP Server: {coordinator.app.name} on {host}:{port}")
    async with streamable_http_server(host=host, port=port) as (read_stream, write_stream):
        await coordinator.app.run(read_stream, write_stream, _init_options())


def run_server():
    """Synchronous wrapper to run the async MCP server."""
    parser = argparse.ArgumentParser(description="Google Analytics MCP Server")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "9003")))
    args = parser.parse_args()

    if args.transport == "streamable-http":
        asyncio.run(run_streamable_http_async(args.host, args.port))
    else:
        asyncio.run(run_stdio_async())


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nMCP Server stopped by user.")
    except Exception:
        import traceback

        print("MCP Server encountered an error:")
        traceback.print_exc()
    finally:
        print("MCP Server process exiting.")
