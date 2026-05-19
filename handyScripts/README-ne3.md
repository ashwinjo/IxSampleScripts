# ne3.py — NE Port Delay Automation

Python CLI and library for configuring **ethernet delay** on a network element (NE) via REST. Authenticates with Basic auth, applies delay with a minimal `profiles` PUT payload, and verifies each change with `GET /api/hw/Port/{id}`.

## Requirements

- Python 3.10+
- [`requests`](https://pypi.org/project/requests/)

```bash
pip install requests
```

## Quick start

```bash
python3 ne3.py
```

Defaults: host `10.36.84.18`, port `1`, profile `Port1-msoftProfile`.

With arguments:

```bash
python3 ne3.py <host> <port_id> <profile_tag> [steps]
```

Example with a custom delay sequence:

```bash
python3 ne3.py 10.36.158.21 1 Port1-msoftProfile 100:MS,200:MS,300:MS
```

## Operations menu

When you run the script, choose:

| Option | Description |
|--------|-------------|
| **1** | Run the configured delay sequence; GET-verify after each step |
| **2** | Interactive loop — enter delay + unit, confirm, apply, verify |
| **3** | Sequence, then interactive loop |

## Delay format

Delay is **value + unit**, sent in `ethernetDelay` as:

```json
{
  "delay": 150,
  "units": "MS",
  "pdvMode": "NONE",
  "enabled": "true"
}
```

### Supported units

| Code | Meaning |
|------|---------|
| `KM` | kilometer |
| `US` | microsecond |
| `MS` | millisecond |
| `NS` | nanosecond |
| `M`  | meter |

Edit `DELAY_UNITS` at the top of `ne3.py` to change or extend units.

### Input examples

- Interactive: `150 MS`, `150MS`, or `150` (defaults to `MS`)
- CLI steps: `100:MS,200:US,10:M`

### Default sequence

Configured in `DELAY_STEPS`:

```python
DELAY_STEPS = (
    (100, "MS"),
    (200, "MS"),
    (300, "MS"),
)
```

## API flow

1. **Login** — `GET http://{host}/api` with Basic auth → read `X-Auth-Token`
2. **Set delay** — `PUT http://{host}/api/hw/Port/{port_id}` with `Authorization: Token …` and minimal `profiles` body (`enabled` as string `"true"`)
3. **Verify** — `GET` same port URL and compare `delay` + `units` to expected

## Programmatic use

```python
from ne3 import NEClient, DelaySetting, DELAY_STEPS

with NEClient("10.36.158.21", "admin", "admin") as ne:
    ne.authenticate()

    # Single update
    ne.update_profile_delay(1, "Port1-msoftProfile", DelaySetting(250, "MS"))

    # Stepped sequence
    ne.apply_delay_sequence(1, "Port1-msoftProfile", DELAY_STEPS)

    # Interactive prompts
    ne.interactive_delay_loop(1, "Port1-msoftProfile")
```

## Verification output

After each PUT, the script prints:

- HTTP status from PUT
- `[OK]` or `[CHECK]` comparing expected vs GET read-back
- A table of **all profiles** on the port (tag, enabled flags, delay, units)

Use the profile table to match what you see in the NE UI — the UI may be showing a different profile tag than the one you are updating.

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| Login fails / no token | NE IP reachable; API at `http://{host}/api` |
| `[CHECK]` but delay matches | `profile.enabled` and `ethernetDelay.enabled` must be `"true"` |
| Script OK, UI unchanged | Profile tag in CLI must match the profile selected in the UI |
| PUT returns 4xx | Profile tag exists on that port; try the name shown in the profile table |

## Files

- `ne3.py` — client, CLI, and configuration constants

## Complete command examples

```bash
# Defaults (host 10.36.84.18, port 1, profile Port1-msoftProfile)
python3 /Users/ashwin.joshi/ne3.py
```

```bash
# Host only
python3 /Users/ashwin.joshi/ne3.py 10.36.158.21
```

```bash
# Host + port + profile
python3 /Users/ashwin.joshi/ne3.py 10.36.158.21 1 Port1-msoftProfile
```

```bash
# Full command: host, port, profile, and delay sequence (100 → 200 → 300 ms)
python3 /Users/ashwin.joshi/ne3.py 10.36.158.21 1 Port1-msoftProfile 100:MS,200:MS,300:MS
```

```bash
# Mixed units in the sequence
python3 /Users/ashwin.joshi/ne3.py 10.36.158.21 1 Port1-msoftProfile 100:MS,500:US,10:M
```

After you run one of these, the script prompts for an operation:

```
Operations:
  1) Run configured delay sequence (GET verify each step)
  2) Interactive delay loop (enter value + unit each time)
  3) Both — sequence, then interactive loop
Choose [1]:
```

For option **2**, enter delays at the prompt like:

```
New delay (value UNIT) [q=quit]: 150 MS
```
