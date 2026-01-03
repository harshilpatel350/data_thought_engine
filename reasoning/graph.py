"""
Directed acyclic graph for reasoning nodes.
Provides insertion and acyclicity checks via topological sort.
"""
from __future__ import annotations

from typing import Dict, List, Set
from data_thought_engine.reasoning.node import Node


class ReasoningDAG:
    """Simple DAG implemented with adjacency lists.

    Keeps nodes immutable and checks for cycles when adding edges.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.adj: Dict[str, List[str]] = {}

    def add_node(self, node: Node) -> None:
        if node.id in self.nodes:
            return
        self.nodes[node.id] = node
        self.adj.setdefault(node.id, [])

    def add_edge(self, src: str, dst: str) -> None:
        if src not in self.nodes or dst not in self.nodes:
            raise KeyError("Both nodes must be present before adding an edge")
        self.adj.setdefault(src, []).append(dst)
        if self._has_cycle():
            # revert and raise explicit error
            self.adj[src].pop()
            raise ValueError("Adding this edge would create a cycle")

    def _has_cycle(self) -> bool:
        visited: Set[str] = set()
        stack: Set[str] = set()

        def visit(n: str) -> bool:
            if n in stack:
                return True
            if n in visited:
                return False
            visited.add(n)
            stack.add(n)
            for m in self.adj.get(n, []):
                if visit(m):
                    return True
            stack.remove(n)
            return False

        for node_id in list(self.nodes):
            if visit(node_id):
                return True
        return False

    def topological_order(self) -> List[Node]:
        in_deg: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for src, dsts in self.adj.items():
            for d in dsts:
                in_deg[d] = in_deg.get(d, 0) + 1
        queue = [nid for nid, deg in in_deg.items() if deg == 0]
        order: List[Node] = []
        while queue:
            n = queue.pop(0)
            order.append(self.nodes[n])
            for m in self.adj.get(n, []):
                in_deg[m] -= 1
                if in_deg[m] == 0:
                    queue.append(m)
        if len(order) != len(self.nodes):
            raise ValueError("Graph has a cycle or missing nodes")
        return order
