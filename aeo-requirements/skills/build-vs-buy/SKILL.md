---
name: build-vs-buy
description: |
  Build-vs-buy decision framework with TCO analysis, vendor evaluation, and migration planning.
  Activate when: evaluating build vs buy, comparing vendors, assessing make or buy decisions,
  analyzing total cost of ownership, planning vendor migrations, evaluating SaaS vs custom.
---

# Build vs Buy Decision Framework

## Decision Framework Overview

```markdown
When to consider Build:
- Core differentiator (competitive advantage)
- Unique domain logic not served by existing products
- Need full control over roadmap and customization
- Existing solutions require heavy customization (>40% custom)
- Data sovereignty or compliance prevents third-party use

When to consider Buy:
- Commodity capability (auth, payments, email, monitoring)
- Time-to-market is critical
- Internal team lacks domain expertise
- Proven solutions exist with strong ecosystems
- Maintenance burden of build exceeds license cost
```

## TCO Analysis (Total Cost of Ownership)

### Build Cost Model

```markdown
## Upfront Costs
Development:
  - Engineering hours × hourly rate
  - Design and architecture time
  - Testing and QA effort
  - Documentation creation
  - Infrastructure setup

Opportunity cost:
  - What else could the team build instead?
  - Revenue delayed by building vs buying

## Ongoing Costs (Annual)
Maintenance:
  - Bug fixes: ~20% of original development effort per year
  - Security patches and updates
  - Dependency upgrades
  - On-call and incident response

Operations:
  - Infrastructure (compute, storage, networking)
  - Monitoring and alerting tools
  - Backup and disaster recovery
  - Performance tuning

Evolution:
  - Feature enhancements
  - Scaling for growth
  - Integration with new systems
  - Technical debt reduction

People:
  - Knowledge concentration risk (bus factor)
  - Hiring and training specialists
  - Team turnover and ramp-up time
```

### Buy Cost Model

```markdown
## Upfront Costs
Procurement:
  - License or subscription fees
  - Implementation/consulting fees
  - Data migration effort
  - Integration development
  - User training

Customization:
  - Configuration and setup
  - Custom integrations
  - Workflow adaptation
  - Plugin/extension development

## Ongoing Costs (Annual)
Licensing:
  - Per-user or per-transaction fees
  - Tier upgrades as usage grows
  - Support plan costs
  - Add-on module costs

Integration maintenance:
  - API version upgrades
  - Custom integration fixes
  - Data sync monitoring

Operational:
  - Vendor management overhead
  - Contract renewals and negotiations
  - Compliance audits
  - Internal admin and configuration

Hidden costs:
  - Vendor lock-in switching costs
  - Feature limitations and workarounds
  - Downtime from vendor outages (outside your control)
  - Data export/portability limitations
```

### TCO Comparison Template

```markdown
| Cost Category        | Build (5yr) | Buy (5yr) |
|---------------------|-------------|-----------|
| Initial development | $XXX        | —         |
| Implementation      | —           | $XXX      |
| Integration         | $XXX        | $XXX      |
| License/subscription| —           | $XXX      |
| Infrastructure      | $XXX        | $XXX      |
| Maintenance (annual)| $XXX × 5   | $XXX × 5  |
| Support             | Internal    | $XXX × 5  |
| Training            | $XXX        | $XXX      |
| Opportunity cost    | $XXX        | —         |
| **Total**           | **$XXX**    | **$XXX**  |

Break-even point: Year [N] (where build becomes cheaper than buy)
```

## Vendor Evaluation Criteria

### Evaluation Scorecard

```markdown
Score each criterion 1-5 (1=poor, 5=excellent), weight by importance.

| Criterion              | Weight | Vendor A | Vendor B | Build |
|------------------------|--------|----------|----------|-------|
| Feature fit            | 25%    |          |          |       |
| Integration capability | 20%    |          |          |       |
| Scalability            | 15%    |          |          |       |
| Security & compliance  | 15%    |          |          |       |
| Vendor stability       | 10%    |          |          |       |
| Support quality        | 10%    |          |          |       |
| Pricing model          | 5%     |          |          |       |
| **Weighted total**     | 100%   |          |          |       |
```

### Feature Fit Assessment

```markdown
For each required capability:

| Requirement          | Priority | Vendor A    | Vendor B    |
|---------------------|----------|-------------|-------------|
| [Feature 1]         | Must     | Native      | Plugin      |
| [Feature 2]         | Must     | Custom dev  | Native      |
| [Feature 3]         | Should   | Not available| Native     |
| [Feature 4]         | Could    | Native      | Not available|

Legend:
  Native         — Built-in, works out of the box
  Configuration  — Requires setup but no code
  Plugin         — Available via marketplace/extension
  Custom dev     — Requires custom development
  Not available  — Cannot be achieved
```

### Vendor Due Diligence

```markdown
Financial Health:
  - Revenue trend (growing, stable, declining?)
  - Funding status (bootstrapped, funded, public?)
  - Customer count and retention rate
  - Key customer references in your industry

Product Maturity:
  - Years in market
  - Release frequency and changelog quality
  - Public roadmap availability
  - API stability (breaking changes history)
  - Documentation quality and completeness

Security & Compliance:
  - SOC 2 Type II certification
  - GDPR compliance (if applicable)
  - Data residency options
  - Penetration testing cadence
  - Incident response track record
  - Encryption standards (at rest, in transit)

Support & SLA:
  - Support tiers and response times
  - Uptime SLA (99.9%? 99.99%?)
  - Penalty/credit structure for SLA violations
  - Dedicated account manager (at your tier?)
  - Community and self-service resources

Contract Terms:
  - Minimum commitment period
  - Price escalation caps
  - Data portability on exit
  - Termination for convenience clause
  - Auto-renewal terms
```

## Integration Risk Assessment

### Integration Complexity Matrix

```markdown
| Integration Point    | Complexity | Risk  | Mitigation |
|---------------------|------------|-------|------------|
| Authentication (SSO)| Low        | Low   | Standard OIDC/SAML |
| Data sync (real-time)| High      | High  | Event-driven, idempotent |
| Reporting/BI        | Medium     | Low   | Read-only API |
| Workflow automation  | Medium    | Medium| Webhook + retry |
| Legacy system bridge | High      | High  | Adapter pattern |

Complexity factors:
  - Data format transformation required
  - Bi-directional sync needed
  - Real-time vs batch requirements
  - Error handling and retry complexity
  - Authentication and authorization model
  - Rate limiting and throttling
```

### API Evaluation Checklist

```markdown
- [ ] REST or GraphQL API available
- [ ] API documentation is complete and accurate
- [ ] API versioning strategy (URL, header, or query param)
- [ ] Rate limits are documented and sufficient
- [ ] Webhook support for event-driven integration
- [ ] Sandbox/test environment available
- [ ] SDK available in your language(s)
- [ ] Bulk/batch operations supported
- [ ] Pagination for large result sets
- [ ] Error responses are structured and documented
- [ ] API status page and incident communication
```

### Vendor Lock-In Assessment

```markdown
Lock-in risk factors (score each 1-5):

Data portability:
  - Can you export all your data? In what format?
  - Is the data schema documented?
  - How long does export take at your data volume?

Feature portability:
  - How much custom logic lives inside the vendor?
  - Are workflows exportable or vendor-specific?
  - Can configurations be version-controlled?

Integration coupling:
  - How many systems depend on this vendor's API?
  - Are you using vendor-specific features or standards?
  - Can you swap to an alternative without rewriting integrations?

Contractual lock-in:
  - Multi-year commitment required?
  - Penalty for early termination?
  - Data held hostage after contract ends?

Total lock-in score:
  4-8:  Low risk (easy to switch)
  9-14: Medium risk (switching is painful but feasible)
  15-20: High risk (significant switching cost; plan mitigation)
```

## Migration Planning

### Migration Phases

```markdown
Phase 1: Assessment
  - Inventory current system capabilities
  - Map data entities and relationships
  - Identify integration dependencies
  - Document business rules embedded in current system
  - Assess user workflows and training needs

Phase 2: Planning
  - Define data migration strategy (big-bang vs incremental)
  - Design integration architecture
  - Plan parallel running period
  - Create rollback strategy
  - Build test plan for migration validation

Phase 3: Execution
  - Set up target system
  - Develop and test data migration scripts
  - Build integrations
  - Migrate data (with validation checkpoints)
  - Run parallel systems during transition

Phase 4: Cutover
  - Final data sync
  - Switch traffic to new system
  - Monitor for issues
  - Decommission old system (after bake period)

Phase 5: Stabilization
  - Address post-migration issues
  - Optimize performance
  - Complete user training
  - Document lessons learned
```

### Data Migration Checklist

```markdown
- [ ] Complete data inventory (entities, volumes, relationships)
- [ ] Field-level mapping between source and target
- [ ] Data cleansing rules defined (dedup, format, validation)
- [ ] Migration scripts developed and tested
- [ ] Dry run completed on production-like data
- [ ] Data validation queries prepared (row counts, checksums)
- [ ] Rollback procedure tested
- [ ] Cutover window scheduled with stakeholders
- [ ] Post-migration verification plan ready
```

## Decision Documentation Template

```markdown
# Build vs Buy Decision: [Capability Name]

## Context
- Business need: [what problem are we solving]
- Timeline: [when do we need it]
- Team capacity: [available engineering bandwidth]

## Options Evaluated
1. Build in-house
2. Vendor A: [name]
3. Vendor B: [name]

## Evaluation Summary
| Criterion | Build | Vendor A | Vendor B |
|-----------|-------|----------|----------|
| Feature fit | X/5 | X/5 | X/5 |
| Time to value | X/5 | X/5 | X/5 |
| 5-year TCO | $X | $X | $X |
| Lock-in risk | X/5 | X/5 | X/5 |
| Team capacity | X/5 | X/5 | X/5 |

## Decision
**Choice**: [Build / Vendor X]
**Rationale**: [2-3 sentences explaining the primary driver]
**Trade-offs accepted**: [what are we giving up]
**Review date**: [when to revisit this decision]

## Approved by
- [Name, Role, Date]
```
