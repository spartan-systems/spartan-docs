The Spartan API serves the same DLA procurement data as the Spartan app: NSNs and their part numbers, DLA award history, open DIBBS solicitations, no-bid solicitations and CAGE companies. It is a read-only JSON API over HTTPS.

## Getting started

1. **Get an API key.** Sign in to [Spartan](https://data.spartansystems.us), open **Settings → API Keys** and create a key. Keys are available on paid plans. The key is shown once, so copy it somewhere safe.
2. **Send it in the `X-Api-Key` header** on every request.
3. **Make a call:**

```bash
curl -H "X-Api-Key: sk_live_..." \
  "{{API_URL}}/api/v1/search?q=o%20ring&pageSize=5"
```

Every endpoint is a `GET` and returns JSON with camelCase field names. Dates are ISO 8601 (`2026-05-14`), and fields DLA leaves blank are `null`.

## Authentication

Every request needs your key in the `X-Api-Key` header. Keep it server-side: anyone holding it can spend your quota. If a key leaks, revoke or regenerate it under **Settings → API Keys**; the old key stops working at once.

A key works only while your company's subscription is active.

## Rate limits and quota

| Limit | Default |
|---|---|
| Requests per minute, per key | 60 |
| Units per calendar month (UTC), per key | 10,000 |

Each request costs 1 unit. Every request that passes the key check counts, including ones that return `400` or `404`. Need more? Contact us.

Responses to accepted requests carry your remaining allowance (the `X-Usage-*` headers only when the key has a monthly quota):

| Header | Meaning |
|---|---|
| `X-RateLimit-Limit` / `X-RateLimit-Remaining` | Requests allowed this minute, and how many are left |
| `X-RateLimit-Reset` | When the minute window resets (Unix seconds) |
| `X-Usage-Limit` / `X-Usage-Remaining` | Units allowed this month, and how many are left |
| `X-Usage-Reset` | When the month resets (Unix seconds) |

Over either limit you get `429 Too Many Requests`. A per-minute `429` also has a `Retry-After` header in seconds.

## Errors

Key, subscription and limit errors (`401`, `403`, `429`, `503`) and the API's own parameter checks (`400`, e.g. an unknown set-aside code) return `{"message": "..."}`, with a `code` on some. A parameter of the wrong type (`page=abc`) and a `404` return a standard [problem details](https://www.rfc-editor.org/rfc/rfc9457) body (`title`, `status`, and for invalid parameters `errors`, keyed by parameter). Branch on the status code, not the body.

| Status | Meaning |
|---|---|
| `400` | A parameter is missing or malformed. |
| `401` | The `X-Api-Key` header is missing, or the key is invalid or revoked. |
| `403` | The key's company has no active subscription (`"code": "subscription_required"`). |
| `404` | Nothing matches, e.g. an unknown NIIN or CAGE code. |
| `429` | Rate limit or monthly quota spent. See the headers above. |
| `503` | We couldn't confirm your subscription just then. Retry after a moment. |

## Paging

List endpoints take `page` (from 1) and `pageSize`, and return one page with `totalCount`, `page` and `pageSize`. The rows are in `items`, except search, which calls them `results`. A page past the end comes back empty, so you can page until a response has no rows.

An NSN's record (`GET /api/v1/nsn/{niin}`) doesn't include its awards or solicitations: page through awards with `GET /api/v1/nsn/{niin}/awards`, and find solicitations with `GET /api/v1/solicitations?nsn=` and its 13-digit NSN.

## Identifiers

- **NIIN**: 9 digits, e.g. `012345678`. **NSN**: 13 digits, the 4-digit FSC followed by the NIIN, e.g. `5330-01-234-5678`. Endpoints take either, with or without dashes, and return them without dashes. The one exception is the `nsn` filter on `GET /api/v1/solicitations`, which needs the full 13-digit NSN.
- **CAGE code**: 5 characters, e.g. `1CAY9`.

## How fresh the data is

| Data | Updated |
|---|---|
| DIBBS solicitations | Every 4 hours |
| No-bid solicitations | Daily, 06:00 Pacific |
| Awards, stock, forecasts and other DLA FOIA files | Nightly, as DLA publishes them. DLA's award files run months behind, so the last year of awards is still filling in. |
| Search results | Rebuilt nightly |

## Versioning

Everything here is under `/api/v1`. Within v1 we only add things: new endpoints, new optional parameters and new response fields. Write your client to ignore fields it doesn't know. Removing or renaming a field, or changing what one means, would come as `/api/v2`, with v1 kept running while you move over.

One exception, on 2026-10-19 before any customer had used v1: every endpoint moved to the response shapes documented here (awards became paged; the NSN record, solicitations, no-bid solicitations and companies got their own trimmed models with ISO dates).
