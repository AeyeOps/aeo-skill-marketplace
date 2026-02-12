# TRD Tech Evaluation & Feature Enrichment

Adaptive interview heuristics and technical feature enrichment for TRD generation.

## Adaptive Interview Heuristics

**Match question depth to project complexity** (discovered dynamically):

### Simple Project Indicators
- Single service/application
- <10K users
- Standard CRUD operations
- 0-2 integrations
- No compliance requirements

**Adapt**: Focus on Stack + Data + Basic Security (~10-12 questions)

### Medium Project Indicators
- 2-3 services
- 10K-100K users
- Some real-time features
- 3-5 integrations
- Basic security needs

**Adapt**: All 6 phases with moderate depth (~20-25 questions)

### Complex Project Indicators
- Microservices/distributed
- >100K users
- Compliance requirements
- >5 integrations
- High performance/availability needs

**Adapt**: Comprehensive exploration of all 6 phases (~30-40 questions)

**Dynamic adjustment**: If user mentions compliance/high-scale/many integrations during simple TRD → offer to switch to comprehensive mode.

## Technical Feature Enrichment (Long-Running Project Support)

After generating TECH_REQ.md, enrich the feature list with technical subtasks if `epcc-features.json` exists.

### Step 1: Check for Existing Feature List

```bash
if [ -f "epcc-features.json" ]; then
    echo "Found epcc-features.json - enriching features with technical details..."
else
    echo "No epcc-features.json found - technical decisions will inform /epcc-plan"
fi
```

### Step 2: Add Technical Subtasks to Existing Features

For each feature in `epcc-features.json`, add technical subtasks based on TRD decisions:

```json
{
  "features": [
    {
      "id": "F001",
      "name": "User Authentication",
      "subtasks": [
        {"name": "Set up [Auth provider] integration", "status": "pending", "source": "TECH_REQ.md#authentication"},
        {"name": "Implement [JWT/Session] token handling", "status": "pending", "source": "TECH_REQ.md#authentication"},
        {"name": "Create [Database] user schema", "status": "pending", "source": "TECH_REQ.md#data-model"},
        {"name": "Configure [bcrypt/argon2] password hashing", "status": "pending", "source": "TECH_REQ.md#security"},
        {"name": "Add rate limiting middleware", "status": "pending", "source": "TECH_REQ.md#security"}
      ]
    }
  ]
}
```

**Subtask generation rules:**
- Map each TRD technology decision to relevant features
- Add infrastructure subtasks for features requiring new components
- Include security subtasks based on compliance requirements
- Add integration subtasks for third-party services
- Include testing subtasks for critical paths

### Step 3: Add Infrastructure Features

Add new features for infrastructure tasks not covered by product features:

```json
{
  "features": [
    {
      "id": "INFRA-001",
      "name": "Database Setup",
      "description": "Set up [PostgreSQL] database with schemas and migrations",
      "priority": "P0",
      "status": "pending",
      "passes": false,
      "acceptanceCriteria": [
        "Database provisioned and accessible",
        "All migrations run successfully",
        "Connection pooling configured",
        "Backup strategy in place"
      ],
      "subtasks": [],
      "source": "TECH_REQ.md#data-model"
    },
    {
      "id": "INFRA-002",
      "name": "CI/CD Pipeline",
      "description": "Set up continuous integration and deployment",
      "priority": "P1",
      "status": "pending",
      "passes": false,
      "acceptanceCriteria": [
        "Tests run on every commit",
        "Automated deployment to staging",
        "Production deployment with approval gate"
      ],
      "subtasks": [],
      "source": "TECH_REQ.md#deployment"
    },
    {
      "id": "INFRA-003",
      "name": "Monitoring & Logging",
      "description": "Set up application monitoring and centralized logging",
      "priority": "P1",
      "status": "pending",
      "passes": false,
      "acceptanceCriteria": [
        "Error tracking configured",
        "Performance monitoring in place",
        "Logs aggregated and searchable"
      ],
      "subtasks": [],
      "source": "TECH_REQ.md#monitoring"
    }
  ]
}
```

**Infrastructure feature rules:**
- Add database setup if database selected in TRD
- Add CI/CD if deployment strategy defined
- Add monitoring if observability discussed
- Add security setup if compliance requirements exist
- Add caching setup if caching strategy defined

### Step 4: Update Progress Log

Append TRD session to `epcc-progress.md`:

```markdown
---

## Session [N]: TRD Created - [Date]

### Summary
Technical Requirements Document created with architecture and technology decisions.

### Technical Decisions
- **Architecture**: [Pattern chosen]
- **Backend**: [Technology + rationale]
- **Frontend**: [Technology + rationale]
- **Database**: [Technology + rationale]
- **Hosting**: [Platform chosen]
- **Authentication**: [Method chosen]

### Feature Enrichment
- Updated [X] features with technical subtasks
- Added [Y] infrastructure features:
  - INFRA-001: Database Setup
  - INFRA-002: CI/CD Pipeline
  [...]

### Feature Summary (Updated)
- **Total Features**: [N] (was [M] from PRD)
- **Product Features**: [X] (with technical subtasks)
- **Infrastructure Features**: [Y] (new from TRD)

### Next Session
Run `/epcc-plan` to finalize implementation order and create detailed task breakdown.

---
```

### Step 5: Report Enrichment Results

```markdown
## Technical Requirements Complete

✅ **TECH_REQ.md** - Technical decisions documented
✅ **epcc-features.json** - Features enriched with technical details:
   - [X] existing features updated with subtasks
   - [Y] infrastructure features added
   - Total features: [N]
✅ **epcc-progress.md** - TRD session logged

### Technical Subtasks Added

| Feature | Subtasks Added | Source |
|---------|----------------|--------|
| F001: User Auth | 5 subtasks | TECH_REQ.md#authentication |
| F002: Task CRUD | 3 subtasks | TECH_REQ.md#data-model |
| ... | ... | ... |

### Infrastructure Features Added

| Feature | Priority | Source |
|---------|----------|--------|
| INFRA-001: Database Setup | P0 | TECH_REQ.md#data-model |
| INFRA-002: CI/CD Pipeline | P1 | TECH_REQ.md#deployment |
| ... | ... | ... |

### Next Steps

**For Implementation Planning**: `/epcc-plan` - Finalize task order and create detailed breakdown
**For Brownfield Projects**: `/epcc-explore` - Understand existing codebase first
**To check progress**: `/epcc-resume` - Quick orientation and status
```

## Subtask Generation Heuristics

Map TRD decisions to subtasks based on technology choices:

| TRD Section | Generated Subtasks |
|-------------|-------------------|
| **Authentication: JWT** | Token generation, validation middleware, refresh token handling |
| **Authentication: OAuth2** | Provider integration, callback handling, token storage |
| **Database: PostgreSQL** | Schema creation, migrations, connection pooling, indexes |
| **Database: MongoDB** | Schema design, indexes, aggregation pipelines |
| **API: REST** | Route structure, validation, error handling, documentation |
| **API: GraphQL** | Schema definition, resolvers, subscriptions setup |
| **Hosting: AWS** | IAM setup, VPC config, deployment scripts |
| **Hosting: Vercel** | Environment variables, build config, domain setup |
| **Caching: Redis** | Connection setup, cache invalidation, session storage |
| **Security: GDPR** | Audit logging, data export, deletion handlers |
