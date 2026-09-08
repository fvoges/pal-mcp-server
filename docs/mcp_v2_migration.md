# MCP Python SDK v2 Migration (Not Yet Done)

`requirements.txt` currently pins `mcp>=1.0.0,<2.0.0`. This document explains why, and what a
future migration to `mcp` v2 would involve.

## Why the pin exists

`requirements.txt` previously had an unbounded floor pin (`mcp>=1.0.0`), which meant CI always
installed whatever the latest `mcp` release was at run time. The `mcp` SDK shipped a breaking
2.0.0 major release (spec revision 2026-07-28) that removed the decorator-based `Server` API
this repo's `server.py` relies on, which broke CI (`test (3.13)`/`3.14`) with no code changes on
our side — CI simply picked up `mcp==2.2.0` on its next run.

Locally this went unnoticed because dev virtualenvs had `mcp==1.27.0` installed from before the
2.0 release and were never reinstalled from a clean `requirements.txt`.

The SDK maintainers' own guidance for projects not ready to migrate is to pin `<2` — v1.x is in
maintenance mode and continues to receive security fixes. See the official migration guide:
<https://py.sdk.modelcontextprotocol.io/migration/>.

## What changes in v2 (for when we do migrate)

This is a real API rewrite, not a mechanical rename:

- **Decorators are gone.** `@server.list_tools()`, `@server.call_tool()`, `@server.list_prompts()`,
  `@server.get_prompt()` are replaced by keyword-only constructor arguments on `Server(...)`:
  `on_list_tools`, `on_call_tool`, `on_list_prompts`, `on_get_prompt`.
- **Handler signatures change shape.** Handlers now take a `RequestContext` first argument and a
  typed params object, and return typed `*Result` objects (e.g. `ListToolsResult(tools=[...])`
  instead of a bare `list[Tool]`).
- **`InitializationOptions`/`stdio_server` usage changes.** `stdio_server()` no longer takes
  `InitializationOptions` as a second call at the bottom of `main()`; the server config now flows
  through the `Server(...)` constructor.
- **New hard dependencies**: `opentelemetry-api` (every outbound request carries a `_meta`
  tracing envelope) and `httpx2` (replaces `httpx` + `httpx-sse`).
- **Protocol goes stateless**: the 2026-07-28 spec drops the `initialize` handshake for
  streamable HTTP; not directly relevant to our stdio-only usage today, but part of the same
  release.

Affected code in this repo: `server.py` (all four decorator handlers, `InitializationOptions`,
the `stdio_server()` call in `main()`) — roughly 1550 lines, this is the live entry point used
on every tool call, so the migration should get its own dedicated PR with full manual testing
against a real MCP client, not be bundled into an unrelated change.

## When to revisit

- If `mcp` v1.x stops receiving security fixes.
- If a feature we need only exists in v2 (e.g. new spec capabilities).
- Proactively, on a slow week, as its own scoped effort.
