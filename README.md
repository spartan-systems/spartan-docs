# Spartan API docs

The public reference for the Spartan API, served at https://docs.spartansystems.us by GitHub Pages.

A static page: `index.html` renders `openapi.json` with [Scalar](https://github.com/scalar/scalar) (pinned in the
`<script>` tag). There is no build step.

## Updating

`openapi.json` is generated. Don't edit it by hand.

| To change | Edit |
|---|---|
| An endpoint's summary, description or parameters | the attributes on its action in `spartan-api` (`[SwaggerOperation]`, `[SwaggerParameter]`, `[SwaggerSchema]`), deploy, then sync |
| The intro, auth, limits, errors and versioning sections | `guide.md`, then sync |
| A sample response | `examples/<operationId>.json` (a real response, trimmed to a couple of rows), then sync |
| Sidebar groups and their order | `spec["tags"]` in `scripts/sync-spec.py` |

```bash
scripts/sync-spec.py                                          # from production
scripts/sync-spec.py http://localhost:5186/api/v1/openapi.json  # from a local API
```

The script fetches the API's `/api/v1/openapi.json`, pins the server URL to production, folds in `guide.md`,
the tag order and the examples, and writes `openapi.json`. Commit the result.

## Previewing

```bash
python3 -m http.server 8091
```

Then open http://localhost:8091.
