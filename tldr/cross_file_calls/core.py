"""
Core types and constants for cross-file call graph resolution.
"""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from tldr.workspace import WorkspaceConfig, load_workspace_config, filter_paths

# Tree-sitter support detection
try:
    import tree_sitter
    import tree_sitter_typescript
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

TREE_SITTER_GO_AVAILABLE = False
try:
    import tree_sitter_go
    TREE_SITTER_GO_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_RUST_AVAILABLE = False
try:
    import tree_sitter_rust
    TREE_SITTER_RUST_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_JAVA_AVAILABLE = False
try:
    import tree_sitter_java
    TREE_SITTER_JAVA_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_C_AVAILABLE = False
try:
    import tree_sitter_c
    TREE_SITTER_C_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_RUBY_AVAILABLE = False
try:
    import tree_sitter_ruby
    TREE_SITTER_RUBY_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_PHP_AVAILABLE = False
try:
    import tree_sitter_php
    TREE_SITTER_PHP_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_CPP_AVAILABLE = False
try:
    import tree_sitter_cpp
    TREE_SITTER_CPP_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_KOTLIN_AVAILABLE = False
try:
    import tree_sitter_kotlin
    TREE_SITTER_KOTLIN_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_SWIFT_AVAILABLE = False
try:
    import tree_sitter_swift
    TREE_SITTER_SWIFT_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_CSHARP_AVAILABLE = False
try:
    import tree_sitter_c_sharp
    TREE_SITTER_CSHARP_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_SCALA_AVAILABLE = False
try:
    import tree_sitter_scala
    TREE_SITTER_SCALA_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_LUA_AVAILABLE = False
try:
    import tree_sitter_lua
    TREE_SITTER_LUA_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_LUAU_AVAILABLE = False
try:
    import tree_sitter_luau
    TREE_SITTER_LUAU_AVAILABLE = True
except ImportError:
    pass

TREE_SITTER_ELIXIR_AVAILABLE = False
try:
    import tree_sitter_elixir
    TREE_SITTER_ELIXIR_AVAILABLE = True
except ImportError:
    pass

# Alias names for HAS_*_PARSER pattern
HAS_TS_PARSER = TREE_SITTER_AVAILABLE
HAS_GO_PARSER = TREE_SITTER_GO_AVAILABLE
HAS_RUST_PARSER = TREE_SITTER_RUST_AVAILABLE
HAS_JAVA_PARSER = TREE_SITTER_JAVA_AVAILABLE
HAS_C_PARSER = TREE_SITTER_C_AVAILABLE
HAS_RUBY_PARSER = TREE_SITTER_RUBY_AVAILABLE
HAS_PHP_PARSER = TREE_SITTER_PHP_AVAILABLE
HAS_CPP_PARSER = TREE_SITTER_CPP_AVAILABLE
HAS_KOTLIN_PARSER = TREE_SITTER_KOTLIN_AVAILABLE
HAS_SWIFT_PARSER = TREE_SITTER_SWIFT_AVAILABLE
HAS_CSHARP_PARSER = TREE_SITTER_CSHARP_AVAILABLE
HAS_SCALA_PARSER = TREE_SITTER_SCALA_AVAILABLE
HAS_LUA_PARSER = TREE_SITTER_LUA_AVAILABLE
HAS_LUAU_PARSER = TREE_SITTER_LUAU_AVAILABLE
HAS_ELIXIR_PARSER = TREE_SITTER_ELIXIR_AVAILABLE


@dataclass
class ProjectCallGraph:
    """Cross-file call graph with edges as (src_file, src_func, dst_file, dst_func)."""

    _edges: set[tuple[str, str, str, str]] = field(default_factory=set)

    def add_edge(self, src_file: str, src_func: str, dst_file: str, dst_func: str):
        """Add a call edge from src_file:src_func to dst_file:dst_func."""
        self._edges.add((src_file, src_func, dst_file, dst_func))

    @property
    def edges(self) -> set[tuple[str, str, str, str]]:
        """Return all edges as a set of tuples."""
        return self._edges

    def __contains__(self, edge: tuple[str, str, str, str]) -> bool:
        """Check if an edge exists in the graph."""
        return edge in self._edges


# Parser factory functions
def _get_ts_parser():
    """Get or create a tree-sitter TypeScript parser."""
    if not TREE_SITTER_AVAILABLE:
        raise RuntimeError("tree-sitter-typescript not available")

    ts_lang = tree_sitter.Language(tree_sitter_typescript.language_typescript())
    parser = tree_sitter.Parser(ts_lang)
    return parser


def _get_rust_parser():
    """Get or create a tree-sitter Rust parser."""
    if not TREE_SITTER_RUST_AVAILABLE:
        raise RuntimeError("tree-sitter-rust not available")

    rust_lang = tree_sitter.Language(tree_sitter_rust.language())
    parser = tree_sitter.Parser(rust_lang)
    return parser


def _get_go_parser():
    """Get or create a tree-sitter Go parser."""
    if not TREE_SITTER_GO_AVAILABLE:
        raise RuntimeError("tree-sitter-go not available")

    go_lang = tree_sitter.Language(tree_sitter_go.language())
    parser = tree_sitter.Parser(go_lang)
    return parser


def _get_java_parser():
    """Get or create a tree-sitter Java parser."""
    if not TREE_SITTER_JAVA_AVAILABLE:
        raise RuntimeError("tree-sitter-java not available")

    java_lang = tree_sitter.Language(tree_sitter_java.language())
    parser = tree_sitter.Parser(java_lang)
    return parser


def _get_c_parser():
    """Get or create a tree-sitter C parser."""
    if not TREE_SITTER_C_AVAILABLE:
        raise RuntimeError("tree-sitter-c not available")

    c_lang = tree_sitter.Language(tree_sitter_c.language())
    parser = tree_sitter.Parser(c_lang)
    return parser


def _get_ruby_parser():
    """Get or create a tree-sitter Ruby parser."""
    if not TREE_SITTER_RUBY_AVAILABLE:
        raise RuntimeError("tree-sitter-ruby not available")

    ruby_lang = tree_sitter.Language(tree_sitter_ruby.language())
    parser = tree_sitter.Parser(ruby_lang)
    return parser


def _get_php_parser():
    """Get or create a tree-sitter PHP parser."""
    if not TREE_SITTER_PHP_AVAILABLE:
        raise RuntimeError("tree-sitter-php not available")

    php_lang = tree_sitter.Language(tree_sitter_php.language_php())
    parser = tree_sitter.Parser(php_lang)
    return parser


def _get_cpp_parser():
    """Get or create a tree-sitter C++ parser."""
    if not TREE_SITTER_CPP_AVAILABLE:
        raise RuntimeError("tree-sitter-cpp not available")

    cpp_lang = tree_sitter.Language(tree_sitter_cpp.language())
    parser = tree_sitter.Parser(cpp_lang)
    return parser


def _get_kotlin_parser():
    """Get or create a tree-sitter Kotlin parser."""
    if not TREE_SITTER_KOTLIN_AVAILABLE:
        raise RuntimeError("tree-sitter-kotlin not available")

    kotlin_lang = tree_sitter.Language(tree_sitter_kotlin.language())
    parser = tree_sitter.Parser(kotlin_lang)
    return parser


def _get_swift_parser():
    """Get or create a tree-sitter Swift parser."""
    if not TREE_SITTER_SWIFT_AVAILABLE:
        raise RuntimeError("tree-sitter-swift not available")

    swift_lang = tree_sitter.Language(tree_sitter_swift.language())
    parser = tree_sitter.Parser(swift_lang)
    return parser


def _get_csharp_parser():
    """Get or create a tree-sitter C# parser."""
    if not TREE_SITTER_CSHARP_AVAILABLE:
        raise RuntimeError("tree-sitter-c-sharp not available")

    csharp_lang = tree_sitter.Language(tree_sitter_c_sharp.language())
    parser = tree_sitter.Parser(csharp_lang)
    return parser


def _get_scala_parser():
    """Get or create a tree-sitter Scala parser."""
    if not TREE_SITTER_SCALA_AVAILABLE:
        raise RuntimeError("tree-sitter-scala not available")

    scala_lang = tree_sitter.Language(tree_sitter_scala.language())
    parser = tree_sitter.Parser(scala_lang)
    return parser


def _get_lua_parser():
    """Get or create a tree-sitter Lua parser."""
    if not TREE_SITTER_LUA_AVAILABLE:
        raise RuntimeError("tree-sitter-lua not available")

    lua_lang = tree_sitter.Language(tree_sitter_lua.language())
    parser = tree_sitter.Parser(lua_lang)
    return parser


def _get_luau_parser():
    """Get or create a tree-sitter Luau parser."""
    if not TREE_SITTER_LUAU_AVAILABLE:
        raise RuntimeError("tree-sitter-luau not available")

    luau_lang = tree_sitter.Language(tree_sitter_luau.language())
    parser = tree_sitter.Parser(luau_lang)
    return parser


def _get_elixir_parser():
    """Get or create a tree-sitter Elixir parser."""
    if not TREE_SITTER_ELIXIR_AVAILABLE:
        raise RuntimeError("tree-sitter-elixir not available")

    elixir_lang = tree_sitter.Language(tree_sitter_elixir.language())
    parser = tree_sitter.Parser(elixir_lang)
    return parser
