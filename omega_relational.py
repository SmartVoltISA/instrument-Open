"""Ω Relational Diagnostic Engine — public, dependency-free MVP.

A graph is represented as weighted directed relations. Each relation carries
strength, stiffness, connectivity, memory and flow. The engine reports
observable/derived diagnostics; it does not claim physical laws.
"""
from dataclasses import dataclass
from collections import defaultdict
from math import log

@dataclass
class Relation:
    source: str
    target: str
    strength: float = 0.0
    stiffness: float = 0.0
    connectivity: float = 0.0
    memory: float = 0.0
    flow: float = 0.0

class OmegaRelationalGraph:
    def __init__(self):
        self.relations = {}
        self.nodes = set()

    def add_relation(self, source, target, *, strength=0.0, stiffness=0.0,
                     connectivity=0.0, memory=0.0, flow=0.0):
        self.nodes.update((source, target))
        self.relations[(source, target)] = Relation(
            source, target, float(strength), float(stiffness),
            float(connectivity), float(memory), float(flow))

    def diagnostics(self):
        incoming = defaultdict(float); outgoing = defaultdict(float)
        memory = defaultdict(float); degree = defaultdict(int)
        for r in self.relations.values():
            incoming[r.target] += max(0.0, r.flow)
            outgoing[r.source] += max(0.0, r.flow)
            memory[r.source] += max(0.0, r.memory)
            memory[r.target] += max(0.0, r.memory)
            degree[r.source] += 1; degree[r.target] += 1

        total = sum(outgoing.values()) or 1.0
        p = [v / total for v in outgoing.values() if v > 0]
        entropy = -sum(x * log(x) for x in p) if p else 0.0
        effective_nodes = 2.718281828459045 ** entropy if p else 0.0

        nodes = sorted(self.nodes)
        rows = []
        for n in nodes:
            fin = incoming[n]; fout = outgoing[n]
            rows.append({
                "node": n,
                "incoming_flow": fin,
                "outgoing_flow": fout,
                "flow_ratio_in_out": fin / (fout + 1e-12),
                "memory": memory[n],
                "degree": degree[n],
            })
        rows.sort(key=lambda x: x["flow_ratio_in_out"], reverse=True)
        return {
            "nodes": len(nodes),
            "relations": len(self.relations),
            "effective_outgoing_nodes": effective_nodes,
            "node_diagnostics": rows,
        }

    def classify(self):
        d = self.diagnostics()
        labels = []
        for row in d["node_diagnostics"]:
            r = row["flow_ratio_in_out"]
            if r >= 2.0:
                state = "HIGH_INFLOW"
            elif r <= 0.5:
                state = "HIGH_OUTFLOW"
            else:
                state = "BALANCED"
            labels.append((row["node"], state))
        return labels
