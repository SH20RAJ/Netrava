# ADR-001: Selection of PostgreSQL with PostGIS as Spatial System of Record

## Status
Accepted

## Context
Statewide CCTV deployment across Gujarat encompasses 80,000 cameras positioned along urban junctions, state expressways, and inter-district checkposts. The platform requires spatial bounding-box indexing, proximity radius queries, route line generation, and strict transactional ACID integrity for audit logs and watchlists.

Alternative databases considered:
1. **MongoDB**: Strong JSON flexibility, but inferior spatial geometry analytics and weak transactional foreign key consistency for chain-of-custody audits.
2. **Elasticsearch**: Fast text search, but high operational complexity, dual-write synchronization hazards, and excessive RAM footprint for small edge/district nodes.
3. **Cassandra**: High write throughput, but lack of complex spatial joins (`ST_DWithin`, `ST_MakeLine`) and no ACID transactions.

## Decision
We selected **PostgreSQL 16 with PostGIS** as the primary relational and spatial system of record, supplemented by an in-memory SQLite fallback with Python Haversine calculations for zero-dependency local development and evaluation.

## Consequences
- **Benefits**: Native R-Tree spatial indexing (`GIST`), court-grade ACID transactional logs, trigram text matching (`pg_trgm`) for fuzzy license plate lookup, and battle-tested government reliability.
- **Trade-offs**: For large-scale full-text event search beyond 50 million events, an OpenSearch read-replica can be attached without altering the primary schema.
