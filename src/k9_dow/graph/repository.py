from __future__ import annotations

import logging
from typing import Any, Optional

log = logging.getLogger(__name__)


# ─── Neo4j Constraint Definitions ───

CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:CapabilityNeed) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:CapabilityDocs) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:SERequirement) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:TechnicalBaselineItem) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:DoDAFView) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:TestCase) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:VerificationEvent) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:FundingLine) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:SEPBaseline) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:GateCriterion) REQUIRE n.id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (n:SERequirement) ON (n.status)",
    "CREATE INDEX IF NOT EXISTS FOR (n:SERequirement) ON (n.maturity)",
    "CREATE INDEX IF NOT EXISTS FOR (n:SERequirement) ON (n.verification_method)",
    "CREATE INDEX IF NOT EXISTS FOR (n:DoDAFView) ON (n.view_type)",
    "CREATE INDEX IF NOT EXISTS FOR (n:FundingLine) ON (n.status)",
    "CREATE INDEX IF NOT EXISTS FOR (n:SEPBaseline) ON (n.status)",
]


class TraceabilityRepository:
    """Graph CRUD for the DAS traceability model.

    Uses neo4j Driver directly — no OGM. Matches the canonical entities
    and relationships from the Project-Specification (SWP cut).
    """

    def __init__(self, driver) -> None:
        self._driver = driver

    def init_schema(self) -> None:
        with self._driver.session() as session:
            for stmt in CONSTRAINTS + INDEXES:
                session.run(stmt)
        log.info("[Graph] Schema initialized: %d constraints, %d indexes",
                 len(CONSTRAINTS), len(INDEXES))

    # ─── Node CRUD ───

    def merge_node(self, label: str, props: dict[str, Any]) -> None:
        node_id = props["id"]
        set_clause = ", ".join(f"n.{k} = ${k}" for k in props if k != "id")
        query = f"MERGE (n:{label} {{id: $id}}) SET {set_clause}"
        with self._driver.session() as session:
            session.run(query, **props)

    def get_node(self, label: str, node_id: str) -> Optional[dict]:
        query = f"MATCH (n:{label} {{id: $id}}) RETURN properties(n) AS props"
        with self._driver.session() as session:
            result = session.run(query, id=node_id)
            record = result.single()
            return dict(record["props"]) if record else None

    def delete_node(self, label: str, node_id: str) -> None:
        query = f"MATCH (n:{label} {{id: $id}}) DETACH DELETE n"
        with self._driver.session() as session:
            session.run(query, id=node_id)

    # ─── Relationship CRUD ───

    def create_relationship(
        self,
        from_label: str, from_id: str,
        rel_type: str,
        to_label: str, to_id: str,
        props: Optional[dict] = None,
    ) -> None:
        prop_clause = ""
        params: dict[str, Any] = {"from_id": from_id, "to_id": to_id}
        if props:
            prop_clause = " {" + ", ".join(f"{k}: ${k}" for k in props) + "}"
            params.update(props)

        query = (
            f"MATCH (a:{from_label} {{id: $from_id}}), (b:{to_label} {{id: $to_id}}) "
            f"MERGE (a)-[r:{rel_type}{prop_clause}]->(b)"
        )
        with self._driver.session() as session:
            session.run(query, **params)

    def remove_relationship(
        self, from_label: str, from_id: str, rel_type: str, to_label: str, to_id: str,
    ) -> None:
        query = (
            f"MATCH (a:{from_label} {{id: $from_id}})-[r:{rel_type}]->(b:{to_label} {{id: $to_id}}) "
            f"DELETE r"
        )
        with self._driver.session() as session:
            session.run(query, from_id=from_id, to_id=to_id)

    # ─── Traceability Queries ───

    def get_requirement_trace_up(self, req_id: str) -> list[dict]:
        query = """
        MATCH path = (s:SERequirement {id: $id})<-[:DERIVES|DECOMPOSES_TO_CHILD*]-(cap:CapabilityDocs)
        RETURN [n IN nodes(path) | properties(n)] AS chain
        """
        with self._driver.session() as session:
            return [dict(r) for r in session.run(query, id=req_id)]

    def get_requirement_trace_down(self, req_id: str) -> list[dict]:
        query = """
        MATCH (s:SERequirement {id: $id})-[:VERIFIED_BY]->(tc:TestCase)
        RETURN properties(tc) AS test_case
        """
        with self._driver.session() as session:
            return [dict(r)["test_case"] for r in session.run(query, id=req_id)]

    def get_coverage_report(self) -> dict:
        query = """
        MATCH (s:SERequirement) WHERE s.status <> 'superseded'
        WITH count(s) AS total
        OPTIONAL MATCH (v:SERequirement)-[:VERIFIED_BY]->() WHERE v.status <> 'superseded'
        WITH total, count(DISTINCT v) AS verified
        RETURN total, verified, total - verified AS unverified,
               CASE WHEN total > 0 THEN toFloat(verified) / total ELSE 0.0 END AS coverage
        """
        with self._driver.session() as session:
            record = session.run(query).single()
            return dict(record) if record else {"total": 0, "verified": 0, "unverified": 0, "coverage": 0.0}

    def supersede_requirement(self, old_id: str, new_id: str) -> None:
        """SWP-specific: requirements are revised via supersedes edges,
        not edited in place, to preserve audit trail."""
        with self._driver.session() as session:
            session.run(
                "MATCH (old:SERequirement {id: $old_id}), (new:SERequirement {id: $new_id}) "
                "MERGE (new)-[:SUPERSEDES]->(old) "
                "SET old.status = 'superseded'",
                old_id=old_id, new_id=new_id,
            )
