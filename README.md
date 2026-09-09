# PiPhi Network UniFi Protect & Access

UniFi Protect and Access integration for cameras, detections, NVRs, doors, readers, intercoms, alarms, and access events.

This repository is a Scaffold CLI 0.3.0 development baseline. The runtime currently implements the secure PiPhi lifecycle foundation (`connected`, configuration events, and `refresh`). The complete known upstream surface is accounted for in [`capability-catalog.json`](capability-catalog.json); vendor/device behavior remains unadvertised until its implementation and executable tests are complete.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
python scripts/validate.py
python scripts/validate_capability_catalog.py capability-catalog.json
```

## Security and ownership

- Secrets are removed from browser-visible runtime state and diagnostics.
- Mutating actions remain disabled and unadvertised until allow-list, confirmation, permission, idempotency, and failure semantics are implemented.
- Runtime identity is deterministic per PiPhi configuration.
- Planned and excluded capability-catalog entries must never leak into manifests, entities, behaviors, or commands.
