"""
ALZEN Graphify MCP HTTP Server (Phase 06)
Serves knowledge graph queries via HTTP on port 8889.
Loads graph once at startup (~1s for 102MB graph.json).
"""
import json
import os
import sys
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PROJECT_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = PROJECT_DIR / "graphify-out" / "graph.json"

# Global in-memory graph + indices (loaded once at startup)
GRAPH = None
GOD_NODES = None
NODE_INDEX = {}  # id -> node dict


def init_graph():
    global GRAPH, GOD_NODES, NODE_INDEX
    t0 = time.time()
    if not GRAPH_FILE.exists():
        print(f"[graphify-mcp] WARNING: {GRAPH_FILE} not found", file=sys.stderr)
        GRAPH = {"nodes": [], "links": []}
        GOD_NODES = []
        return

    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        GRAPH = json.load(f)
    load_time = time.time() - t0

    # Build node index
    for node in GRAPH.get("nodes", []):
        NODE_INDEX[node.get("id", "")] = node

    # Pre-compute god nodes
    links = GRAPH.get("links", [])
    degree = {}
    for link in links:
        src = link.get("source", "")
        tgt = link.get("target", "")
        degree[src] = degree.get(src, 0) + 1
        degree[tgt] = degree.get(tgt, 0) + 1

    top = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:10]
    GOD_NODES = [
        {"id": nid, "label": NODE_INDEX.get(nid, {}).get("label", nid), "edges": count}
        for nid, count in top
    ]

    print(f"[graphify-mcp] Graph loaded: {len(GRAPH['nodes'])} nodes, "
          f"{len(links)} links, {len(NODE_INDEX)} indexed "
          f"({load_time:.1f}s)", file=sys.stderr)


def query_graph(q: str, max_results: int = 50):
    nodes = GRAPH.get("nodes", [])
    results = []
    ql = q.lower()
    for node in nodes:
        label = node.get("label", "")
        src = node.get("source_file", "")
        if ql in label.lower() or ql in src.lower():
            results.append({
                "id": node.get("id", ""),
                "label": label[:200],
                "source_file": src,
                "community": node.get("community", "?"),
            })
            if len(results) >= max_results:
                break
    return results


class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _json(self, data, status=200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        try:
            if path == "/mcp" or path == "":
                self._json({
                    "service": "ALZEN Graphify MCP",
                    "version": "3.0.0",
                    "nodes": len(GRAPH.get("nodes", [])),
                    "links": len(GRAPH.get("links", [])),
                    "endpoints": [
                        "GET /mcp/query?q=<query>",
                        "GET /mcp/god-nodes",
                        "GET /mcp/health"
                    ]
                })
            elif path == "/mcp/health":
                self._json({
                    "status": "healthy" if GRAPH_FILE.exists() else "degraded",
                    "graph_exists": GRAPH_FILE.exists(),
                })
            elif path == "/mcp/query":
                q = params.get("q", [""])[0]
                if not q:
                    self._json({"error": "Missing 'q' parameter"}, 400)
                    return
                results = query_graph(q)
                self._json({"results": results, "total_hits": len(results)})
            elif path == "/mcp/god-nodes":
                self._json({"god_nodes": GOD_NODES})
            else:
                self._json({"error": "Unknown endpoint"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)


def main():
    port = int(os.environ.get("GRAPHIFY_MCP_PORT", 8889))
    print(f"[graphify-mcp] Initializing...", file=sys.stderr)
    init_graph()
    server = HTTPServer(("127.0.0.1", port), MCPHandler)
    print(f"[graphify-mcp] Ready on http://127.0.0.1:{port}/mcp", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
