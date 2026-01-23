# Packet Diagrams

**Keyword:** `packet-beta`

**Purpose:** Network packet structure visualization.

## Basic Syntax

```mermaid
packet-beta
0-7: "Header"
8-15: "Flags"
16-31: "Payload"
```

## Bit Range Notation

**Traditional (absolute):**
```mermaid
packet-beta
0: "Bit 0"
1-7: "Bits 1-7"
8-15: "Byte 2"
16-31: "Bytes 3-4"
```

**Modern (relative, v11.7.0+):**
```mermaid
packet-beta
+1: "Single bit"
+8: "One byte"
+16: "Two bytes"
```

**Mixed notation:**
```mermaid
packet-beta
0-7: "Header"
+8: "Type"
16-31: "Length"
```

## Configuration

```yaml
---
config:
  packet:
    bitsPerRow: 32
    bitWidth: 10
    rowHeight: 32
    paddingX: 5
    paddingY: 5
    showBits: true
---
packet-beta
0-7: "Field A"
8-15: "Field B"
```

**Options:**
- `bitsPerRow` - Bits displayed per row (default: 32)
- `bitWidth` - Individual bit width in pixels
- `rowHeight` - Vertical spacing
- `paddingX/Y` - Margins
- `showBits` - Toggle bit number visibility

## Example: IPv4 Header

```mermaid
packet-beta
0-3: "Version"
4-7: "IHL"
8-15: "Type of Service"
16-31: "Total Length"
32-47: "Identification"
48-50: "Flags"
51-63: "Fragment Offset"
64-71: "TTL"
72-79: "Protocol"
80-95: "Header Checksum"
96-127: "Source Address"
128-159: "Destination Address"
```

## Key Limitations
- Fixed row-based layout
- Limited styling options
- Best for standard packet formats

## When to Use
- Network protocol documentation
- Packet format specification
- Protocol analysis
- Educational materials
