The Spartan API serves the same DLA procurement data as the Spartan app: NSNs and their part numbers, DLA award history, open DIBBS solicitations, no-bid solicitations and CAGE companies. It is a read-only JSON API over HTTPS.

## Getting started

1. **Get an API key.** Sign in to [Spartan](https://data.spartansystems.us), open **Settings → API Keys** and create a key. Keys are available on paid plans. The key is shown once, so copy it somewhere safe.
2. **Send it in the `X-Api-Key` header** on every request.
3. **Make a call:**

```bash
curl -H "X-Api-Key: sk_live_..." \
  "https://calf-lenient-officially.ngrok-free.app/api/v1/search?q=o%20ring&pageSize=5"
```

Every endpoint is a `GET` and returns JSON with camelCase field names.

## Authentication

Every request needs your key in the `X-Api-Key` header. Keep it server-side: anyone holding it can spend your quota. If a key leaks, revoke or regenerate it under **Settings → API Keys**; the old key stops working at once.

A key works only while your company's subscription is active.

## Rate limits and quota

| Limit | Default |
|---|---|
| Requests per minute, per key | 60 |
| Units per calendar month (UTC), per key | 10,000 |

Each request costs 1 unit. Every request that passes the key check counts, including ones that return `400` or `404`. Need more? Contact us.

Every response carries your remaining allowance:

| Header | Meaning |
|---|---|
| `X-RateLimit-Limit` / `X-RateLimit-Remaining` | Requests allowed this minute, and how many are left |
| `X-RateLimit-Reset` | When the minute window resets (Unix seconds) |
| `X-Usage-Limit` / `X-Usage-Remaining` | Units allowed this month, and how many are left |
| `X-Usage-Reset` | When the month resets (Unix seconds) |

Over either limit you get `429 Too Many Requests`. A per-minute `429` also has a `Retry-After` header in seconds.

## Errors

Errors return a JSON body with a `message`.

| Status | Meaning |
|---|---|
| `400` | A parameter is missing or malformed. Validation errors list each field under `errors`. |
| `401` | The `X-Api-Key` header is missing, or the key is invalid or revoked. |
| `403` | The key's company has no active subscription (`"code": "subscription_required"`). |
| `404` | Nothing matches, e.g. an unknown NIIN or CAGE code. |
| `429` | Rate limit or monthly quota spent. See the headers above. |
| `503` | We couldn't confirm your subscription just then. Retry after a moment. |

## Identifiers

- **NIIN**: 9 digits, e.g. `012345678`. **NSN**: 13 digits, the 4-digit FSC followed by the NIIN, e.g. `5330-01-234-5678`. Endpoints take either, with or without dashes, and return them without dashes.
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
