# Hardware Watchdog Register Implementation

## Specification & Guidelines
Hardware timer 0 configured in count-up mode. Exceeding 1800s without reset drives GPIO 25 and 26 HIGH, shutting off coils.
