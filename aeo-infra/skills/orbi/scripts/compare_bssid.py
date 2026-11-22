"""Compare a repeater's saved upstream against one CSV survey."""

import argparse
import csv
from pathlib import Path
import re


def normalize_bssid(value):
    value = value.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{2}([:-])[0-9a-f]{2}(?:\1[0-9a-f]{2}){4}", value):
        raise ValueError(f"invalid BSSID {value!r}, expected six colon- or hyphen-separated hex pairs")
    return value.replace("-", ":")


def normalize_band(value):
    match = re.fullmatch(r"(2\.4|5|6)\s*(?:g|ghz)?", value.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"invalid band {value!r}, expected 2.4, 5 or 6 GHz")
    return match[1] + " GHz"


def read_survey(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if sorted(reader.fieldnames or []) != ["band", "bssid", "channel", "ssid"]:
            raise ValueError("CSV header must contain ssid,bssid,band,channel exactly once")
        rows = []
        for row in reader:
            try:
                if None in row or None in row.values():
                    raise ValueError("wrong number of CSV fields")
                channel = row["channel"].strip()
                if not re.fullmatch(r"[0-9]+", channel) or int(channel) <= 0:
                    raise ValueError(f"invalid channel {channel!r}, expected a positive integer")
                rows.append((row["ssid"], normalize_bssid(row["bssid"]), normalize_band(row["band"]), int(channel)))
            except ValueError as error:
                raise ValueError(f"CSV line {reader.line_num}: {error}") from error
    return rows


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Example: python compare_bssid.py survey.csv --ssid 'Example WiFi' "
            "--bssid 02:00:00:00:00:01 --band 5GHz\n\n"
            "UTF-8 CSV example:\nssid,bssid,band,channel\nExample WiFi,02:00:00:00:00:01,5 GHz,36\n\n"
            "SSID matching is exact. Exit 0 means the survey was compared; exit 2 means invalid input."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("survey", type=Path, help="CSV snapshot from the repeater's location")
    parser.add_argument("--ssid", required=True, help="saved SSID (case and spaces are significant)")
    parser.add_argument("--bssid", required=True, help="saved upstream BSSID")
    parser.add_argument("--band", help="saved band, if known (2.4, 5 or 6 GHz)")
    args = parser.parse_args()
    try:
        if not args.ssid:
            raise ValueError("supply the saved SSID")
        bssid = normalize_bssid(args.bssid)
        band = normalize_band(args.band) if args.band is not None else None
        rows = read_survey(args.survey)
    except (OSError, csv.Error, ValueError) as error:
        parser.error(str(error))

    same_bssid = [row for row in rows if row[1] == bssid]
    exact = [row for row in same_bssid if row[0] == args.ssid]
    if exact:
        if band and all(row[2] != band for row in exact):
            status = "BAND_MISMATCH"
        else:
            status = "OBSERVED"
    elif same_bssid:
        status = "BSSID_OBSERVED_WITHOUT_SAVED_SSID"
    else:
        status = "ABSENT_IN_SURVEY"

    print(f"{status} | saved SSID={ascii(args.ssid)} BSSID={bssid} band={band or 'unspecified'}")
    for ssid, mac, radio, channel in sorted(set(same_bssid)):
        print(f"  saved BSSID observed: SSID={ascii(ssid)} BSSID={mac} band={radio} channel={channel}")
    alternatives = {(mac, radio, channel) for ssid, mac, radio, channel in rows if ssid == args.ssid and mac != bssid}
    print("Other BSSIDs for the saved SSID:" + ("" if alternatives else " none in survey"))
    for mac, radio, channel in sorted(alternatives):
        print(f"  {mac} band={radio} channel={channel}")


if __name__ == "__main__":
    main()
