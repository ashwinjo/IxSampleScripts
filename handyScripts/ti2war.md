# `ixia-ex.py` — Convert an IxNetwork Traffic Item to Raw and Re-point It to New Ports

## What this script does

You have an existing IxNetwork traffic item that was built on top of protocol
topologies (A → B). You want a **raw** copy of that same traffic — same packet
headers, same frame size, same rate — but sent between two **different**
physical ports (C → D), without touching the original.

This script does that in one run:

1. Connects to your live IxNetwork session.
2. Finds the original traffic item and shows you what it looks like.
3. Stops traffic if it is running (traffic config cannot be edited while live).
4. Cleans up any copies left over from a previous run.
5. Calls IxNetwork's `ConvertToRaw()`, which produces a new raw item.
6. Finds ports C and D by their **physical** location (chassis / card / port).
7. Re-points the new raw item's endpoints to C → D.
8. Renames the new item to the name you chose.
9. Prints a before/after summary so you can verify the result.

The original item is **never modified**. The script does **not** generate or
apply traffic — it only sets up the configuration.

---



## Prerequisites


| Requirement                                                  | Notes                                                           |
| ------------------------------------------------------------ | --------------------------------------------------------------- |
| Python 3.9+                                                  | Tested with 3.14                                                |
| `ixnetwork_restpy`                                           | `pip install ixnetwork-restpy` (tested with 1.9.0)              |
| IxNetwork Web Edition / Linux API server                     | Tested against IxNetwork 26.0                                   |
| An existing session                                          | The script connects to a session by ID — it does not create one |
| Ports C and D already **assigned** to vports in that session | They do not need to be connected; they do need to be mapped     |


---



## Configuration (edit these before running)

```python
SESSION_ID = 1
USERNAME = "admin"
PASSWORD = "..."
IXNETWORK_API_SERVER = "10.36.84.12"
```

Connection details for the IxNetwork API server and the session you want to
work in. `SESSION_ID` is the number you see in the IxNetwork Web UI URL
(`/api/v1/sessions/<ID>`).

> **Security note:** the password is stored in plain text in this file. For
> anything beyond a lab proof-of-concept, read it from an environment variable
> or a secrets store instead.

```python
SOURCE_TRAFFIC_ITEM_NAME = "AshJo"
```

The **exact** display name of the traffic item you want to copy. Matching is
case-sensitive and must be unique in the session.

```python
CONVERTED_RAW_TRAFFIC_ITEM_NAME = "Ashjo-Raw-Traffic"
```

What the new raw copy will be called when the script finishes.

```python
PORTS = {
    "C": {"chassis": "10.36.84.12", "card": 6, "port": 7},
    "D": {"chassis": "10.36.84.12", "card": 6, "port": 8},
}
```

The two **physical** test ports for the new traffic. You give the script the
real location (which chassis, which card, which port) and it works out which
IxNetwork vport is sitting on that location at run time. This matters because
vport IDs (`/vport/1`, `/vport/2`, …) are assigned dynamically and can change
between sessions — physical locations don't.

---



## Helper functions



### `fail(message)`

```python
def fail(message):
    raise RuntimeError(message)
```

A one-liner that stops the script with a clear error message. Every validation
check in the script calls this so you get a readable sentence instead of a
Python stack trace.

### `expected_assigned_to(port_definition)`

Builds the string IxNetwork uses to describe a physical port assignment:
`"<chassis>:<card>:<port>"`, for example `10.36.84.12:6:7`. Used for matching
and for printing.

### `show_vports(ixnetwork)`

Diagnostic helper. Lists every vport in the session with its name, REST path,
physical assignment, and connection state. Only called when something goes
wrong (e.g. port C can't be found), so you can see what *is* there.

### `find_vport_by_physical_port(ixnetwork, chassis, card, port)`

The core of the "resolve by physical location" logic.

1. Walks every vport in the session.
2. Compares each vport's `AssignedTo` value against `"<chassis>:<card>:<port>"`.
3. Fails if **zero** vports match (the port isn't assigned in this session).
4. Fails if **more than one** vport matches (ambiguous — IxNetwork normally
  prevents this, but the check is cheap).
5. Fails if the matched vport reports `IsMapped=False`.
6. Returns the vport object.

If it fails, it prints the full vport table first so you can see exactly what
the session contains.

### `raw_endpoint_from_alias(ixnetwork, alias)`

Translates `"C"` or `"D"` into the thing a raw traffic item actually needs as an
endpoint. For raw traffic, IxNetwork does **not** use the vport itself — it
uses the vport's `/protocols` child object:

```
/api/v1/sessions/1/ixnetwork/vport/3/protocols
```

This function looks up the alias in `PORTS`, finds the vport via
`find_vport_by_physical_port`, prints the resolution chain
(`10.36.84.12:6:7 → /vport/3 → /vport/3/protocols`), and returns the
`/protocols` object.

### `find_single_traffic_item(ixnetwork, name)`

Looks up a traffic item by its exact display name. Uses an anchored regex
(`^name$`) so `"Ashjo"` won't accidentally match `"Ashjo Raw (1)"`.

- If nothing matches, it prints every traffic item in the session (name, type,
REST path) so you can spot a typo.
- If more than one matches, it fails — names must be unique for this to work.



### `display_endpoint_sets(traffic_item)`

Prints a traffic item's name, `TrafficType`, REST path, and each endpoint set's
`Sources` and `Destinations`. Called before and after conversion so the change
is visible in the output.

---



## `main()` — step by step



### Step 1 — Connect to the session

```python
session_assistant = SessionAssistant(IpAddress=..., RestPort=443, SessionId=SESSION_ID, ...)
session = session_assistant.TestPlatform.Sessions.find(Id=SESSION_ID)
ixnetwork = session[0].Ixnetwork
```

`SessionAssistant` is RestPy's connection helper. It authenticates, finds the
platform type, and attaches to the existing session. `ClearConfig=False` is
essential — otherwise it would wipe the session on connect.

The script then verifies the session ID really exists and lists the available
IDs if it doesn't.

### Step 2 — Find the original traffic item

```python
traffic_item = find_single_traffic_item(ixnetwork, SOURCE_TRAFFIC_ITEM_NAME)
display_endpoint_sets(traffic_item)
```

Locates the source item and prints it. **Nothing is changed yet.** This is
your "before" snapshot.

### Step 3 — Stop traffic if it's running

```python
if traffic_state not in ("stopped", "unapplied"):
    ixnetwork.Traffic.StopStatelessTrafficBlocking()
```

IxNetwork won't let you edit traffic configuration while traffic is
transmitting. The script checks `Traffic.State` and only stops if necessary.
If it's already `stopped` or `unapplied`, this step is skipped.

### Step 4 — Clean up leftovers from previous runs

```python
leftover_pattern = "^(Ashjo-Raw-Traffic|AshJo Raw \(\d+\))$"
for leftover in ixnetwork.Traffic.TrafficItem.find(Name=leftover_pattern):
    leftover.remove()
```

Makes the script safe to run repeatedly. It removes:

- Any item already named `CONVERTED_RAW_TRAFFIC_ITEM_NAME` (from a previous
successful run).
- Any item named `"<Source> Raw (N)"` (from a previous run that failed midway).

Only items matching those exact patterns are removed. The original is not
affected.

### Step 5 — Convert to raw

This is the step with the important IxNetwork behaviour to understand.

```python
before_hrefs = {ti.href for ti in ixnetwork.Traffic.TrafficItem.find()}
traffic_item.ConvertToRaw()
new_items = [ti for ti in ixnetwork.Traffic.TrafficItem.find() if ti.href not in before_hrefs]
raw_item = new_items[0]
```

`ConvertToRaw()` **does not convert the item in place.** On IxNetwork 26.x it
creates a **brand-new** traffic item named `"<Original> Raw (1)"`, copies the
packet stacks / frame size / rate into it, and leaves the original exactly as
it was.

That's why the script takes a snapshot of all traffic item REST paths *before*
the call, then looks for whichever path is new *after* the call. That new item
is the raw copy. The script verifies exactly one new item appeared and that
its `TrafficType` is really `raw`.

> **Why this matters:** an earlier version of this script re-looked-up the
> item by the *original* name after converting, got the untouched original
> (still `ipv4`), and tried to push raw endpoints onto it. IxNetwork rejected
> that with `Invalid Endpoints: Unable to create endpoint sets` — because raw
> endpoints are only valid on a raw item.



### Step 6 — Resolve ports C and D

```python
c_raw_endpoint = raw_endpoint_from_alias(ixnetwork, "C")
d_raw_endpoint = raw_endpoint_from_alias(ixnetwork, "D")
```

Turns your physical port definitions into the `/vport/N/protocols` objects the
raw item needs. Output shows the full chain so you can confirm the right vport
was picked:

```
Resolved C: 10.36.84.12:6:7 -> /api/v1/sessions/1/ixnetwork/vport/3 -> .../vport/3/protocols
Resolved D: 10.36.84.12:6:8 -> /api/v1/sessions/1/ixnetwork/vport/4 -> .../vport/4/protocols
```



### Step 7 — Re-point the endpoints

```python
for es in raw_item.EndpointSet.find():
    es.update(Sources=[c_raw_endpoint.href], Destinations=[d_raw_endpoint.href])
```

Updates every endpoint set on the **new raw item** so source = C and
destination = D. The loop handles items with more than one endpoint set.

### Step 8 — Rename and verify

```python
raw_item.update(Name=CONVERTED_RAW_TRAFFIC_ITEM_NAME)
```

Renames `"<Original> Raw (1)"` to your chosen name, then re-reads it from the
server and prints:

- The final `TrafficType` and endpoint REST paths.
- A human-readable mapping of each endpoint back to its physical port:

```
Resolved physical ports:
  EndpointSet 1   Sources     : 10.36.84.12:6:7  (Ethernet - 003)
  EndpointSet 1   Destinations: 10.36.84.12:6:8  (Ethernet - 004)
```



### Error handling

```python
if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        sys.exit(1)
```

Any failure — connection, lookup, validation — prints a single `ERROR:` line
and exits with status 1, so this can be dropped into a larger automation
pipeline and the caller can check the exit code.

---



## Running it

```bash
pip install ixnetwork-restpy
python3 ixia-ex.py
```

A successful run ends with:

```
Success.
  'AshJo' — unchanged
  'Ashjo-Raw-Traffic' — raw copy with C->D endpoints (not generated/applied)
```

RestPy also writes a detailed log to `restpy.log` in the working directory.

---



## What the script deliberately does **not** do


| Not done                  | Why                                                                                                                              | How to do it yourself                                                |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Modify the original item  | That's the whole point — you keep A → B intact                                                                                   | —                                                                    |
| `Generate()` the raw item | You may want to tune headers first                                                                                               | Traffic → right-click item → Generate, or `raw_item.Generate()`      |
| `Traffic.Apply()`         | Apply is global: it pushes **every** enabled item. If any other item references released/unassigned ports, the whole apply fails | Connect the required ports, disable items you don't want, then Apply |
| Connect ports C and D     | Taking port ownership is a decision for the operator                                                                             | In the UI, or `vport.ConnectPort()`                                  |


---



## Troubleshooting

`Traffic item 'X' was not found`
The name must match exactly, including case. The error lists every item in the
session so you can copy the right one.

`No mapped vport matches physical port '...'`
Ports C / D aren't assigned to a vport in this session. Assign them in the
Ports view first. The error prints every vport and its `AssignedTo` value.

`Expected ConvertToRaw() to create exactly 1 new traffic item, found 0`
Usually means traffic is still running or the item is already raw. Check
`Traffic.State` in the output.

`Invalid Endpoints: Unable to create endpoint sets`
You should not see this with the current script. If you do, it means endpoints
were applied to a non-raw item — see Step 5 above.

**Apply fails later with** `Port is Unassigned or Port CPU not ready`
Not caused by this script. Some *other* enabled traffic item in the session
references ports that aren't connected. Either connect those ports or disable
that item before applying.
