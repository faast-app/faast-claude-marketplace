# Senior Backend Architect — Claude Code Plugin

An expert-level backend engineering agent for Claude Code. Provides deep analysis, code review, architecture design, debugging, database design, and technical documentation across the full backend technology stack.

---

## What it does

This plugin installs a specialized agent that thinks and acts like a Senior Backend Architect with 15+ years of production experience. It goes beyond surface-level suggestions: it reads your code, traces execution paths, identifies root causes, and delivers concrete solutions with the reasoning behind every decision.

---

## Capabilities

### Languages & Frameworks
- **.NET** — .NET Core 3.x through .NET 10, ASP.NET Core, EF Core, Minimal APIs, SignalR, gRPC, Worker Services, MAUI
- **Python** — Django, FastAPI, Flask, SQLAlchemy, Celery, asyncio
- **Java / Kotlin** — Spring Boot, Spring Cloud, Hibernate, Jakarta EE
- **JavaScript / TypeScript** — Node.js, Express, NestJS, Deno, Bun
- **C / C++** — Systems programming, performance-critical services
- **Other** — Go, Rust, PHP (Laravel), Ruby (Rails)

### Databases (DBA-level)
- **Relational**: SQL Server, PostgreSQL, MySQL/MariaDB, Oracle, SQLite
- **NoSQL**: MongoDB, Redis, Cassandra, DynamoDB, CosmosDB, Elasticsearch
- Schema design, query optimization, execution plan analysis, indexing strategies, migrations, replication, sharding, partitioning, backup/recovery

### Architecture & Patterns
- Clean Architecture, Hexagonal, Onion, CQRS, Event Sourcing, DDD
- Microservices, Modular Monolith, Serverless, Event-Driven Architecture
- REST, GraphQL, gRPC, WebSockets, API versioning
- RabbitMQ, Kafka, Azure Service Bus, outbox pattern, saga pattern, circuit breaker

### DevOps & Infrastructure
- Docker, Kubernetes, CI/CD pipelines
- Azure, AWS, GCP
- Application Insights, Serilog, ELK, Prometheus/Grafana

---

## How to use

### Command: `/architect`

The primary entry point for any backend task.

```
/architect <describe what you need>
```

The agent processes your request through four phases:

1. **Understand** — Captures requirements, constraints, and context. Asks one clarifying question if critical information is missing.
2. **Analyze** — Deep inspection of code, architecture, or design problem. Findings are classified by severity.
3. **Recommend** — Prioritized, concrete recommendations with corrected code and trade-off analysis.
4. **Implement** — Production-quality implementation with error handling, logging hooks, and testability baked in.

### Usage examples

```
/architect review my repository pattern — I think there's a DbContext lifetime issue
```

```
/architect design a caching layer for my product catalog API using Redis
```

```
/architect my .NET 8 endpoint takes 30 seconds to respond, help me diagnose it
```

```
/architect design the database schema for a multi-tenant SaaS invoicing system in PostgreSQL
```

```
/architect I'm migrating from .NET 6 to .NET 9, what breaking changes should I expect?
```

```
/architect generate OpenAPI documentation for all endpoints in /src/Api/Controllers
```

---

## When the agent activates automatically

Beyond the explicit `/architect` command, the agent activates on its own when Claude Code detects:

- A request to debug a complex or multi-layer backend error
- A request to design or review a database schema
- A request to review existing backend code for quality, bugs, or anti-patterns
- A request to propose or evaluate an architectural approach
- A request to generate API documentation
- After significant backend code is written — the agent proactively reviews quality, patterns, and improvement opportunities
- A .NET framework migration request

---

## Severity classification

When reviewing code or architecture, findings are classified as:

| Level | Meaning |
|-------|---------|
| Critical | Bugs, security vulnerabilities, data corruption risks |
| Important | Performance issues, anti-patterns, maintainability concerns |
| Suggestion | Improvements, modernization, code style |
| Good Practice | Things done well — acknowledged explicitly |

---

## Language

The agent responds in the language you use. Write in Spanish, get answers in Spanish. Write in English, get answers in English.

---

## Author

Carlos Fuentes — [carlos.fuentes@faast.cl](mailto:carlos.fuentes@faast.cl)

## License

MIT License — see [LICENSE](LICENSE) for details.
