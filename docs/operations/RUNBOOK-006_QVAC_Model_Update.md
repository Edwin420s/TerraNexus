# RUNBOOK-006: QVAC Model Update

1. Validate new GGUF / quantized binary checksum.
2. Copy to `models/qvac/qvac-agronomist-7b.bin`.
3. Execute test inference script `python3 scripts/run_qvac_server.py`.
4. Verify Wi-Fi-off execution mode.
