# C4 Model — full reference

The [C4 model](https://c4model.com) describes software architecture at four levels of detail. Each level has its own audience and purpose. Most systems need Levels 1 and 2; Level 3 when the system is non-trivial; Level 4 rarely earns its keep.

## Level 1 — System Context

**Purpose**: show how the system fits into its environment.
**Audience**: everyone — engineers, product, executives, external integrators.
**Elements**: the system as a single box, the people who use it, the external systems it integrates with.

This is the "elevator pitch in diagram form". It should be readable by anyone with five seconds and no prior context.

```d2
direction: right
vars: { d2-config: { layout-engine: elk, theme-id: 0 } }

customer: Customer { shape: c4-person }
admin: Admin { shape: c4-person }

system: E-commerce System {
  shape: rectangle
  style.fill: "#1168bd"
  style.font-color: white
}

stripe: Stripe { shape: rectangle }
sendgrid: SendGrid { shape: rectangle }

customer -> system: "Browses, buys"
admin -> system: "Manages catalog"
system -> stripe: "Processes payments"
system -> sendgrid: "Sends order email"
```

## Level 2 — Container

**Purpose**: show high-level technology choices and how containers communicate.
**Audience**: technical stakeholders.
**Elements**: deployable units (web app, API, mobile app, database, message broker, etc.), the protocols they use to talk, and the data each holds.

A "container" in C4 means *something that runs on its own* (a process, a database, a serverless function) — not a Docker container, although a Docker container is one example.

```d2
direction: right
vars: { d2-config: { layout-engine: elk, theme-id: 0 } }

customer: Customer { shape: c4-person }

system: E-commerce System {
  web: Web App {
    description: "React SPA"
  }
  api: API {
    description: "Node.js / Express"
  }
  workers: Background Workers {
    description: "Python / Celery"
  }
  db: Postgres {
    shape: cylinder
  }
  queue: Redis {
    shape: cylinder
    description: "Queue + cache"
  }
}

customer -> system.web: "HTTPS"
system.web -> system.api: "JSON / REST"
system.api -> system.db: "SQL"
system.api -> system.queue: "enqueue jobs"
system.workers -> system.queue: "consume"
system.workers -> system.db: "SQL"
```

## Level 3 — Component

**Purpose**: show the major building blocks inside a single container.
**Audience**: architects, senior developers.
**Elements**: components (modules / packages / services-within-a-service) and their responsibilities and interfaces.

You'd produce a Level 3 diagram per container that's complex enough to warrant one. A simple CRUD container probably doesn't need one; a domain-heavy service does.

## Level 4 — Code

**Purpose**: show class / module structure inside a component.
**Audience**: developers.
**Elements**: classes, functions, key data structures.

This level is **usually skipped**. The code itself is the source of truth and Level 4 diagrams go stale instantly. Generate them on-demand from the code (UML class diagrams from an IDE, dependency graphs from a tool) rather than maintaining them by hand.

## What to put where

| Question | Level | Notes |
|----------|-------|-------|
| Who uses it and what does it talk to? | 1 — Context | Always |
| What runs where, and what tech is each piece? | 2 — Container | Always |
| What's inside this service? | 3 — Component | When the service is non-trivial |
| How is this class organized? | 4 — Code | Skip unless you have a specific reason |

## Common pitfalls

- **Mixing levels in one diagram**: putting a class from Level 4 next to a person from Level 1 makes the diagram unreadable. Pick a level per diagram and stick to it.
- **Calling deployments "containers"**: C4 uses "container" to mean *runnable unit*, which is broader than Docker. A Postgres database is a container; a serverless function is a container; a mobile app is a container. There's a separate **Deployment Diagram** for showing where things actually run on infrastructure.
- **Showing every external system at Level 1**: only show the externals that are core to the system's purpose. Three or four boxes around the central system is healthy; twenty boxes is unreadable.
- **Drift**: a Level 2 diagram that doesn't match the actual deployed services is worse than no diagram. Either keep it current or remove it.

## File naming

```
docs/architecture/
├── c4-context.md           # Level 1
├── c4-container.md         # Level 2
├── c4-component-[service].md  # Level 3, one per non-trivial service
└── deployment.md           # How containers map to infrastructure
```

## Tools

- **D2** (`aeo-docs:d2` skill) — has `shape: c4-person` and produces clean C4 output. Recommended.
- **Mermaid** — works for simple C4-flavored diagrams via generic graph syntax, but lacks the c4-person shape and produces less canonical output.
- **Structurizr** — purpose-built for C4 with its own DSL. Good for large architectures with many views from the same model. Outside the scope of these skills.
