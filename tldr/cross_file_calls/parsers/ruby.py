"""
Ruby parser for cross-file call analysis.
"""

import re
from typing import Dict, List, Optional

from tldr.cross_file_calls.parsers.base import BaseParser


class RubyParser(BaseParser):
    """Parser for Ruby files."""
    
    def extract_calls(self, file_path: str, timeout: Optional[float] = None) -> List[Dict]:
        """Extract function calls from a Ruby file."""
        return self._extract_calls_regex(file_path)
    
    def parse_imports(self, file_path: str) -> List[Dict]:
        """Parse require statements from a Ruby file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            
            patterns = [
                (r'require\s+[\'"]([^\'"]+)[\'"]', 'require'),
                (r'require_relative\s+[\'"]([^\'"]+)[\'"]', 'require_relative'),
                (r'include\s+(\w+)', 'include'),
            ]
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern, import_type in patterns:
                    match = re.search(pattern, line)
                    if match:
                        imports.append({
                            'type': import_type,
                            'module': match.group(1).strip(),
                            'name': match.group(1).strip(),
                            'asname': None,
                            'line': line_num,
                            'column': line.find(match.group(0))
                        })
            
            return imports
            
        except Exception:
            return []
    
    def _extract_calls_regex(self, file_path: str) -> List[Dict]:
        """Regex-based call extraction for Ruby."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            calls = []
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in re.finditer(r'(\b[a-z_]\w*[!?]?)\s*\(', line):
                    calls.append({
                        'file': file_path,
                        'line': line_num,
                        'column': match.start(),
                        'type': 'method_call',
                        'function': match.group(1),
                        'object': None,
                        'module': None,
                        'full_expression': match.group(1),
                        'args': []
                    })
            
            return calls
            
        except Exception:
            return []


# Backward compatibility
def _extract_ruby_file_calls(file_path: str) -> List[Dict]:
    """Extract Ruby file calls (backward compatibility)."""
    parser = RubyParser()
    return parser.extract_calls(file_path)