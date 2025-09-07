"""
File operations tool - Does one thing well: file I/O

Pure Python pathlib usage. No framework abstractions.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional


class FileOperations:
    """Simple file operations using standard Python pathlib."""
    
    async def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read a text file (async)."""
        try:
            path = Path(file_path)
            content = await asyncio.to_thread(path.read_text, encoding=encoding)

            return {
                "content": content,
                "path": str(path),
                "size": len(content),
                "success": True,
            }

        except Exception as e:
            return {"error": str(e), "path": file_path, "success": False}
    
    async def write_file(
        self, 
        file_path: str, 
        content: str, 
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """Write content to a file (async)."""
        try:
            path = Path(file_path)

            if create_dirs:
                await asyncio.to_thread(path.parent.mkdir, True, True)

            await asyncio.to_thread(path.write_text, content, encoding)

            return {
                "path": str(path),
                "bytes_written": len(content.encode(encoding)),
                "success": True,
            }

        except Exception as e:
            return {"error": str(e), "path": file_path, "success": False}
    
    async def list_files(
        self, 
        directory: str, 
        pattern: str = "*",
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List files in a directory (async)."""
        try:
            path = Path(directory)

            exists = await asyncio.to_thread(path.exists)
            if not exists:
                raise FileNotFoundError(f"Directory not found: {directory}")

            is_dir = await asyncio.to_thread(path.is_dir)
            if not is_dir:
                raise NotADirectoryError(f"Path is not a directory: {directory}")

            if recursive:
                files = await asyncio.to_thread(lambda: list(path.rglob(pattern)))
            else:
                files = await asyncio.to_thread(lambda: list(path.glob(pattern)))

            file_list = []
            for file_path in files:
                is_file = await asyncio.to_thread(file_path.is_file)
                is_directory = await asyncio.to_thread(file_path.is_dir)
                size = await asyncio.to_thread(lambda p=file_path: p.stat().st_size) if is_file else None
                file_list.append(
                    {
                        "name": file_path.name,
                        "path": str(file_path),
                        "is_file": is_file,
                        "is_dir": is_directory,
                        "size": size,
                    }
                )

            return {
                "directory": directory,
                "files": file_list,
                "count": len(file_list),
                "success": True,
            }

        except Exception as e:
            return {"error": str(e), "directory": directory, "success": False}


# Direct usage:
# files = FileOperations()
# content = files.read_file("example.txt")
# files.write_file("output.txt", "Hello World")
# file_list = files.list_files(".", "*.py")
