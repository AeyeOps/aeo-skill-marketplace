# TRD Output Templates

Three complexity-matched TRD variants plus the full comprehensive template.

## Simple TRD (~400-600 tokens)

**When**: Single service, standard stack, minimal integrations, <10K users

```markdown
# Technical Requirements: [Project Name]

**Created**: [Date] | **Complexity**: Simple | **From PRD**: [Yes/No]

## Architecture
**Pattern**: [Monolith/SPA/JAMstack]
**Rationale**: [Why this pattern fits the project]

## Technology Stack
**Backend**: [Language + Framework] - [Rationale]
**Frontend**: [Framework/Vanilla] - [Rationale]
**Database**: [Database] - [Rationale]
**Hosting**: [Platform] - [Rationale]

## Data Model
**Core Entities**: [List 3-5 main entities]
**Relationships**: [Key relationships]
**Migrations**: [Strategy: tool/approach]

## Security
**Authentication**: [Method] - [Rationale]
**Authorization**: [Approach] - [Rationale]
**Data Protection**: [Encryption strategy]

## Integrations
[List essential integrations with rationale, or "None" if standalone]

## Performance
**Expected Scale**: [<1K users, load expectations]
**Caching**: [Strategy if needed, or "Not required initially"]

## PRD Alignment
[If PRD.md exists, reference how technical choices support product requirements]

## Next Steps
Technical requirements defined. Ready for:
- Brownfield: `/epcc-explore` then `/epcc-plan`
- Greenfield: `/epcc-plan` (skip explore)
```

## Medium TRD (~800-1,200 tokens)

**When**: Multiple services, moderate complexity, several integrations, 10K-100K users

Add to simple structure:
- **Architecture Diagram**: Component relationships, data flow
- **Detailed Stack Justification**: Compare alternatives with tradeoffs
- **API Design**: REST/GraphQL, versioning strategy, rate limiting
- **Caching Strategy**: Layers (CDN, application, database), invalidation
- **Monitoring**: Observability approach, key metrics
- **Deployment**: CI/CD pipeline, environment strategy

## Complex TRD (~1,500-2,500 tokens)

**When**: Distributed system, compliance requirements, high scale, many integrations

Add to medium structure:
- **Detailed Architecture**: Service boundaries, event flows, async patterns
- **Technology Evaluation**: Deep comparison of alternatives with scoring
- **Data Architecture**: Schema design, partitioning, replication, migrations
- **Security & Compliance**: OWASP checklist, compliance requirements (GDPR/HIPAA/SOC2), audit logging
- **Performance & Scale**: Load testing strategy, auto-scaling, multi-region, CDN strategy
- **Disaster Recovery**: Backup strategy, failover, RTO/RPO targets
- **Migration Plan**: If replacing existing system

**Depth heuristic**: TRD complexity should match technical complexity. Don't write distributed systems TRD for simple CRUD app.

## Full TRD Template (Adapt to Complexity)

```markdown
# Technical Requirements Document: [Project Name]

**Created**: [Date]
**Version**: 1.0
**Complexity**: [Simple/Medium/Complex]
**PRD Reference**: [PRD.md if available, or "Standalone"]

---

## Executive Summary
[2-3 sentence technical overview]

## Research & Exploration

**Key Insights** (from WebSearch/WebFetch/exploration):
- **[Technology choice]**: [Research finding, benchmark, or rationale]
- **[Pattern/approach]**: [Best practice discovered or code pattern leveraged]
- **[Existing component]**: [Reusable code discovered from exploration]

**Documentation Identified**:
- **[Doc type]**: Priority [H/M/L] - [Why needed for this project]

## Architecture

### Pattern
[Monolith/Microservices/Serverless/JAMstack/Hybrid]

**Rationale**: [Why this pattern? Considered alternatives?]

### Component Structure
[List main components/services and their responsibilities]

### Data Flow
[How data moves through the system - simple description or diagram]

### Design Patterns
[Key patterns: Event-driven, CQRS, Repository, etc.]

## Technology Stack

### Backend
**Language/Runtime**: [Choice] - [Rationale vs alternatives]
**Framework**: [Choice] - [Rationale vs alternatives]

### Frontend
**Framework**: [React/Vue/Svelte/Vanilla] - [Rationale vs alternatives]
**Build Tools**: [Vite/Webpack/etc.] - [Rationale]

### Database
**Primary Database**: [PostgreSQL/MongoDB/MySQL/etc.] - [Rationale vs alternatives]
**Caching**: [Redis/CDN/Application cache] - [Strategy]

### Infrastructure
**Hosting**: [AWS/GCP/Azure/Vercel/etc.] - [Rationale vs alternatives]
**Deployment**: [Containers/Serverless/VMs] - [Rationale]
**CI/CD**: [GitHub Actions/GitLab CI/CircleCI/etc.] - [Strategy]

## Environment Setup

**init.sh required**: [Yes/No]

**Triggers** (if any apply, init.sh is needed):
- [ ] Web server / API backend
- [ ] Database setup required
- [ ] External services (Redis, Elasticsearch, etc.)
- [ ] Complex dependency installation
- [ ] Environment variables required

**Components to initialize** (if init.sh required):
- [ ] Virtual environment / package installation
- [ ] Database setup/migration
- [ ] Service dependencies: [list services]
- [ ] Environment variables: [list vars, no secrets]
- [ ] Development server startup

**Startup command**: [e.g., "npm run dev", "uvicorn main:app --reload"]
**Health check**: [e.g., "curl localhost:3000/health"]

## Data Architecture

### Core Entities
1. **[Entity Name]**
   - Purpose: [What it represents]
   - Key attributes: [Essential fields]
   - Relationships: [Connections to other entities]

### Schema Design
**Approach**: [Normalized/Denormalized/Hybrid] - [Rationale]
**Migrations**: [Tool: Prisma/TypeORM/Alembic/etc.] - [Strategy]

### Data Access Patterns
- [Read-heavy? Write-heavy? Analytics?]
- [Query optimization strategy]

## API Design

### API Style
**Choice**: [REST/GraphQL/gRPC/tRPC] - [Rationale vs alternatives]

### Endpoints (if REST)
[High-level endpoint groups, not exhaustive list]

### Authentication
**Method**: [JWT/Session/OAuth2/Auth0] - [Rationale vs alternatives]
**Token Storage**: [Where tokens stored, expiry strategy]

### Authorization
**Model**: [RBAC/ABAC/Ownership/Multi-tenancy] - [Rationale]

### Rate Limiting
[Strategy if needed]

## Integrations

### Third-Party Services
1. **[Service Name]** (e.g., Stripe for payments)
   - Purpose: [What it does]
   - Rationale: [Why this vs alternatives]
   - Integration approach: [API/SDK/Webhook]

### External APIs
[Any external APIs to consume]

### Webhooks
[If handling incoming webhooks]

## Security

### Authentication & Authorization
**Authentication**: [Detailed approach from API Design]
**Authorization**: [Detailed model from API Design]

### Data Protection
**Encryption at Rest**: [Yes/No - approach if yes]
**Encryption in Transit**: [TLS configuration]
**Sensitive Data**: [PII handling, secrets management]

### OWASP Considerations
[Key OWASP Top 10 items relevant to this project]

### Compliance (if applicable)
**Requirements**: [GDPR/HIPAA/SOC2/PCI DSS/etc.]
**Implementation**: [How compliance requirements are met]
**Audit Logging**: [What's logged, retention period]

## Performance & Scalability

### Scale Targets
**Users**: [Expected user count]
**Requests**: [Expected req/sec or req/day]
**Data Volume**: [Expected data growth]

### Performance Budgets
- **Page Load**: [Target: <2s]
- **API Latency**: [Target: <100ms p95]
- **Database Queries**: [Target: <50ms p95]

### Caching Strategy
**Layers**:
1. **CDN**: [Static assets, edge caching]
2. **Application Cache**: [Redis/in-memory, what's cached]
3. **Database Query Cache**: [If applicable]

**Invalidation**: [Strategy for cache freshness]

### Scaling Approach
**Horizontal vs Vertical**: [Choice and rationale]
**Auto-scaling**: [Triggers, min/max instances]
**Load Balancing**: [Strategy]

### Monitoring & Observability
**Metrics**: [What to track: latency, errors, throughput]
**Logging**: [Structured logging approach]
**Tracing**: [Distributed tracing if microservices]
**Tools**: [DataDog/New Relic/Prometheus/etc.]

## Deployment Strategy

### Environments
- **Development**: [Local/shared dev environment]
- **Staging**: [Pre-production testing]
- **Production**: [Live environment]

### CI/CD Pipeline
1. [Build step]
2. [Test step]
3. [Deploy step]

### Rollback Strategy
[How to revert if deployment fails]

### Zero-Downtime Deployment
[Blue-green? Rolling? Canary?]

## Disaster Recovery (Complex projects)

### Backup Strategy
**Frequency**: [Hourly/Daily/etc.]
**Retention**: [How long backups kept]
**Testing**: [Backup restore testing frequency]

### Failover
**RTO** (Recovery Time Objective): [Target downtime]
**RPO** (Recovery Point Objective): [Acceptable data loss]

## Migration Plan (If applicable)

### Migration Strategy
- [Approach: Big bang? Phased? Strangler pattern?]

### Data Migration
- [Source → Target mapping]
- [Validation strategy]

### Rollback Plan
- [How to revert if migration fails]

## Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Technical risk] | H/M/L | H/M/L | [How to address] |

## Assumptions

[Critical technical assumptions that could change the plan]

## Out of Scope

[Technical decisions deferred or explicitly excluded]

## PRD Alignment

[If PRD.md exists]

**Product Requirements Supported**:
- [Feature from PRD] → [Technical approach]
- [Constraint from PRD] → [How technical design respects it]
- [Success criteria from PRD] → [How architecture enables measurement]

**Technical Decisions Informing Product**:
- [Technology limitation] → [Product implication]
- [Performance characteristic] → [User experience impact]

## Next Steps

This TRD feeds into the EPCC workflow. Choose your entry point:

**For Greenfield Projects** (new codebase):
1. Review & approve this TRD
2. Run `/epcc-plan` to create implementation plan (can skip Explore)
3. Begin development with `/epcc-code`
4. Finalize with `/epcc-commit`

**For Brownfield Projects** (existing codebase):
1. Review & approve this TRD
2. Run `/epcc-explore` to understand existing codebase and patterns
3. Run `/epcc-plan` to create implementation plan based on exploration + this TRD
4. Begin development with `/epcc-code`
5. Finalize with `/epcc-commit`

**Note**: The core EPCC workflow is: **Explore → Plan → Code → Commit**. This TRD is the optional technical preparation step before that cycle begins.

---

**End of TRD**
```

**Completeness heuristic**: TRD is ready when you can answer:
- What's the architecture pattern and why?
- What's the technology stack with rationale for each choice?
- What's the data model and storage strategy?
- How are integrations and APIs designed?
- How is security and compliance handled?
- How does the system scale and perform?
- If PRD exists, how do technical choices support product requirements?

**Anti-patterns**:
- **Simple CRUD with 2,000-token distributed systems TRD** → Violates complexity matching
- **Complex platform with 500-token TRD** → Insufficient technical detail
- **"Use PostgreSQL" without explaining why vs MongoDB/MySQL** → No rationale
- **Implementation details** → "Create UserService class with getUserById method" belongs in CODE phase
- **Every section filled with "TBD"** → If unknown, document as assumption or open question
- **No security consideration** → All projects need auth/data protection discussion
