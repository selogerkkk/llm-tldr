"""
Base parser interface for cross-file call analysis.
"""

from typing import Dict, List, Optional


class BaseParser:
    """Base interface for all language parsers."""
    
    def extract_calls(self, file_path: str, timeout: Optional[float] = None) -> List[Dict]:
        """Extract function calls from a file."""
        raise NotImplementedError
    
    def parse_imports(self, file_path: str) -> List[Dict]:
        """Parse import statements from a file."""
        raise NotImplementedError