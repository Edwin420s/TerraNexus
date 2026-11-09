# ADR-011: Mandatory Human Approval Gate

## Status
Accepted

## Context
Autonomous AI agents propose inventory restocks. Rogue proposals must never autonomously drain treasury funds.

## Decision
Enforce strict human sign-off requirement (`requires_human_approval: true`) on every disbursement proposal.

## Consequences
Human operator maintains authoritative signature control over every financial transfer.