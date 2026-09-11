# Integration With Codex And Claude

The MCP endpoint is:

```text
http://localhost:8000/mcp
```

Verify `GET http://localhost:8000/ready` before diagnosing an MCP client. A
healthy process may still have unavailable data.

## Codex

With a Codex CLI version that supports remote MCP registration:

```sh
codex mcp add csit_mcp --url http://localhost:8000/mcp
codex mcp list
```

Codex CLI, the Codex IDE extension, and the ChatGPT desktop app on the same
host share MCP configuration. See the
[official Codex MCP documentation](https://developers.openai.com/docs/extend/mcp?surface=cli)
for current UI, CLI, and `config.toml` options.

Restart or open a new Codex task if the tool inventory was captured before the
server was registered. A message saying `csit_mcp` is not exposed means the MCP
server is not part of that task's available tool set; it does not imply a CSIT
data or serialization failure.

Useful prompts:

```text
Use csit_mcp datasets, columns, and values before choosing filters.
Use trending_catalog to find logical VPP MRR series, then fetch selected series.
Use comparison_catalog to find a meaningful DUT-version comparison.
Check server://info and readiness metadata before diagnosing data_unavailable.
```

## Claude Code

Use the Claude Code MCP management command available in the installed version
to register a remote HTTP server named `csit_mcp` at the endpoint above. CLI
syntax changes between releases, so confirm it with the local
`claude mcp --help` rather than copying an unverified command.

After registration, verify that Claude lists `datasets` and `server://info`
before issuing data queries.

## Claude Desktop

Whether Claude Desktop accepts remote Streamable HTTP MCP URLs directly depends
on the installed release. If it does, configure the same endpoint. If it
accepts only local stdio server definitions, use an MCP HTTP-to-stdio bridge
approved for that environment. This repository does not ship or configure such
a bridge.

Do not place AWS credentials in AI-client MCP configuration. Credentials belong
to the server process/container only.

## Discovery-First Pattern

1. Read `server://info` or call `datasets()`.
2. Call `columns(dataset)` to understand available dimensions and result
   metadata.
3. Call `values(dataset, column, limit=...)` for concrete filter values.
4. Prefer focused catalog/series/table/comparison tools for dashboard-shaped
   questions.
5. Use generic data tools with filters, selected columns, aggregation, and a
   small limit.
6. Follow `has_more`/`next_offset` only when the task needs more rows.

For telemetry, call `telemetry_metrics` with no metric name to discover names,
then request one metric and narrow by label or result dimensions.

## Capability Boundaries

- All 27 public tools are read-only.
- `server://info` is public.
- `data://parquet/{query}` is private/internal and preview-only.
- The browser client is not a general MCP proxy.
- Browser exports are client HTTP endpoints, not MCP tools.
- Telemetry is MCP-accessible but has no dedicated browser tab.
- Large generic responses may return `response_too_large`; reduce the query
  rather than requesting the private resource as a workaround.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| MCP server not visible in the AI task | Client registration, task restart/tool refresh, and endpoint reachability. |
| Tool is visible but returns `data_unavailable` | `/ready`, `server://info.data`, configuration errors, and dataset status. |
| Unknown or stale logical series ID | Re-run the relevant catalog and use the returned ID. |
| `response_too_large` | Reduce columns/limit, add filters, aggregate, or use a compact analysis tool. |
| Telemetry reports zero samples | Inspect per-dataset telemetry decode/parse counters and truncation metadata. |
