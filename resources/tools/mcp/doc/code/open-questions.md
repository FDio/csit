# Open Questions

The following items cannot be established from this repository:

1. Which container registry, orchestrator, rollout policy, and production
   resource limits are used outside local Docker Compose?
2. Which CI system, if any, runs the documented server/client tests and Docker
   builds?
3. Which production CORS origins, AWS profile/role policy, and S3-compatible
   endpoint are expected in each deployment environment?
4. What retention and publication guarantees apply to the external CSIT
   parquet prefixes and FD.io result-log URLs?
5. Which exact Codex, Claude Code, and Claude Desktop versions are supported by
   the project, and does the selected Claude Desktop version accept remote
   Streamable HTTP MCP without a bridge?

Everything else in this guide is derived from the checked-in source,
configuration, manifests, tests, and Compose files.
