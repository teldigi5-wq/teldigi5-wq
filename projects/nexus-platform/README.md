# NEXUS Platform

> A zero-cost, local-first distributed API platform built to learn enterprise software engineering by building it.

NEXUS is a portfolio engineering project focused on the same classes of problems solved by modern integration and API platforms: routing, service boundaries, authentication, observability, resilience and developer experience.

## Stage 1 — Core Platform

Current MVP:

- Java 21 + Spring Boot
- Spring Cloud API Gateway
- Independent User Service
- PostgreSQL
- Docker Compose
- Health endpoints
- REST API routing through the gateway
- Containerized, reproducible local environment

## Architecture

```text
Client
  |
  v
NEXUS Gateway :8080
  |
  +---- /api/users/** ----> User Service :8081 ----> PostgreSQL :5432
```

## Run for free

Requirements: Docker Desktop / Docker Engine.

```bash
docker compose up --build
```

Test:

```bash
curl http://localhost:8080/api/users
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Poojana","email":"poojana@example.com"}'
```

Gateway health:

```bash
curl http://localhost:8080/actuator/health
```

User-service health:

```bash
curl http://localhost:8081/actuator/health
```

## Roadmap

- [x] Stage 1: gateway + microservice + PostgreSQL + Docker
- [ ] Stage 2: JWT authentication, RBAC and API keys
- [ ] Stage 3: Redis rate limiting and caching
- [ ] Stage 4: RabbitMQ/Kafka event-driven services
- [ ] Stage 5: circuit breakers, retries and fault simulation
- [ ] Stage 6: OpenTelemetry + Prometheus + Grafana
- [ ] Stage 7: CLI + OpenAPI/SDK generation
- [ ] Stage 8: local AI Agent Gateway with Ollama
- [ ] Stage 9: local Kubernetes deployment
- [ ] Stage 10: security lab + chaos lab

## Engineering principles

1. Local-first and zero recurring software cost.
2. Every feature must be explainable, testable and observable.
3. Prefer small independently deployable components.
4. Build the core correctly before adding visual complexity.
5. Document design decisions and trade-offs.

## Author

**Poojana Kaveesh** — BSc (Hons) IT undergraduate at SLIIT.

This project is being built as a serious software-engineering portfolio and learning system.