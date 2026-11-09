# ADR-008: On-Device Vector Retrieval

## Status
Accepted

## Context
Farmer manuals and FAO guidelines must be queryable offline without external Pinecone or Milvus vector databases.

## Decision
Implement in-memory deterministic token embedding and cosine similarity vector search matching `qvac-fabric-llm.cpp`.

## Consequences
Sub-2ms semantic retrieval over thousands of document chunks locally.