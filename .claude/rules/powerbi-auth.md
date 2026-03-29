# Power BI Auth Rules — WhyBoard (Phase 2)
> MSAL OAuth, Power BI REST API patterns, token handling.
> Do not build any of this until Phase 1 is complete and deployed.

---

## Auth Architecture

**Flow type**: Delegated OAuth (Authorization Code Flow)
**Tenant type**: Single tenant — ScriptsHub Azure AD only
**User**: ScriptsHub internal team members with Microsoft work accounts
**Token storage**: Server-side session only — never exposed to frontend

```
User clicks "Connect Power BI"
    → Backend redirects to Microsoft login
    → User authenticates with ScriptsHub Microsoft account
    → Microsoft redirects to /api/auth/callback with auth code
    → Backend exchanges code for access token + refresh token
    → Tokens stored in server-side session (never sent to frontend)
    → Frontend receives only: { authenticated: true, user_email: "..." }
```

---

## Azure AD App Registration Requirements

Before writing any auth code, confirm these are set up in Azure Portal:

```
App Name: WhyBoard (Internal)
Tenant: ScriptsHub Azure AD tenant
Supported account types: Single tenant only

Redirect URIs:
  - http://localhost:8000/api/auth/callback  (development)
  - https://[railway-url]/api/auth/callback  (production)

API Permissions (Delegated):
  - Power BI Service → Dataset.Read.All
  - Power BI Service → Report.Read.All
  - Power BI Service → Workspace.Read.All

Required environment variables:
  AZURE_CLIENT_ID=<from app registration>
  AZURE_TENANT_ID=<ScriptsHub tenant ID>
  AZURE_CLIENT_SECRET=<from app registration secrets>
  SESSION_SECRET=<random 32-char string>
```

---

## MSAL Implementation (auth.py)

```python
import msal
from fastapi import HTTPException

SCOPES = ["https://analysis.windows.net/powerbi/api/Dataset.Read.All",
          "https://analysis.windows.net/powerbi/api/Workspace.Read.All"]

def get_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_CLIENT_ID,
        client_credential=settings.AZURE_CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"
    )

def get_auth_url() -> str:
    app = get_msal_app()
    return app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=settings.REDIRECT_URI
    )

def exchange_code_for_token(code: str) -> dict:
    app = get_msal_app()
    result = app.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=settings.REDIRECT_URI
    )
    if "error" in result:
        raise HTTPException(status_code=401, detail=result.get("error_description"))
    return result  # contains access_token, refresh_token, expires_in
```

---

## Power BI REST API Patterns (powerbi.py)

### Base URL
```
https://api.powerbi.com/v1.0/myorg/
```

### Key Endpoints

```python
import httpx

PBI_BASE = "https://api.powerbi.com/v1.0/myorg"

async def get_workspaces(token: str) -> list:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{PBI_BASE}/groups",
            headers={"Authorization": f"Bearer {token}"}
        )
        r.raise_for_status()
        return r.json().get("value", [])

async def get_datasets(token: str, workspace_id: str) -> list:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{PBI_BASE}/groups/{workspace_id}/datasets",
            headers={"Authorization": f"Bearer {token}"}
        )
        r.raise_for_status()
        return r.json().get("value", [])

async def get_tables(token: str, dataset_id: str) -> list:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{PBI_BASE}/datasets/{dataset_id}/tables",
            headers={"Authorization": f"Bearer {token}"}
        )
        r.raise_for_status()
        return r.json().get("value", [])

async def query_table(token: str, dataset_id: str, table_name: str, top: int = 1000) -> list:
    """Execute DAX query and return rows as list of dicts."""
    dax_query = f"EVALUATE TOPN({top}, '{table_name}')"
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PBI_BASE}/datasets/{dataset_id}/executeQueries",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"queries": [{"query": dax_query}], "serializerSettings": {"includeNulls": True}}
        )
        r.raise_for_status()
        results = r.json()
        rows = results["results"][0]["tables"][0]["rows"]
        return rows  # list of dicts — pipe directly into pandas
```

### Converting DAX Results to DataFrame

```python
import pandas as pd

def dax_rows_to_dataframe(rows: list) -> pd.DataFrame:
    """Convert Power BI DAX query result rows to DataFrame.
    Column names come back as 'TableName[ColumnName]' — strip the prefix."""
    df = pd.DataFrame(rows)
    df.columns = [col.split("[")[-1].rstrip("]") for col in df.columns]
    return df
```

---

## Token Refresh

Access tokens expire in 1 hour. Handle silently:

```python
def get_valid_token(session: dict) -> str:
    """Return valid token, refreshing if expired."""
    app = get_msal_app()
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]
    raise HTTPException(status_code=401, detail="Session expired. Please reconnect Power BI.")
```

---

## Security Rules

- **Never** send access tokens to the frontend — not even for debugging
- **Never** log token values — log only token expiry time and user email
- **Always** validate that the authenticated user's email ends in `@scriptshub.net` (or the actual domain)
- Token storage: use `itsdangerous` signed server-side sessions or Redis session store
- On logout: clear session completely, do not just remove the token field
