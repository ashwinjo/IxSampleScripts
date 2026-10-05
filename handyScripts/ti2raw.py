from ixnetwork_restpy import SessionAssistant
import sys
import re
# # The following code represents how you can connect to the session using Session Assistant
# session= SessionAssistant(IpAddress="10.36.84.12", 
#                                      RestPort=443, SessionId=1, 
#                                      UserName="admin", Password="wrinkle#B52#B52", 
#                                      LogLevel=SessionAssistant.LOGLEVEL_INFO, LogFilename="restpy.log", ClearConfig=False)

# # The below section shows how to add or access the current Node
# high_level_stream = session_assistant.Ixnetwork .Traffic.TrafficItem.find(Name = "Traffic Item NMS").HighLevelStream.find()

# for high_level_streams in high_level_stream:
#     print(high_level_streams.Name)
#     high_level_streams.update(Enabled=False)
#     #high_level_streams.StartStatelessTrafficBlocking()
#     break

SESSION_ID = 1
USERNAME = "admin"
PASSWORD = "wrinkle#B52#B52"
IXNETWORK_API_SERVER = "10.36.84.12"

# The existing A->B traffic item to convert.
SOURCE_TRAFFIC_ITEM_NAME = "AshJo"

# Name assigned after ConvertToRaw() completes.
CONVERTED_RAW_TRAFFIC_ITEM_NAME = "Ashjo-Raw-Traffic"

# Physical locations of C and D.
# The script resolves these to whatever dynamic vport IDs exist in this session.
PORTS = {
    "C": {
        "chassis": "10.36.84.12",
        "card": 6,
        "port": 7,
    },
    "D": {
        "chassis": "10.36.84.12",
        "card": 6,
        "port": 8,
    },
}

# =============================================================================
# END USER CONFIGURATION
# =============================================================================


def fail(message):
    raise RuntimeError(message)


def expected_assigned_to(port_definition):
    """
    Expected Vport.AssignedTo string.

    Example:
        10.10.10.20:1:3
    """
    return (
        f"{port_definition['chassis']}:"
        f"{port_definition['card']}:"
        f"{port_definition['port']}"
    )


def show_vports(ixnetwork):
    """
    Prints diagnostics so you can verify IxNetwork's dynamic vport mapping.
    """
    print("\nAvailable Vports:")

    for vport in ixnetwork.Vport.find():
        print(
            f"  Name={getattr(vport, 'Name', None)!r}, "
            f"href={getattr(vport, 'href', None)!r}, "
            f"AssignedTo={getattr(vport, 'AssignedTo', None)!r}, "
            f"IsMapped={getattr(vport, 'IsMapped', None)!r}, "
            f"ConnectionState={getattr(vport, 'ConnectionState', None)!r}"
        )


def find_vport_by_physical_port(ixnetwork, chassis, card, port):
    """
    Finds the Vport mapped to the chassis/card/port supplied by the user.

    It returns the Vport object, not a static REST URL.
    """
    target = f"{chassis}:{card}:{port}"
    matching_vports = []

    for vport in ixnetwork.Vport.find():
        assigned_to = str(getattr(vport, "AssignedTo", ""))

        if assigned_to.lower() == target.lower():
            matching_vports.append(vport)

    if len(matching_vports) == 0:
        show_vports(ixnetwork)
        fail(
            f"No mapped vport matches physical port {target!r}. "
            "Assign/connect C and D before running this script."
        )

    if len(matching_vports) > 1:
        show_vports(ixnetwork)
        fail(
            f"More than one Vport maps to physical port {target!r}. "
            "Exactly one Vport must be mapped to each physical test port."
        )

    vport = matching_vports[0]

    if not getattr(vport, "IsMapped", False):
        fail(
            f"Vport {vport.href!r} matches {target!r}, "
            "but IxNetwork reports IsMapped=False."
        )

    return vport


def raw_endpoint_from_alias(ixnetwork, alias):
    """
    Converts customer alias C/D into the raw Traffic Item endpoint object:

        /api/v1/sessions/<session>/ixnetwork/vport/<id>/protocols
    """
    if alias not in PORTS:
        fail(f"Unknown port alias {alias!r}. Valid aliases: {list(PORTS)}")

    port_definition = PORTS[alias]

    vport = find_vport_by_physical_port(
        ixnetwork=ixnetwork,
        chassis=port_definition["chassis"],
        card=port_definition["card"],
        port=port_definition["port"],
    )

    print(
        f"Resolved {alias}: "
        f"{expected_assigned_to(port_definition)} -> "
        f"{vport.href} -> {vport.Protocols.find().href}"
    )

    return vport.Protocols.find()


def find_single_traffic_item(ixnetwork, name):
    """
    Looks up exactly one traffic item by display name.
    """
    traffic_items = ixnetwork.Traffic.TrafficItem.find(
        Name=f"^{re.escape(name)}$"
    )

    if len(traffic_items) == 0:
        available = []

        for traffic_item in ixnetwork.Traffic.TrafficItem.find():
            available.append(
                {
                    "name": traffic_item.Name,
                    "traffic_type": traffic_item.TrafficType,
                    "traffic_item_type": traffic_item.TrafficItemType,
                    "href": traffic_item.href,
                }
            )

        fail(
            f"Traffic item {name!r} was not found. "
            f"Available traffic items: {available}"
        )

    if len(traffic_items) > 1:
        fail(
            f"More than one traffic item has the name {name!r}. "
            "Traffic-item names must be unique."
        )

    return traffic_items[0]


def display_endpoint_sets(traffic_item):
    """
    Shows the actual source/destination REST paths after conversion.
    """
    print(f"\nTraffic item: {traffic_item.Name!r}")
    print(f"TrafficType:  {traffic_item.TrafficType!r}")
    print(f"Object:       {traffic_item.href}")

    endpoint_sets = traffic_item.EndpointSet.find()

    for index, endpoint_set in enumerate(endpoint_sets, start=1):
        print(f"\nEndpointSet {index}: {endpoint_set.href}")
        print(f"  Sources:      {endpoint_set.Sources}")
        print(f"  Destinations: {endpoint_set.Destinations}")


def main():
    # -------------------------------------------------------------------------
    # 1. Connect to the existing IxNetwork session.
    # -------------------------------------------------------------------------
    session_assistant= SessionAssistant(IpAddress=IXNETWORK_API_SERVER, 
                                      RestPort=443, SessionId=SESSION_ID, 
                                      UserName=USERNAME, Password=PASSWORD, 
                                      LogLevel=SessionAssistant.LOGLEVEL_INFO, LogFilename="restpy.log", ClearConfig=False)
    session = session_assistant.TestPlatform.Sessions.find(Id=SESSION_ID)

    if len(session) == 0:
        sessions = session_assistant.TestPlatform.Sessions.find()

        available_ids = [getattr(item, "Id", None) for item in sessions]

        fail(
            f"Session ID {SESSION_ID} does not exist. "
            f"Available session IDs: {available_ids}"
        )

    if len(session) > 1:
        fail(f"More than one session matched ID={SESSION_ID!r}.")

    ixnetwork = session[0].Ixnetwork

    print(f"Connected to IxNetwork session: {session[0].href}")

    # -------------------------------------------------------------------------
    # 2. Find Ashjo — display only, not modified yet.
    # -------------------------------------------------------------------------
    traffic_item = find_single_traffic_item(ixnetwork, SOURCE_TRAFFIC_ITEM_NAME)
    print(f"\nFound {SOURCE_TRAFFIC_ITEM_NAME!r}:")
    display_endpoint_sets(traffic_item)

    # -------------------------------------------------------------------------
    # 3. Stop traffic — traffic config cannot be modified while running.
    # -------------------------------------------------------------------------
    traffic_state = getattr(ixnetwork.Traffic, "State", "unknown")
    print(f"\nTraffic state: {traffic_state!r}")
    if traffic_state not in ("stopped", "unapplied"):
        print("Stopping traffic...")
        try:
            ixnetwork.Traffic.StopStatelessTrafficBlocking()
        except Exception:
            ixnetwork.Traffic.Stop()
        print("Traffic stopped.")

    # -------------------------------------------------------------------------
    # 4. Remove leftovers from previous runs so re-runs are idempotent.
    #    ConvertToRaw() names its output "<Source> Raw (N)"; clean those too.
    # -------------------------------------------------------------------------
    leftover_pattern = (
        f"^({re.escape(CONVERTED_RAW_TRAFFIC_ITEM_NAME)}"
        f"|{re.escape(SOURCE_TRAFFIC_ITEM_NAME)} Raw \\(\\d+\\))$"
    )
    for leftover in ixnetwork.Traffic.TrafficItem.find(Name=leftover_pattern):
        print(f"Removing leftover traffic item {leftover.Name!r}...")
        leftover.remove()

    # -------------------------------------------------------------------------
    # 5. Convert Ashjo to raw.
    #
    # On IxNetwork 26.x ConvertToRaw() does NOT modify the source item.  It
    # creates a NEW item named "<Source> Raw (N)" and leaves the original
    # untouched.  Snapshot hrefs before/after to locate the new item.
    # -------------------------------------------------------------------------
    before_hrefs = {ti.href for ti in ixnetwork.Traffic.TrafficItem.find()}

    print(f"\nCalling ConvertToRaw() on {SOURCE_TRAFFIC_ITEM_NAME!r}...")
    traffic_item.ConvertToRaw()

    new_items = [
        ti for ti in ixnetwork.Traffic.TrafficItem.find()
        if ti.href not in before_hrefs
    ]

    if len(new_items) != 1:
        fail(
            f"Expected ConvertToRaw() to create exactly 1 new traffic item, "
            f"found {len(new_items)}: {[ti.Name for ti in new_items]}"
        )

    raw_item = new_items[0]
    print(f"ConvertToRaw() created {raw_item.Name!r} "
          f"(TrafficType={raw_item.TrafficType!r})")

    if str(raw_item.TrafficType).lower() != "raw":
        fail(f"New item {raw_item.Name!r} is not raw: {raw_item.TrafficType!r}")

    # -------------------------------------------------------------------------
    # 6. Resolve C and D to their vport /protocols hrefs.
    # -------------------------------------------------------------------------
    print("\nResolving C and D raw endpoints...")
    c_raw_endpoint = raw_endpoint_from_alias(ixnetwork, "C")
    d_raw_endpoint = raw_endpoint_from_alias(ixnetwork, "D")

    # -------------------------------------------------------------------------
    # 7. Swap endpoints to C/D on the NEW raw item.
    # -------------------------------------------------------------------------
    print("\nUpdating endpoints -> C/D...")
    endpoint_sets = raw_item.EndpointSet.find()

    if len(endpoint_sets) == 0:
        fail(f"No EndpointSet found on {raw_item.Name!r}.")

    for es in endpoint_sets:
        es.update(
            Sources=[c_raw_endpoint.href],
            Destinations=[d_raw_endpoint.href],
        )

    # -------------------------------------------------------------------------
    # 8. Rename to Ashjo-Raw-Traffic.
    # -------------------------------------------------------------------------
    raw_item.update(Name=CONVERTED_RAW_TRAFFIC_ITEM_NAME)

    raw_traffic_item = find_single_traffic_item(ixnetwork, CONVERTED_RAW_TRAFFIC_ITEM_NAME)

    print(f"\nFinal {CONVERTED_RAW_TRAFFIC_ITEM_NAME!r}:")
    display_endpoint_sets(raw_traffic_item)

    print("\nResolved physical ports:")
    # RestPy's find() filters on attributes, not href — build a lookup once.
    vports_by_href = {v.href: v for v in ixnetwork.Vport.find()}
    for index, endpoint_set in enumerate(raw_traffic_item.EndpointSet.find(), start=1):
        for label, hrefs in (("  Sources     ", endpoint_set.Sources),
                             ("  Destinations", endpoint_set.Destinations)):
            for href in hrefs:
                vport    = vports_by_href.get(href.rsplit("/protocols", 1)[0])
                assigned = vport.AssignedTo if vport else "?"
                vname    = vport.Name       if vport else "?"
                print(f"  EndpointSet {index} {label}: {assigned}  ({vname})")

    print(f"\nSuccess.")
    print(f"  {SOURCE_TRAFFIC_ITEM_NAME!r} — unchanged")
    print(f"  {CONVERTED_RAW_TRAFFIC_ITEM_NAME!r} — raw copy with C->D endpoints "
          f"(not generated/applied)")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        sys.exit(1)
