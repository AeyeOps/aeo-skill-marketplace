# TRD Discovery Phases

Six structured interview phases for technical requirements discovery.

## Phase 1: Architecture & Patterns

**Goal**: Define high-level structure and component organization.

**Context**: Research with WebSearch/WebFetch("[architecture] patterns 2025"), explore with /epcc-explore (brownfield).

**Use AskUserQuestion for**:
```typescript
// Architecture Pattern
{
  question: "What architectural pattern fits your project?",
  header: "Architecture",
  options: [
    {label: "Monolith", description: "Single codebase, simpler deployment, good for small teams, faster initial development"},
    {label: "Microservices", description: "Independent services, complex deployment, team autonomy, scales components independently"},
    {label: "Serverless", description: "Function-based, auto-scaling, pay-per-use, less infrastructure management"},
    {label: "JAMstack", description: "Static generation + APIs, excellent performance, simple hosting, limited dynamic features"}
  ]
}

// Design Patterns (if complex project)
{
  question: "What design patterns are important for your system?",
  header: "Patterns",
  multiSelect: true,
  options: [
    {label: "Event-driven", description: "Async communication, decoupled components, eventual consistency"},
    {label: "CQRS", description: "Separate read/write models, optimized queries, complex to implement"},
    {label: "Repository", description: "Data access abstraction, testable, clean architecture"},
    {label: "Factory", description: "Object creation patterns, dependency injection, flexible instantiation"}
  ]
}
```

**Converse about**: Component structure, service boundaries (if microservices), data flow between components.

**From PRD.md (if available)**: Features → Architectural needs (real-time? background jobs? file processing?)

## Phase 2: Technology Stack & Infrastructure

**Goal**: Select languages, frameworks, hosting, and deployment approach.

**Context**: Research with WebSearch/WebFetch("[tech-stack] best practices 2025"), explore with /epcc-explore (brownfield).

**Use AskUserQuestion for**:
```typescript
// Backend Language
{
  question: "What backend language/runtime fits your needs?",
  header: "Backend",
  options: [
    {label: "Node.js", description: "JavaScript/TypeScript, async I/O, npm ecosystem, good for APIs"},
    {label: "Python", description: "Django/Flask/FastAPI, AI/ML libraries, readable, slower than compiled"},
    {label: "Go", description: "Compiled, fast, simple concurrency, strong typing, smaller ecosystem"},
    {label: "Java/Kotlin", description: "Enterprise-grade, JVM, Spring ecosystem, verbose, battle-tested"}
  ]
}

// Frontend Framework
{
  question: "What frontend approach do you want?",
  header: "Frontend",
  options: [
    {label: "React", description: "Popular, large ecosystem, component-based, JSX syntax, flexible"},
    {label: "Vue", description: "Simpler than React, good docs, template syntax, smaller ecosystem"},
    {label: "Svelte", description: "Compile-time framework, fast, less boilerplate, newer ecosystem"},
    {label: "Vanilla JS", description: "No framework, full control, smaller bundle, more manual work"}
  ]
}

// Hosting Infrastructure
{
  question: "Where will you host this application?",
  header: "Hosting",
  options: [
    {label: "AWS", description: "Full service suite, complex, powerful, enterprise-ready, higher cost"},
    {label: "Google Cloud", description: "Good for AI/ML, Kubernetes native, competitive pricing"},
    {label: "Azure", description: "Enterprise integration, Microsoft stack, hybrid cloud"},
    {label: "Vercel/Netlify", description: "Simple deployment, great DX, limited backend, good for JAMstack"}
  ]
}
```

**Converse about**: Framework choices within language, build tools and CI/CD pipeline, deployment strategy.

**From PRD.md (if available)**: Budget → Hosting costs, Timeline → Deployment complexity

## Phase 3: Data Models & Storage

**Goal**: Define data storage strategy, schemas, and caching.

**Context**: Research with WebSearch/WebFetch("[database] best practices 2025"), explore with /epcc-explore (brownfield).

**Use AskUserQuestion for**:
```typescript
// Database Selection
{
  question: "What database technology fits your data model?",
  header: "Database",
  options: [
    {label: "PostgreSQL", description: "Relational, ACID, complex queries, JSON support, mature"},
    {label: "MongoDB", description: "Document store, flexible schema, good for JSON, horizontal scaling"},
    {label: "MySQL", description: "Relational, widely supported, proven at scale, simpler than Postgres"},
    {label: "DynamoDB", description: "AWS NoSQL, serverless, auto-scaling, key-value or documents"}
  ]
}

// Caching Strategy (if medium/complex)
{
  question: "What caching approach do you need?",
  header: "Caching",
  multiSelect: true,
  options: [
    {label: "Redis", description: "In-memory, fast, pub/sub, session storage, requires management"},
    {label: "CDN", description: "Edge caching, static assets, global distribution, reduces origin load"},
    {label: "Application cache", description: "In-process, simple, no network, lost on restart"},
    {label: "Database query cache", description: "Built-in, automatic, limited control"}
  ]
}
```

**Converse about**: Data model structure, schema design approach, data access patterns (read-heavy? write-heavy?).

**From PRD.md (if available)**: Features → Data entities, Users → Access patterns

## Phase 4: Integrations & APIs

**Goal**: Define API design, authentication, and third-party integrations.

**Context**: Research with WebSearch/WebFetch("[API/auth] best practices 2025"), explore with /epcc-explore (brownfield).

**Use AskUserQuestion for**:
```typescript
// API Style
{
  question: "What API style fits your needs?",
  header: "API",
  options: [
    {label: "REST", description: "Standard HTTP, widely understood, simple, over-fetching/under-fetching"},
    {label: "GraphQL", description: "Flexible queries, precise data fetching, complex setup, learning curve"},
    {label: "gRPC", description: "High performance, typed, binary protocol, requires code generation"},
    {label: "tRPC", description: "Type-safe, TypeScript end-to-end, simple, ecosystem smaller"}
  ]
}

// Authentication Method
{
  question: "How will users authenticate?",
  header: "Auth",
  options: [
    {label: "JWT", description: "Stateless, scalable, client stores token, can't revoke easily"},
    {label: "Session", description: "Server-side state, easy to revoke, requires session store"},
    {label: "OAuth2", description: "Third-party login (Google, GitHub), complex setup, better UX"},
    {label: "Auth0/Clerk", description: "Managed service, fast setup, monthly cost, less control"}
  ]
}

// Third-Party Services (multiSelect)
{
  question: "What third-party services do you need?",
  header: "Services",
  multiSelect: true,
  options: [
    {label: "Payment", description: "Stripe, PayPal, Square - transaction processing"},
    {label: "Email", description: "SendGrid, Mailgun, AWS SES - transactional emails"},
    {label: "Storage", description: "S3, Cloudinary, Uploadcare - file uploads and CDN"},
    {label: "Analytics", description: "Mixpanel, Amplitude, PostHog - user behavior tracking"}
  ]
}
```

**Converse about**: API versioning strategy, webhook handling, rate limiting and API security.

**From PRD.md (if available)**: Features → Required integrations (payments, notifications, etc.)

## Phase 5: Security & Compliance

**Goal**: Define authentication, authorization, data protection, and compliance.

**Context**: Research with WebSearch/WebFetch("[security/compliance] requirements 2025"), explore with /epcc-explore (brownfield).

**Use AskUserQuestion for**:
```typescript
// Authorization Model
{
  question: "What authorization model do you need?",
  header: "Authz",
  options: [
    {label: "RBAC", description: "Role-based, simple, roles assigned to users, good for most apps"},
    {label: "ABAC", description: "Attribute-based, flexible, complex policies, enterprise use cases"},
    {label: "Simple ownership", description: "Users own resources, basic access control, simplest"},
    {label: "Multi-tenancy", description: "Isolated data per tenant, complex, SaaS products"}
  ]
}

// Compliance Requirements (multiSelect, if applicable)
{
  question: "What compliance standards apply?",
  header: "Compliance",
  multiSelect: true,
  options: [
    {label: "GDPR", description: "EU data privacy, right to deletion, consent management"},
    {label: "HIPAA", description: "Healthcare data, strict security, audit logs, encryption"},
    {label: "SOC2", description: "Security controls, audit reports, enterprise customers"},
    {label: "PCI DSS", description: "Payment card data, strict requirements, third-party audits"}
  ]
}
```

**Converse about**: Data encryption (at rest? in transit?), OWASP Top 10 considerations, security testing approach.

**From PRD.md (if available)**: Constraints → Compliance requirements, Data sensitivity

## Phase 6: Performance & Scalability

**Goal**: Define performance targets, scaling strategy, and optimization priorities.

**Context**: Research with WebSearch/WebFetch("[performance/scaling] patterns 2025"), explore with /epcc-explore (brownfield).

**Use AskUserQuestion for**:
```typescript
// Expected Scale
{
  question: "What scale are you targeting?",
  header: "Scale",
  options: [
    {label: "Small (<1K users)", description: "Single server, minimal caching, simple deployment"},
    {label: "Medium (1K-100K users)", description: "Load balancer, caching layer, horizontal scaling"},
    {label: "Large (100K-1M users)", description: "Multi-region, CDN, advanced caching, auto-scaling"},
    {label: "Massive (>1M users)", description: "Global infrastructure, edge computing, complex architecture"}
  ]
}

// Performance Priorities (multiSelect)
{
  question: "What performance aspects are most critical?",
  header: "Performance",
  multiSelect: true,
  options: [
    {label: "Page load speed", description: "Initial render, time to interactive, Core Web Vitals"},
    {label: "API latency", description: "Response times, database query optimization"},
    {label: "Real-time updates", description: "WebSocket, SSE, sub-second data freshness"},
    {label: "Background jobs", description: "Async processing, job queues, worker scaling"}
  ]
}
```

**Converse about**: Performance budgets, monitoring and observability strategy, optimization approach.

**From PRD.md (if available)**: Success criteria → Performance targets, Users → Scale expectations
