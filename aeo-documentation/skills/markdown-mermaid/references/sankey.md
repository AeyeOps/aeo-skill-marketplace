# Sankey Diagrams

**Keyword:** `sankey-beta`

**Purpose:** Visualize flow quantities between nodes.

## Basic Syntax

```mermaid
sankey-beta
Source,Target,Value
A,B,100
A,C,50
B,D,75
C,D,25
```

## CSV Format Requirements

- **3 columns:** source, target, value
- **RFC 4180 compliant** with modifications
- **Empty lines allowed** (without commas)
- **Commas in text:** Wrap in double quotes
- **Double quotes:** Escape by doubling (`""`)

**Example:**
```mermaid
sankey-beta
"Node, with comma",NodeB,50
NodeC,"Another, comma",30
```

## Configuration

**Link colors:**
```yaml
---
config:
  sankey:
    linkColor: gradient
---
sankey-beta
A,B,100
```

Options:
- `source` - Inherit source node color
- `target` - Inherit target node color
- `gradient` - Smooth transition
- Hex codes: `#ff0000`

**Node alignment:**
```yaml
config:
  sankey:
    nodeAlignment: justify
```

Options: `justify`, `center`, `left`, `right`

**Dimensions:**
```yaml
config:
  sankey:
    width: 800
    height: 600
```

## Key Limitations
- Exactly 3 CSV columns required
- Experimental feature (v10.3.0+)
- Limited customization vs dedicated tools

## When to Use
- Energy flow diagrams
- Material flow analysis
- Budget allocation
- Traffic visualization
