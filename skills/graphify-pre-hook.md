---
name: graphify-pre-hook
description: Pre-tool-use hook that queries Graphify MCP before any file read. Reduces token cost by 71.5x.
trigger: before Read tool
---

# Graphify Pre-Hook

Before reading ANY file in the ALZEN codebase, this hook intercepts and:
1. Queries `GET http://localhost:8889/mcp/query?q=<keyword>` for the symbol you're about to read
2. Returns the graph context (community, dependencies, related nodes)
3. Claude uses the graph context instead of reading the raw file

## Integration Architecture
```
Claude Code Read(file.py)
  → PreToolUse Hook
    → GET http://localhost:8889/mcp/query?q=file.py
    → Returns: {community: 5, related_nodes: [...], dependencies: [...]}
  → Claude uses graph context (71.5x fewer tokens)
  → Fallback: Read file range with symdex (lines 42-89)
```

## Token Reduction Math
- Naive full-file read: ~3,000 tokens/file
- Graph query: ~42 tokens/response
- Reduction: 3,000/42 = 71.5x

## Hermes CLI Integration
```bash
# Add to ~/.hermes/cli-config.yaml:
mcp_servers:
  - name: alzen-knowledge-graph
    url: http://localhost:8889/mcp
    pre_tool_use: true
    always_load: true
```
