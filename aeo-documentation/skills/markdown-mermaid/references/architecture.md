# Architecture Diagrams

**Keyword:** `architecture-beta`

**Purpose:** Cloud/CI-CD service and infrastructure visualization.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Groups](#groups)
- [Services](#services)
- [Edges](#edges)
- [Junctions](#junctions)
- [Icons](#icons)
- [Icon and Label Syntax](#icon-and-label-syntax)
- [Key Limitations](#key-limitations)
- [When to Use](#when-to-use)

## Basic Syntax

```mermaid
architecture-beta
    service web(internet)[Web Server]
    service api(server)[API Gateway]
    service db(database)[Database]

    web:R --> L:api
    api:R --> L:db
```

## Groups

```mermaid
architecture-beta
    group backend(cloud)[Backend Services]

    service api(server)[API] in backend
    service db(database)[Database] in backend
```

**Nested groups:**
```mermaid
architecture-beta
    group cloud(cloud)[Cloud]
    group k8s(server)[Kubernetes] in cloud

    service app(server)[App] in k8s
```

## Services

```mermaid
architecture-beta
    service name(icon)[Label]
    service name(icon)[Label] in groupId
```

## Edges

**Syntax:** `serviceId{group}?:SIDE <-->? SIDE:serviceId{group}?`

**Sides:** `T` (top), `B` (bottom), `L` (left), `R` (right)

```mermaid
architecture-beta
    service A(server)[Service A]
    service B(server)[Service B]

    A:R --> L:B
    A:B <--> T:B
```

**Group connections:**
```mermaid
architecture-beta
    group g1(cloud)[Group 1]
    group g2(cloud)[Group 2]
    service A(server)[A] in g1
    service B(server)[B] in g2

    A{g1}:R --> L:B{g2}
```

## Junctions

```mermaid
architecture-beta
    junction j1
    service A(server)[A]
    service B(server)[B]
    service C(server)[C]

    A:R --> L:j1
    j1:R --> L:B
    j1:B --> T:C
```

## Icons

**Default icons:**
- `cloud`
- `database`
- `disk`
- `internet`
- `server`

**Iconify icons (200,000+):**
```yaml
---
config:
  architecture:
    iconifyPacks:
      - mdi
---
architecture-beta
    service app(mdi:application)[Application]
```

**Format:** `packname:icon-name`

## Icon and Label Syntax

- Icons: `(icon-name)`
- Labels: `[Label Text]`

## Key Limitations
- Beta feature
- Limited default icons (must register packs)
- Manual positioning required

## When to Use
- Cloud architecture diagrams
- CI/CD pipeline visualization
- Microservices topology
- Infrastructure documentation
