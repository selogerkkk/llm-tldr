"""
C++ parser for cross-file call analysis.
"""

import os
import re
from typing import Dict, List, Optional

from tldr.cross_file_calls.parsers.base import BaseParser


class CppParser(BaseParser):
    """Parser for C++ files."""
    
    def extract_calls(self, file_path: str, timeout: Optional[float] = None) -> List[Dict]:
        """Extract function calls from a C++ file."""
        return self._extract_calls_regex(file_path)
    
    def parse_imports(self, file_path: str) -> List[Dict]:
        """Parse include statements from a C++ file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            
            # C++ include patterns
            patterns = [
                (r'#include\s+<([^>]+)>', 'system'),
                (r'#include\s+"([^"]+)"', 'local'),
            ]
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern, import_type in patterns:
                    match = re.search(pattern, line)
                    if match:
                        imports.append({
                            'type': import_type,
                            'module': match.group(1),
                            'name': match.group(1),
                            'asname': None,
                            'line': line_num,
                            'column': line.find(match.group(0))
                        })
            
            return imports
            
        except Exception:
            return []
    
    def _extract_calls_regex(self, file_path: str) -> List[Dict]:
        """Regex-based call extraction for C++."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            calls = []
            
            # C++ function call patterns (including method calls)
            patterns = [
                r'(\b[a-zA-Z_]\w*)\s*\(',
                r'(\b[a-zA-Z_]\w*::[a-zA-Z_]\w*)\s*\(',
            ]
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in patterns:
                    for match in re.finditer(pattern, line):
                        calls.append({
                            'file': file_path,
                            'line': line_num,
                            'column': match.start(),
                            'type': 'function_call',
                            'function': match.group(1).split('::')[-1],
                            'object': match.group(1).split('::')[0] if '::' in match.group(1) else None,
                            'module': match.group(1).split('::')[0] if '::' in match.group(1) else None,
                            'full_expression': match.group(1),
                            'args': []
                        })
            
            return calls
            
        except Exception:
            return []


# Backward compatibility
def _extract_cpp_file_calls(file_path: str) -> List[Dict]:
    """Extract C++ file calls (backward compatibility)."""
    parser = CppParser()
    return parser.extract_calls(file_path)