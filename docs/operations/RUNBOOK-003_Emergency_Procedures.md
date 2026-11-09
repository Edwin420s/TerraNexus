# RUNBOOK-003: Hydraulic Emergency Protocol

1. Press hardwired physical E-Stop button on main control box.
2. Verify pump contactor LED de-energizes.
3. Trigger software cutoff via API `/api/v1/irrigation/control/stop`.
4. Inspect field main lines for burst pressure.
