---
name: requirements-elicitation
description: |
  Stakeholder interview techniques, requirement types, prioritization frameworks, and acceptance criteria patterns.
  Activate when: eliciting requirements, writing user stories, interviewing stakeholders,
  prioritizing features, defining acceptance criteria, building a requirements document.
---

# Requirements Elicitation

## Stakeholder Interview Techniques

### Structured Interview
Prepare questions in advance grouped by topic. Best for extracting specific information.

```markdown
Interview Template:
1. Context Setting (5 min)
   - "Walk me through your typical day using [system/process]."
   - "What is your role in relation to this project?"

2. Problem Discovery (15 min)
   - "What are the top 3 pain points you experience?"
   - "How much time/money does this cost you?"
   - "What happens when it goes wrong?"

3. Current Workflow (10 min)
   - "Show me step-by-step how you do [task] today."
   - "Where do things slow down or break?"
   - "What workarounds have you built?"

4. Desired Outcome (10 min)
   - "If you could wave a magic wand, what would change?"
   - "What does success look like in 6 months?"
   - "How would you measure improvement?"

5. Constraints (5 min)
   - "What cannot change?"
   - "What regulatory/compliance requirements apply?"
   - "What are the budget and timeline boundaries?"
```

### Contextual Inquiry
Observe users in their actual work environment. Record what they do, not what they say they do.

```markdown
Observation Checklist:
- Physical workspace setup
- Tools and systems used
- Sequence of actions for key tasks
- Error recovery behaviors
- Collaboration and handoff points
- Workarounds and sticky notes (literal or figurative)
- Interruptions and context switches
```

### Focus Group
Bring 5-8 stakeholders together to surface shared concerns and conflicting needs.

```markdown
Facilitation Guide:
- Set ground rules: no rank, everyone's input valued
- Use "round robin" to ensure all voices heard
- Use dot voting to surface priorities
- Capture exact language (don't paraphrase in session)
- Note areas of agreement AND disagreement
- Follow up individually on sensitive topics
```

### Reverse Engineering
Analyze existing systems, reports, and documentation to extract implicit requirements.

```markdown
Sources to mine:
- Existing system screenshots and workflows
- Support ticket themes (top 10 recurring issues)
- Error logs and exception reports
- User training materials (reveal expected behavior)
- Compliance documentation (non-negotiable requirements)
- Competitor product walkthroughs
```

## Requirement Types

### Functional Requirements
What the system must do — observable behaviors and capabilities.

```markdown
Template: The system shall [action] [object] when [condition].

Examples:
- The system shall send a confirmation email within 30 seconds of order placement.
- The system shall allow users to filter search results by date range, category, and status.
- The system shall prevent duplicate submissions within a 5-second window.

Checklist for completeness:
- [ ] Inputs defined (source, format, validation)
- [ ] Processing logic specified (rules, calculations, transformations)
- [ ] Outputs defined (format, destination, timing)
- [ ] Error handling specified (what happens when things fail)
- [ ] State changes documented (what data is created/modified/deleted)
```

### Non-Functional Requirements
Quality attributes — how the system must perform.

```markdown
Performance:
- Response time: "95th percentile under 200ms"
- Throughput: "Handle 10,000 concurrent users"
- Batch processing: "Complete nightly ETL in under 2 hours"

Reliability:
- Availability: "99.9% uptime (8.7 hours downtime per year)"
- Recovery: "RPO < 1 hour, RTO < 15 minutes"
- Fault tolerance: "No data loss on single-node failure"

Security:
- Authentication: "MFA required for admin access"
- Authorization: "Role-based access control with audit logging"
- Data protection: "PII encrypted at rest and in transit"

Scalability:
- Horizontal: "Scale to 10x current load without architecture changes"
- Data growth: "Support 5TB data growth per year for 5 years"

Usability:
- Accessibility: "WCAG 2.1 AA compliance"
- Learnability: "New user productive within 30 minutes"
- Error prevention: "Confirmation dialogs for destructive actions"
```

### Constraints
Non-negotiable boundaries imposed externally.

```markdown
Types:
- Technical: "Must run on AWS", "Must use PostgreSQL"
- Regulatory: "GDPR compliance", "SOC 2 Type II"
- Business: "Launch before Q3", "Budget under $200K"
- Integration: "Must integrate with SAP via REST API"
- Organizational: "Must support SSO via company Okta"
```

## Prioritization Frameworks

### MoSCoW
```markdown
Must Have   — Non-negotiable; system fails without it.
             Test: "Will the system be useless without this?"
Should Have — Important but not critical for launch.
             Test: "Can we launch without it and add it soon after?"
Could Have  — Desirable if time and budget allow.
             Test: "Would users notice if it's missing?"
Won't Have  — Explicitly out of scope for this release.
             Test: "Can it wait for a future release?"

Recommended split: 60% Must / 20% Should / 20% Could
```

### RICE Scoring
```markdown
Reach: How many users/events per quarter?
  - Use data: analytics, user counts, transaction volumes

Impact: How much does this move the needle per user?
  - 3 = Massive (fundamental improvement)
  - 2 = High (significant improvement)
  - 1 = Medium (noticeable improvement)
  - 0.5 = Low (minor improvement)

Confidence: How sure are we about estimates?
  - 100% = High (data-backed)
  - 80% = Medium (informed estimate)
  - 50% = Low (gut feeling)

Effort: Person-weeks to deliver
  - Include design, development, testing, deployment

Score = (Reach × Impact × Confidence) / Effort
```

### Kano Model
```markdown
Categories:
  Must-Be (Basic):
    - Expected by default; absence causes dissatisfaction
    - Presence doesn't increase satisfaction
    - Example: Login works, pages load, data saves correctly

  One-Dimensional (Performance):
    - More is better; linear relationship with satisfaction
    - Example: Faster load times, more storage, better search

  Attractive (Delighters):
    - Unexpected features that create delight
    - Absence doesn't cause dissatisfaction
    - Example: Smart autocomplete, proactive notifications

  Indifferent:
    - Users don't care either way
    - Don't waste effort here

  Reverse:
    - Feature some users actively dislike
    - Proceed with caution

Classification question pair:
  1. "How would you feel if this feature IS present?"
  2. "How would you feel if this feature is NOT present?"
  Answers: Like / Expect / Neutral / Tolerate / Dislike
```

## User Story Mapping

### Building a Story Map

```markdown
Step 1: Identify the user's journey (backbone)
  Activities:   [Discover] → [Evaluate] → [Purchase] → [Use] → [Support]

Step 2: Break activities into user tasks (walking skeleton)
  Discover:     Search products | Browse categories | View recommendations
  Evaluate:     Read details | Compare items | Check reviews
  Purchase:     Add to cart | Enter payment | Confirm order
  Use:          Track order | Receive item | Rate experience
  Support:      Contact help | Return item | Get refund

Step 3: Slice horizontally for releases
  Release 1 (MVP):  Basic search | View details | Add to cart | Checkout
  Release 2:        Categories | Compare | Reviews | Order tracking
  Release 3:        Recommendations | Wishlists | Returns | Refunds
```

### Story Splitting Patterns
When a story is too large, split using these patterns:

```markdown
1. By workflow step:  "As a user I can register" →
   - Enter email and password
   - Verify email
   - Complete profile

2. By business rule:  "As a user I can apply discounts" →
   - Apply percentage discount
   - Apply fixed-amount discount
   - Apply buy-one-get-one discount

3. By data variation: "As a user I can pay" →
   - Pay with credit card
   - Pay with PayPal
   - Pay with bank transfer

4. By interface:      "As a user I can search" →
   - Search by keyword
   - Search with filters
   - Search with autocomplete

5. By quality:        "As a user I get results" →
   - Return results (basic)
   - Return results in under 200ms
   - Return results with typo tolerance
```

## Acceptance Criteria Patterns

### Given-When-Then (Gherkin)
```markdown
Scenario: [Descriptive name]
  Given [initial context / precondition]
  And [additional context]
  When [action / trigger]
  And [additional action]
  Then [expected outcome]
  And [additional outcome]
  But [exception to outcome]

Example:
  Scenario: Successful login with valid credentials
    Given the user is on the login page
    And the user has a verified account
    When the user enters valid email and password
    And clicks the "Sign In" button
    Then the user is redirected to the dashboard
    And a welcome message displays the user's name
```

### Checklist Style
```markdown
Acceptance Criteria:
  ☐ [Capability]: [measurable outcome]
  ☐ [Capability]: [measurable outcome]
  ☐ [Edge case]: [expected behavior]
  ☐ [Error case]: [expected behavior]

Example:
  ☐ User can upload files up to 50MB
  ☐ Supported formats: PDF, PNG, JPG, DOCX
  ☐ Upload progress bar shows percentage
  ☐ Unsupported format shows error with accepted types listed
  ☐ Files over 50MB show error before upload begins
  ☐ Upload resumes after network interruption
```

### Rule-Based
```markdown
Rules:
  - IF [condition] THEN [outcome]
  - IF [condition] AND [condition] THEN [outcome]
  - IF NOT [condition] THEN [alternative outcome]

Example:
  - IF order total > $100 THEN free shipping applies
  - IF order total > $100 AND user is premium THEN express shipping is free
  - IF order total <= $100 THEN standard shipping rate of $9.99 applies
```

## Requirements Traceability

```markdown
Traceability Matrix:
| Req ID | Business Need | User Story | Test Case | Status |
|--------|--------------|------------|-----------|--------|
| R-001  | BN-003       | US-012     | TC-045    | Verified |
| R-002  | BN-001       | US-003     | TC-012    | In Progress |

Purpose:
- Track every requirement from origin to validation
- Ensure no requirement is orphaned (untested)
- Support impact analysis when requirements change
- Provide audit trail for compliance
```
