
def match_service(url, services):
    if not url:
        return None

    for service, data in services.items():
        for alias in data["aliases"]:
            if alias in url:
                return service

    return None

def build_graph(scan_results, services):
    nodes = {}
    edges = []
    for repo in services:
        nodes[repo] = {
            "id": repo,
            "type": "service"
        }

    for r in scan_results:
        caller = r["repo"]

        for call in r.get("http_calls", []):
            target = match_service(call["url"], services)

            if target and target != caller:
                edges.append({
                    "src": caller,
                    "dst": target,
                    "type": "calls_api",
                    "confidence": "medium",
                    "evidence": {
                        "file": r["file"],
                        "line": call["lineno"],
                        "signal": call["url"]
                    }
                })

    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }
