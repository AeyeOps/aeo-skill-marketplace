# OpenAPI specifications — full reference

OpenAPI 3.x is the de facto standard for HTTP API contracts. A well-written spec serves as both human-readable reference and machine-readable input for client generators, mock servers, validation libraries, and gateways.

## File structure

```
docs/api/
├── openapi.yaml                 # Top-level spec
├── components/
│   ├── schemas/                 # Reusable schema definitions
│   ├── parameters/              # Reusable parameters
│   └── responses/               # Reusable responses
└── README.md                    # How to render / generate clients
```

For small APIs (one to a few endpoints), a single `openapi.yaml` is fine. For larger APIs, split into the structure above and use `$ref` to reassemble — most tooling supports this.

## Minimal valid skeleton

```yaml
openapi: 3.0.3
info:
  title: Orders API
  version: 1.0.0
  description: |
    HTTP API for placing and retrieving orders.
    See `docs/explanation/order-domain.md` for the conceptual model.
  contact:
    name: Platform team
    email: platform@example.com
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging.api.example.com/v1
    description: Staging
paths:
  /orders/{id}:
    get:
      summary: Get an order by ID
      operationId: getOrder
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        "200":
          description: Order found
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Order"
        "404":
          $ref: "#/components/responses/NotFound"
components:
  schemas:
    Order:
      type: object
      required: [id, status, items]
      properties:
        id:
          type: string
          format: uuid
        status:
          type: string
          enum: [pending, confirmed, shipped, delivered, canceled]
        items:
          type: array
          items:
            $ref: "#/components/schemas/OrderItem"
    OrderItem:
      type: object
      required: [productId, quantity]
      properties:
        productId:
          type: string
        quantity:
          type: integer
          minimum: 1
  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    Error:
      description: Generic error response
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
security:
  - bearerAuth: []
```

## Common patterns

### Authentication

Most APIs use one of:

- **Bearer JWT** (most common) — `securitySchemes.bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }`
- **API key in header** — `securitySchemes.apiKey: { type: apiKey, in: header, name: X-API-Key }`
- **OAuth 2.0** — `securitySchemes.oauth2: { type: oauth2, flows: { ... } }` — heavier, use the `OAuth2 Authorization Code Grant` flow when humans are involved, `Client Credentials` when service-to-service.

Apply globally with the top-level `security:` array, or per-operation if some endpoints are public.

### Pagination

Two common shapes:

**Offset / limit** (simple but inefficient at large offsets):

```yaml
parameters:
  - name: limit
    in: query
    schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
  - name: offset
    in: query
    schema: { type: integer, minimum: 0, default: 0 }
```

**Cursor-based** (scalable but harder for clients):

```yaml
parameters:
  - name: limit
    in: query
    schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
  - name: cursor
    in: query
    schema: { type: string }
    description: Opaque cursor returned in the previous response's `nextCursor`
```

Response includes `nextCursor` (null at the end) and the page of items.

### Error schema

A consistent error envelope helps clients handle failures uniformly:

```yaml
components:
  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          description: Stable machine-readable error code
          example: "order_not_found"
        message:
          type: string
          description: Human-readable explanation
        details:
          type: object
          additionalProperties: true
          description: Optional structured context
        traceId:
          type: string
          description: Request correlation ID for support escalation
```

Reference it from every non-2xx response.

### Versioning

Two approaches:

- **URL versioning** — `https://api.example.com/v1/...`. Simple, visible, hostile to incremental change.
- **Header versioning** — `Accept: application/vnd.example.v1+json`. Cleaner URLs, harder to debug from the address bar.

Pick one and document it in `info.description`. Don't mix.

## Handwritten vs. generated

Three approaches, in order of upfront cost:

| Approach | When it fits |
|----------|--------------|
| **Handwritten OpenAPI** | API surface is small, stable, or owned by the doc team |
| **Generated from code** (FastAPI, NestJS, tsoa, springdoc, etc.) | API is large and changes often; framework supports decorators that produce the spec |
| **OpenAPI-first** (write spec, generate server stub) | Multiple teams need to agree on the contract before implementation |

OpenAPI-first is the most rigorous but only earns its keep when the contract is genuinely shared across teams. For a single team's API, generated-from-code usually wins on maintenance.

## Validation and rendering

- **Lint**: `spectral lint openapi.yaml` (or `redocly lint`) catches structural errors and style issues
- **Render**: `redoc-cli build openapi.yaml -o api.html` for a static site, or host a Swagger UI / Redoc instance
- **Mock**: `prism mock openapi.yaml` runs a mock server from the spec
- **Client generation**: `openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o client/`

## Anti-patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|----|
| Schema-less response | Response body is described in prose, not in the schema | Define `components.schemas.X` and `$ref` it |
| `anyOf` everything | Loose schemas with `type: object` and no `properties` | Specify the actual shape; readers and codegen need it |
| Inline duplication | The same schema repeated across 10 endpoints | Define once in `components/schemas`, `$ref` everywhere |
| Drift from reality | Spec says "v1.5" but the deployed API is on v2 | Generate from code, or gate deploys on spec freshness |
| Examples that don't match the schema | An example with fields the schema doesn't allow | Run a linter; examples should validate against their schema |

## Voice

- Terse, factual, present tense. "Returns the order matching `id`", not "This endpoint will return the order...".
- One-sentence summaries; longer descriptions in `description:` (markdown is allowed).
- `operationId` should be a stable identifier (`getOrder`, `listOrders`, `createOrder`) — codegen uses it as the function name in generated clients.
