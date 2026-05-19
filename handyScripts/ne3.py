"""Network element (NE) REST automation for port latency / delay profiles.

API flow:
  - Login: ``GET /api`` with Basic auth → ``X-Auth-Token`` header
  - Set delay: ``PUT /api/hw/Port/{id}`` with minimal ``profiles`` body (lab format)
  - Verify: ``GET /api/hw/Port/{id}``

Delay is expressed as ``<value>`` + ``<unit>`` in ``ethernetDelay`` (e.g. ``150`` + ``MS``).
"""

from __future__ import annotations

import base64
import json
import logging
import re
import sys
import time
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)

# NE API unit codes → human-readable labels (configurable registry).
DELAY_UNITS: dict[str, str] = {
    "KM": "kilometer",
    "US": "microsecond",
    "MS": "millisecond",
    "NS": "nanosecond",
    "M": "meter",
}

# Default sequence: (value, unit) per step.
DELAY_STEPS: tuple[tuple[float, str], ...] = (
    (100, "MS"),
    (200, "MS"),
    (300, "MS"),
)


@dataclass(frozen=True)
class DelaySetting:
    """One delay target: numeric value plus NE unit code."""

    value: float
    unit: str

    def __post_init__(self) -> None:
        normalized = self.unit.upper()
        if normalized not in DELAY_UNITS:
            allowed = ", ".join(sorted(DELAY_UNITS))
            raise ValueError(f"Unknown unit {self.unit!r}. Allowed: {allowed}")
        object.__setattr__(self, "unit", normalized)

    def label(self) -> str:
        return f"{self.value:g} {self.unit}"

    @classmethod
    def from_tuple(cls, pair: tuple[float, str]) -> DelaySetting:
        return cls(pair[0], pair[1])

    @classmethod
    def parse(cls, raw: str) -> DelaySetting:
        """Parse ``<value>`` or ``<value> <UNIT>`` (e.g. ``150``, ``150 MS``, ``150MS``)."""
        text = raw.strip()
        if not text:
            raise ValueError("empty delay input")

        match = re.match(
            r"^([+-]?(?:\d+\.?\d*|\.\d+))\s*([A-Za-z]+)?$",
            text.replace(",", ""),
        )
        if not match:
            raise ValueError(
                f"invalid delay {raw!r} — use '<value>' or '<value> <UNIT>' "
                f"(e.g. 150 MS)"
            )

        value = float(match.group(1))
        unit_raw = match.group(2)
        if unit_raw is None:
            unit_raw = "MS"
        return cls(value, unit_raw.upper())


def _is_enabled(value: Any) -> bool:
    """NE API uses string ``\"true\"`` or JSON boolean — treat both as on."""
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def _normalize_unit(unit: str) -> str:
    code = unit.upper()
    if code not in DELAY_UNITS:
        allowed = ", ".join(f"{k} ({v})" for k, v in sorted(DELAY_UNITS.items()))
        raise ValueError(f"Unknown unit {unit!r}. Allowed: {allowed}")
    return code


def format_units_help() -> str:
    lines = [f"  {code:3} — {label}" for code, label in sorted(DELAY_UNITS.items())]
    return "Delay units:\n" + "\n".join(lines)


def prompt_delay_setting(prompt: str = "Delay (value UNIT)") -> DelaySetting:
    """Prompt until user enters a valid ``<value> <UNIT>``."""
    print(format_units_help())
    while True:
        raw = input(f"{prompt} [default unit MS]: ").strip()
        if not raw:
            print("  (required)\n")
            continue
        try:
            return DelaySetting.parse(raw)
        except ValueError as exc:
            print(f"  {exc}\n")


def prompt_delay_unit(default: str = "MS") -> str:
    """Prompt for unit code only."""
    print(format_units_help())
    while True:
        raw = input(f"Unit [{default}]: ").strip().upper() or default
        try:
            return _normalize_unit(raw)
        except ValueError as exc:
            print(f"  {exc}\n")


class NEClient:
    """REST client for NE hardware port delay (ethernetDelay) configuration."""

    DEFAULT_TIMEOUT_S = 30

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        *,
        use_https: bool = False,
        timeout: float = DEFAULT_TIMEOUT_S,
        verify_tls: bool = True,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self._scheme = "https" if use_https else "http"
        self._timeout = timeout
        self._verify_tls = verify_tls
        self._session = requests.Session()
        self._auth_token: str | None = None

    @property
    def base_url(self) -> str:
        return self._scheme + "://" + self.host + "/api"

    def _port_url(self, port_id: int) -> str:
        return self.base_url + "/hw/Port/" + str(port_id)

    def authenticate(self) -> str:
        user_pass = self.username + ":" + self.password
        base64_user_pass = base64.b64encode(user_pass.encode())
        request_headers = {
            "Authorization": "Basic " + base64_user_pass.decode(),
            "Content-Type": "application/json",
        }
        request_url = self._scheme + "://" + self.host + "/api"
        response = requests.get(
            request_url,
            headers=request_headers,
            timeout=self._timeout,
            verify=self._verify_tls,
        )
        auth_token = response.headers.get("X-Auth-Token")
        if not auth_token:
            raise RuntimeError(
                f"Login failed (HTTP {response.status_code}): "
                f"{(response.text or '')[:300]!r}"
            )
        self._auth_token = auth_token
        logger.info("Authenticated to %s", self.host)
        return auth_token

    def _token_headers(self) -> dict[str, str]:
        if not self._auth_token:
            raise RuntimeError("Not authenticated; call authenticate() first")
        return {
            "Authorization": "Token " + self._auth_token,
            "Content-Type": "application/json",
        }

    @staticmethod
    def build_delay_put_payload(
        profile_tag: str,
        delay: DelaySetting | float,
        *,
        units: str | None = None,
    ) -> str:
        """Build PUT body exactly like the working lab script.

        Only the ``profiles`` array is sent — not the full port document.
        ``enabled`` values are the string ``\"true\"`` (required for UI apply).
        """
        if isinstance(delay, DelaySetting):
            delay_value = delay.value
            unit_code = delay.unit
        else:
            delay_value = float(delay)
            unit_code = _normalize_unit(units or "MS")

        body = {
            "profiles": [
                {
                    "tag": profile_tag,
                    "enabled": "true",
                    "ethernetDelay": {
                        "delay": delay_value,
                        "pdvMode": "NONE",
                        "units": unit_code,
                        "enabled": "true",
                    },
                }
            ]
        }
        return json.dumps(body)

    def set_profile_delay(
        self,
        port_id: int,
        profile_tag: str,
        delay: DelaySetting | float,
        *,
        units: str | None = None,
    ) -> requests.Response:
        """PUT delay using the lab minimal-payload format."""
        request_url = self._port_url(port_id)
        request_payload = self.build_delay_put_payload(
            profile_tag, delay, units=units
        )

        logger.debug("PUT %s payload=%s", request_url, request_payload)
        response = self._session.put(
            request_url,
            headers=self._token_headers(),
            data=request_payload,
            timeout=self._timeout,
            verify=self._verify_tls,
        )
        return response

    def get_port_config(self, port_id: int) -> dict[str, Any]:
        """GET /api/hw/Port/{logical_id} — retrieve port config for verify."""
        response = self._session.get(
            self._port_url(port_id),
            headers=self._token_headers(),
            timeout=self._timeout,
            verify=self._verify_tls,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def find_profile(
        config: dict[str, Any], profile_tag: str
    ) -> dict[str, Any] | None:
        for profile in config.get("profiles", []):
            if profile.get("tag") == profile_tag:
                return profile
        return None

    @staticmethod
    def read_profile_ethernet_delay(
        config: dict[str, Any], profile_tag: str
    ) -> dict[str, Any] | None:
        profile = NEClient.find_profile(config, profile_tag)
        if not profile:
            return None
        eth = profile.get("ethernetDelay")
        return eth if isinstance(eth, dict) else None

    @staticmethod
    def read_delay_setting(
        config: dict[str, Any], profile_tag: str
    ) -> DelaySetting | None:
        eth = NEClient.read_profile_ethernet_delay(config, profile_tag)
        if not eth or eth.get("delay") is None:
            return None
        unit = str(eth.get("units", "MS")).upper()
        return DelaySetting(float(eth["delay"]), unit)

    @staticmethod
    def print_profile_table(config: dict[str, Any]) -> None:
        """Show all profiles — helps match what the NE UI is displaying."""
        print("  Profiles on port:")
        for profile in config.get("profiles", []):
            tag = profile.get("tag")
            eth = profile.get("ethernetDelay") or {}
            print(
                f"    {tag!r}: profile.enabled={profile.get('enabled')!r} "
                f"| ethernetDelay.enabled={eth.get('enabled')!r} "
                f"| delay={eth.get('delay')} {eth.get('units', '')}"
            )

    @staticmethod
    def format_verify_line(
        config: dict[str, Any],
        profile_tag: str,
        expected: DelaySetting,
    ) -> str:
        eth = NEClient.read_profile_ethernet_delay(config, profile_tag)
        if not eth:
            return f"[MISSING] profile {profile_tag!r} not in GET response"

        actual_delay = eth.get("delay")
        actual_unit = str(eth.get("units", "")).upper()
        actual_f = float(actual_delay) if actual_delay is not None else None
        eth_on = _is_enabled(eth.get("enabled"))
        prof = NEClient.find_profile(config, profile_tag)
        prof_on = _is_enabled(prof.get("enabled")) if prof else False

        delay_ok = (
            actual_f is not None
            and abs(actual_f - expected.value) < 0.01
            and actual_unit == expected.unit
        )
        apply_ok = delay_ok and eth_on and prof_on
        status = "OK" if apply_ok else "CHECK"

        return (
            f"[{status}] expected={expected.label()} | "
            f"GET delay={actual_delay} {actual_unit} | "
            f"profile.enabled={prof.get('enabled') if prof else None} | "
            f"ethernetDelay.enabled={eth.get('enabled')!r} | "
            f"pdvMode={eth.get('pdvMode')}"
        )

    def update_profile_delay(
        self,
        port_id: int,
        profile_tag: str,
        delay: DelaySetting | float,
        *,
        units: str | None = None,
    ) -> dict[str, Any]:
        """Set delay via lab PUT, then GET to confirm."""
        response = self.set_profile_delay(
            port_id, profile_tag, delay, units=units
        )
        print(f"  PUT HTTP {response.status_code}")
        if response.status_code >= 400:
            print(f"  PUT body: {response.text[:500]}")
            response.raise_for_status()

        return self.get_port_config(port_id)

    def apply_delay_sequence(
        self,
        port_id: int,
        profile_tag: str,
        steps: tuple[DelaySetting, ...] | tuple[tuple[float, str], ...] = DELAY_STEPS,
        *,
        pause_s: float = 2.0,
    ) -> None:
        """Apply each (value, unit) step and GET-verify after every PUT."""
        normalized: list[DelaySetting] = []
        for step in steps:
            if isinstance(step, DelaySetting):
                normalized.append(step)
            else:
                normalized.append(DelaySetting.from_tuple(step))

        step_labels = ", ".join(s.label() for s in normalized)
        print(
            f"\nPort {port_id} | profile {profile_tag!r} | steps: {step_labels}"
        )
        print("PUT uses minimal lab payload (profiles only, enabled='true')\n")

        for step_no, setting in enumerate(normalized, start=1):
            print(f"--- Step {step_no}/{len(normalized)}: {setting.label()} ---")
            print(
                f"  Payload: {self.build_delay_put_payload(profile_tag, setting)}"
            )

            self.update_profile_delay(port_id, profile_tag, setting)

            if pause_s > 0:
                time.sleep(pause_s)

            verified = self.get_port_config(port_id)
            print("  " + self.format_verify_line(verified, profile_tag, setting))
            self.print_profile_table(verified)
            print()

    def interactive_delay_loop(
        self,
        port_id: int,
        profile_tag: str,
    ) -> None:
        """Prompt for ``<value> <UNIT>``, confirm, PUT, GET-verify."""
        print(f"\n--- Delay loop: port {port_id}, profile {profile_tag!r} ---")
        print("Enter delay as '<value> <UNIT>' (e.g. 150 MS), or 'q' to quit.\n")

        while True:
            try:
                config = self.get_port_config(port_id)
            except requests.HTTPError as exc:
                print(f"Failed to read port config: {exc}")
                return

            current = self.read_delay_setting(config, profile_tag)
            if current:
                print(f"Current on NE: {current.label()}")
            else:
                print(f"Profile {profile_tag!r} not found or has no ethernetDelay.")
            self.print_profile_table(config)
            print()

            raw = input("New delay (value UNIT) [q=quit]: ").strip()
            if raw.lower() in {"q", "quit", "exit"}:
                print("Exiting delay loop.")
                break

            try:
                setting = DelaySetting.parse(raw)
            except ValueError as exc:
                print(f"  {exc}\n")
                continue

            confirm = input(f"Apply {setting.label()} to {profile_tag!r}? [y/N]: ")
            if confirm.strip().lower() not in {"y", "yes"}:
                print("Skipped.\n")
                continue

            try:
                updated = self.update_profile_delay(
                    port_id, profile_tag, setting
                )
            except (ValueError, requests.HTTPError) as exc:
                print(f"Apply failed: {exc}\n")
                continue

            print("Confirmed after PUT + GET:")
            print("  " + self.format_verify_line(updated, profile_tag, setting))
            print()

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> NEClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _parse_cli_steps(argv: list[str]) -> tuple[DelaySetting, ...] | None:
    """Optional 4th arg: comma-separated steps like ``100:MS,200:MS,300:MS``."""
    if len(argv) < 5:
        return None
    steps: list[DelaySetting] = []
    for part in argv[4].split(","):
        part = part.strip()
        if ":" in part:
            val_s, unit = part.split(":", 1)
            steps.append(DelaySetting(float(val_s), unit))
        else:
            steps.append(DelaySetting(float(part), "MS"))
    return tuple(steps)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # python ne3.py [host] [port_id] [profile_tag] [100:MS,200:MS,300:MS]
    host = sys.argv[1] if len(sys.argv) > 1 else "10.36.84.18"
    port_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    profile_tag = sys.argv[3] if len(sys.argv) > 3 else "Port1-msoftProfile"
    cli_steps = _parse_cli_steps(sys.argv)

    print("\nOperations:")
    print("  1) Run configured delay sequence (GET verify each step)")
    print("  2) Interactive delay loop (enter value + unit each time)")
    print("  3) Both — sequence, then interactive loop")
    choice = input("Choose [1]: ").strip() or "1"

    with NEClient(host, "admin", "admin") as client:
        client.authenticate()
        print(f"Logged in to {host}\n")

        before = client.get_port_config(port_id)
        print("Before:")
        client.print_profile_table(before)
        print()

        if choice in {"1", "3"}:
            steps = cli_steps if cli_steps else DELAY_STEPS
            client.apply_delay_sequence(port_id, profile_tag, steps)

        if choice in {"2", "3"}:
            client.interactive_delay_loop(port_id, profile_tag)


if __name__ == "__main__":
    main()

""" Sample Output:

ashwin.joshi@KJ4FGV207R ~ % /usr/local/bin/python3 /Users/ashwin.joshi/ne3.py

Operations:
  1) Run configured delay sequence (GET verify each step)
  2) Interactive delay loop (enter value + unit each time)
  3) Both — sequence, then interactive loop
Choose [1]: 1
INFO:__main__:Authenticated to 10.36.84.18
Logged in to 10.36.84.18

Before:
  Profiles on port:
    'Port1-msoftProfile': profile.enabled=True | ethernetDelay.enabled=True | delay=200.0 MS


Port 1 | profile 'Port1-msoftProfile' | steps: 100 MS, 200 MS, 300 MS
PUT uses minimal lab payload (profiles only, enabled='true')

--- Step 1/3: 100 MS ---
  Payload: {"profiles": [{"tag": "Port1-msoftProfile", "enabled": "true", "ethernetDelay": {"delay": 100, "pdvMode": "NONE", "units": "MS", "enabled": "true"}}]}
  PUT HTTP 200
  [OK] expected=100 MS | GET delay=100.0 MS | profile.enabled=True | ethernetDelay.enabled=True | pdvMode=NONE
  Profiles on port:
    'Port1-msoftProfile': profile.enabled=True | ethernetDelay.enabled=True | delay=100.0 MS

--- Step 2/3: 200 MS ---
  Payload: {"profiles": [{"tag": "Port1-msoftProfile", "enabled": "true", "ethernetDelay": {"delay": 200, "pdvMode": "NONE", "units": "MS", "enabled": "true"}}]}
  PUT HTTP 200
  [OK] expected=200 MS | GET delay=200.0 MS | profile.enabled=True | ethernetDelay.enabled=True | pdvMode=NONE
  Profiles on port:
    'Port1-msoftProfile': profile.enabled=True | ethernetDelay.enabled=True | delay=200.0 MS

--- Step 3/3: 300 MS ---
  Payload: {"profiles": [{"tag": "Port1-msoftProfile", "enabled": "true", "ethernetDelay": {"delay": 300, "pdvMode": "NONE", "units": "MS", "enabled": "true"}}]}
  PUT HTTP 200
  [OK] expected=300 MS | GET delay=300.0 MS | profile.enabled=True | ethernetDelay.enabled=True | pdvMode=NONE
  Profiles on port:
    'Port1-msoftProfile': profile.enabled=True | ethernetDelay.enabled=True | delay=300.0 MS

ashwin.joshi@KJ4FGV207R ~ % 
"""
