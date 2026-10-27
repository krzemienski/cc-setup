#!/usr/bin/env python3
"""
File Operations Example - Working with Files via SDK

Demonstrates patterns for analyzing files, directories, and
codebases using the Python Agent SDK.
"""

import anyio
import os
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import Tool, ToolDefinition, ToolParameter


async def analyze_file(filepath: str) -> dict:
    """
    Analyze a single file
    
    Returns file metadata and content summary
    """
    path = Path(filepath)
    
    if not path.exists():
        return {"error": f"File not found: {filepath}"}
    
    # Get file stats
    stats = path.stat()
    
    # Read content (with size limit)
    content = ""
    if stats.st_size < 1_000_000:  # Limit to 1MB
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            content = f"Error reading file: {e}"
    
    return {
        "path": str(path),
        "name": path.name,
        "extension": path.suffix,
        "size_bytes": stats.st_size,
        "line_count": len(content.split('\n')) if content else 0,
        "is_text": is_text_file(path),
        "content_preview": content[:500] if content else None
    }


async def list_directory(dirpath: str, pattern: str = "*") -> dict:
    """
    List files in a directory matching a pattern
    """
    path = Path(dirpath)
    
    if not path.exists() or not path.is_dir():
        return {"error": f"Directory not found: {dirpath}"}
    
    files = []
    for item in path.glob(pattern):
        if item.is_file():
            files.append({
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size
            })
    
    return {
        "directory": str(path),
        "pattern": pattern,
        "file_count": len(files),
        "files": files
    }


async def search_in_files(dirpath: str, search_term: str, extension: str = ".py") -> dict:
    """
    Search for a term across files in a directory
    """
    path = Path(dirpath)
    results = []
    
    if not path.exists():
        return {"error": f"Directory not found: {dirpath}"}
    
    for filepath in path.rglob(f"*{extension}"):
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            if search_term in content:
                # Find matching lines
                lines = content.split('\n')
                matches = [
                    {"line": i+1, "text": line.strip()}
                    for i, line in enumerate(lines)
                    if search_term in line
                ]
                results.append({
                    "file": str(filepath),
                    "matches": matches[:5]  # Limit matches per file
                })
        except Exception:
            continue
    
    return {
        "search_term": search_term,
        "directory": str(path),
        "extension": extension,
        "files_found": len(results),
        "results": results[:10]  # Limit total results
    }


def is_text_file(path: Path) -> bool:
    """Check if file is likely a text file"""
    text_extensions = {'.txt', '.py', '.js', '.md', '.json', '.yaml', 
                      '.yml', '.html', '.css', '.sh', '.c', '.cpp'}
    return path.suffix.lower() in text_extensions


async def basic_file_analysis():
    """
    Example: Basic file analysis with SDK
    """
    tools = [
        Tool(
            definition=ToolDefinition(
                name="analyze_file",
                description="Analyze a file and return metadata and content summary",
                parameters=[
                    ToolParameter(
                        name="filepath",
                        type="string",
                        description="Path to the file to analyze",
                        required=True
                    )
                ]
            ),
            handler=analyze_file
        ),
        Tool(
            definition=ToolDefinition(
                name="list_directory",
                description="List files in a directory matching a pattern",
                parameters=[
                    ToolParameter(name="dirpath", type="string", required=True),
                    ToolParameter(name="pattern", type="string", required=False)
                ]
            ),
            handler=list_directory
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("File Analysis Demo")
        print("=" * 60)
        
        # Analyze current directory
        print("\n[User]: What Python files are in the current directory?")
        response = await client.send_message(
            "What Python files are in the current directory? Use list_directory with pattern='*.py'"
        )
        print(f"[Claude]: {response}")
        
        # Analyze a specific file
        print("\n[User]: Analyze the simple_query.py file")
        response = await client.send_message(
            "Analyze the simple_query.py file in the scripts directory"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def codebase_search():
    """
    Example: Searching across a codebase
    """
    tools = [
        Tool(
            definition=ToolDefinition(
                name="search_in_files",
                description="Search for a term across files in a directory",
                parameters=[
                    ToolParameter(name="dirpath", type="string", required=True),
                    ToolParameter(name="search_term", type="string", required=True),
                    ToolParameter(name="extension", type="string", required=False)
                ]
            ),
            handler=search_in_files
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("Codebase Search Demo")
        print("=" * 60)
        
        print("\n[User]: Find all uses of 'ClaudeSDKClient' in Python files")
        response = await client.send_message(
            "Search for 'ClaudeSDKClient' in all Python files in the scripts directory"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


async def directory_analysis():
    """
    Example: Comprehensive directory analysis
    """
    async def get_directory_stats(dirpath: str) -> dict:
        """Get comprehensive directory statistics"""
        path = Path(dirpath)
        
        if not path.exists():
            return {"error": "Directory not found"}
        
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "largest_files": []
        }
        
        files_with_size = []
        
        for item in path.rglob("*"):
            if item.is_file():
                stats["total_files"] += 1
                size = item.stat().st_size
                stats["total_size"] += size
                
                ext = item.suffix or "no_extension"
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                
                files_with_size.append((str(item), size))
        
        # Get 5 largest files
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        stats["largest_files"] = [
            {"file": f, "size": s} 
            for f, s in files_with_size[:5]
        ]
        
        return stats
    
    tools = [
        Tool(
            definition=ToolDefinition(
                name="get_directory_stats",
                description="Get comprehensive statistics about a directory",
                parameters=[
                    ToolParameter(name="dirpath", type="string", required=True)
                ]
            ),
            handler=get_directory_stats
        )
    ]
    
    async with ClaudeSDKClient(tools=tools) as client:
        print("Directory Analysis Demo")
        print("=" * 60)
        
        print("\n[User]: Analyze the scripts directory")
        response = await client.send_message(
            "Give me statistics about the scripts directory"
        )
        print(f"[Claude]: {response}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run basic file analysis
    anyio.run(basic_file_analysis)
    
    # Uncomment to try other examples:
    # anyio.run(codebase_search)
    # anyio.run(directory_analysis)
