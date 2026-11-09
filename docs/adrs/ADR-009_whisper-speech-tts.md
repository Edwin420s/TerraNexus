# ADR-009: On-Device Speech AI

## Status
Accepted

## Context
Field workers require voice-driven queries while wearing gloves or operating farm machinery.

## Decision
Integrate local Whisper ASR and synthesize 16-bit PCM WAV audio containers matching `qvac-fabric-speech.cpp`.

## Consequences
Hands-free agricultural intelligence without internet access.