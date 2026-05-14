# Marimo Homelab Workspace

Self-hosted Marimo notebook workspace for PostgreSQL analytics, dashboards, and experiments.

## Stack

- Marimo
- PostgreSQL
- Docker / Docker Compose
- Portainer
- Cloudflare Tunnel

---

# Features

- Self-hosted notebook environment
- PostgreSQL integration
- Persistent notebook storage
- Dockerized deployment
- Environment variable support
- Git-friendly workflow
- Cloudflare Tunnel compatible

---

# Project Structure

```text
.
├── compose.yaml
├── Dockerfile
├── requirements.txt
├── stack.env.example
├── .gitignore
└── notebooks/
````

---

# Setup

## 1. Copy environment file

```bash
cp stack.env.example stack.env
```

Edit `stack.env` with your actual credentials.

---

## 2. Deploy with Portainer

Deploy the stack using:

* `compose.yaml`
* `stack.env`

---

# Environment Variables

Example:

```env
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

MARIMO_PASSWORD=change_this_password
```

---

# Access

Default local URL:

```text
http://localhost:2718
```

Example public URL:

```text
https://marimo.yourdomain.com
```

---

# PostgreSQL Connection Example

```python
import os
import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = (
    f"postgresql://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)

df = pd.read_sql(
    "SELECT NOW() AS current_time",
    engine
)

df
```

---

# Useful SQL Queries

## Show all tables

```sql
SELECT schemaname, tablename
FROM pg_tables
ORDER BY schemaname, tablename;
```

## Show columns

```sql
SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

---

# Security Notes

This deployment exposes a Python execution environment.

Recommended:

* Use Cloudflare Access
* Use strong passwords
* Use readonly PostgreSQL users
* Do not expose without authentication

---

# Development Workflow

## Install new dependencies

Add packages to:

```text
requirements.txt
```

Then redeploy the stack.

---

# Git Workflow

Recommended:

```bash
git add .
git commit -m "update notebooks"
git push
```

Do NOT commit:

* `stack.env`

---

# License

MIT
