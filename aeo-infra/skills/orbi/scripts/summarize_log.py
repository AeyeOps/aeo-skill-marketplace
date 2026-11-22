"""Summarize an Orbi activity log locally, omitting all free-form event details."""

import argparse
import codecs
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Entry:
    event_class: str
    timestamp: datetime | None


class LogTextarea(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_log = False
        self.found_log = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "textarea":
            self.inside_log = any(
                key in {"id", "name"} and value == "log_detail" for key, value in attrs
            )
            self.found_log |= self.inside_log
        elif tag == "br" and self.inside_log:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "textarea" and self.inside_log:
            self.parts.append("\n")
            self.inside_log = False

    def handle_data(self, data):
        if self.inside_log:
            self.parts.append(data)


MONTH_NAMES = (
    "January February March April May June July August September October November December"
).split()
MONTH_NUMBERS = {name[:3].lower(): number for number, name in enumerate(MONTH_NAMES, 1)}
MONTH_PATTERN = "|".join(name + "|" + name[:3] for name in MONTH_NAMES)
SEP = r"(?:\s*,\s*|\s+)"
CLOCK = r"\d{1,2}:\d{2}:\d{2}"
TIMESTAMP = re.compile(
    rf"\b(?P<month>{MONTH_PATTERN}|Sept)\.?\s+(?P<day>\d{{1,2}}){SEP}"
    rf"(?:(?P<year>\d{{4}}){SEP}(?P<clock>{CLOCK})"
    rf"|(?P<clock_first>{CLOCK}){SEP}(?P<year_last>\d{{4}}))\s*$",
    re.IGNORECASE,
)
BR = re.compile(r"<br\s*/?\s*>", re.IGNORECASE)

# Match only the event label. Device names, addresses and other free text never
# become class names and cannot turn an unrelated row into a configuration event.
EVENT_PATTERNS = [
    ("admin_login_failed", r"admin login (?:failure|failed)\b"),
    ("admin_login", r"admin login\b"),
    ("admin_logout", r"admin logout\b"),
    ("wireless_settings", r"(?:wlan|wi-?fi|wireless) (?:config(?:uration)?|settings?)\b"),
    ("configuration", r"(?:configuration|config|settings?) (?:change[ds]?|update[ds]?|applied|restored)\b"),
    ("firmware", r"firmware (?:update|upgrade|version)\b"),
    ("restart", r"(?:initialized\b|(?:system |router )?(?:reboot|restart)(?:ed|ing)?\b)"),
    ("wireless_access", r"(?:wlan|wi-?fi|wireless) (?:access|association|disassociation|connect|disconnect)\w*\b"),
    ("satellite", r"(?:(?:orbi )?satellite|backhaul)\b"),
    ("internet_connected", r"internet connected\b"),
    ("internet_disconnected", r"internet disconnected\b"),
    ("time_sync", r"(?:time synchronized|ntp)\b"),
    ("dhcp", r"dhcp\b"),
    ("access_control", r"(?:access control|site blocked|site allowed|service blocked)\b"),
    ("security_alert", r"(?:dos attack|security alert|attack detected)\b"),
    ("log_cleared", r"log cleared\b"),
]
EVENT_PATTERNS = [(name, re.compile(pattern, re.I)) for name, pattern in EVENT_PATTERNS]
TIMED_EVENTS = {
    "admin_login", "admin_login_failed", "admin_logout", "configuration",
    "firmware", "internet_connected", "internet_disconnected", "log_cleared",
    "restart", "satellite", "time_sync", "wireless_access", "wireless_settings",
}


def _timestamp(line: str) -> datetime | None:
    match = TIMESTAMP.search(line)
    if match is None:
        return None
    clock = match["clock"] or match["clock_first"]
    try:
        return datetime(
            int(match["year"] or match["year_last"]),
            MONTH_NUMBERS[match["month"][:3].lower()],
            int(match["day"]),
            *map(int, clock.split(":")),
        )
    except ValueError:
        # Keep a row with an invalid router date in the undated count.
        return None


def parse_entries(source: str) -> list[Entry]:
    """Read a log_detail textarea or one event per nonblank line of pasted text."""
    source = source.lstrip("\ufeff \t\r\n")
    if source.startswith("<") and not BR.match(source):
        parser = LogTextarea()
        parser.feed(source)
        parser.close()
        if not parser.found_log:
            raise ValueError("The HTML does not contain a log_detail textarea.")
        source = "".join(parser.parts)

    entries = []
    for raw_line in BR.sub("\n", source).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        label = re.match(r"\[([^\]]+)\]", line)
        event_class = "other"
        if label:
            event_class = next(
                (name for name, pattern in EVENT_PATTERNS if pattern.match(label[1].strip())),
                "other",
            )
        entries.append(Entry(event_class, _timestamp(line)))
    return entries


def summarize(entries: list[Entry], target_date: date | None = None) -> dict:
    """Return the full retained bounds and counts for the selected router-local date."""
    timestamps = [entry.timestamp for entry in entries if entry.timestamp is not None]
    counts = Counter()
    times = defaultdict(list)
    for entry in entries:
        stamp = entry.timestamp
        if target_date is not None and (stamp is None or stamp.date() != target_date):
            continue
        counts[entry.event_class] += 1
        if stamp is not None and entry.event_class in TIMED_EVENTS:
            times[entry.event_class].append(stamp.isoformat())
    return {
        "retained_entries": len(entries),
        "earliest": min(timestamps).isoformat() if timestamps else None,
        "latest": max(timestamps).isoformat() if timestamps else None,
        "unknown_timestamp_entries": len(entries) - len(timestamps),
        "date_filter": target_date.isoformat() if target_date else None,
        "selected_entries": sum(counts.values()),
        "event_counts": dict(sorted(counts.items())),
        "event_times": {name: sorted(stamps) for name, stamps in sorted(times.items())},
    }


def _date_arg(value: str) -> date:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError("Use a valid date in YYYY-MM-DD format.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default="-", help="Log file, or - for stdin (default)")
    parser.add_argument("--date", type=_date_arg, help="Filter events by router-local date (YYYY-MM-DD)")
    args = parser.parse_args()
    try:
        data = sys.stdin.buffer.read() if args.file == "-" else Path(args.file).read_bytes()
    except OSError:
        parser.exit(2, "Could not read the log input.\n")
    encoding = "utf-16" if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)) else "utf-8-sig"
    try:
        entries = parse_entries(data.decode(encoding))
    except UnicodeDecodeError:
        parser.exit(2, "Use UTF-8 or UTF-16 with a byte order mark for log input.\n")
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")
    print(json.dumps(summarize(entries, args.date), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
