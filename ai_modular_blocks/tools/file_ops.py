"""
File operations tool - Does one thing well: file I/O

Pure Python pathlib usage. No framework abstractions.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


class FileOperations:
    """Simple file operations using standard Python pathlib."""
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read a text file."""
        try:
            path = Path(file_path)
            content = path.read_text(encoding=encoding)
            
            return {
                "content": content,
                "path": str(path),
                "size": len(content),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "path": file_path,
                "success": False
            }
    
    def write_file(
        self, 
        file_path: str, 
        content: str, 
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            path = Path(file_path)
            
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            path.write_text(content, encoding=encoding)
            
            return {
                "path": str(path),
                "bytes_written": len(content.encode(encoding)),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "path": file_path,
                "success": False
            }
    
    def list_files(
        self, 
        directory: str, 
        pattern: str = "*",
        recursive: bool = False
    ) -> Dict[str, Any]:
        """List files in a directory."""
        try:
            path = Path(directory)
            
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            if not path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {directory}")
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            file_list = []
            for file_path in files:
                file_list.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "is_file": file_path.is_file(),
                    "is_dir": file_path.is_dir(),
                    "size": file_path.stat().st_size if file_path.is_file() else None
                })
            
            return {
                "directory": directory,
                "files": file_list,
                "count": len(file_list),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "directory": directory,
                "success": False
            }


# Direct usage:
# files = FileOperations()
# content = files.read_file("example.txt")
# files.write_file("output.txt", "Hello World")
# file_list = files.list_files(".", "*.py")