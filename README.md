# 📊 Marimo Homelab Data Visualization Workspace

A premium, self-hosted, git-friendly **Marimo** reactive notebook environment. Specially configured for data science, modeling, and real-time visualization querying from your homelab's **PostgreSQL** database.

Designed to be built and deployed effortlessly on **Portainer Stacks** or locally via **Docker Compose**.

---

## 🛠️ The Architecture & Network Flow

Because your PostgreSQL database runs in a separate service container exposed on your homelab host (`localhost:5432`), this Marimo stack is configured to bridge into the host namespace securely via a host network gateway.

```mermaid
graph TD
    subgraph Host["Homelab Server (Host OS)"]
        HostGateway["Host Gateway (172.17.0.1 / host-gateway)"]
        PostgresPort["PostgreSQL Service (localhost:5432)"]
        HostGateway --> PostgresPort
    end

    subgraph DockerBridge["Marimo Container Context"]
        MarimoApp["Marimo Notebook Server (Port 2718)"]
        HostInternal["host.docker.internal"]
        
        MarimoApp -->|Connects to| HostInternal
    end
    
    HostInternal -->|Routes through| HostGateway
```

---

## ⚡ Features

* **Reactive Notebooks:** Powered by **Marimo** (cells run automatically when code or slider dependencies change, eliminating out-of-order execution bugs).
* **SQL Native Editor:** Built on Marimo's official `latest-sql` base container, enabling you to write native, syntax-highlighted SQL directly against your engines.
* **Pre-Baked Data Libraries:** Fully loaded with:
  * **Database & SQL:** `psycopg2-binary`, `asyncpg`, `sqlalchemy`, `sqlmodel`
  * **Analytics:** `pandas`, `polars`, `numpy`
  * **Data Visualizations:** `plotly`, `altair`, `matplotlib`, `seaborn`, `plotnine` (ggplot2-equivalent)
* **Production Security:** Locked behind password-token authentication, loaded securely via `env_file`.
* **State Persistence:** Mounted `./notebooks` mapping guarantees that none of your dashboard code is lost when the container is recreated.

---

## 📁 Repository Structure

```text
.
├── Dockerfile                  # Extends latest-sql image and layers custom libs
├── docker-compose.yml          # Maps ports, volumes, and shell-expands secure token
├── requirements.txt            # Pre-installed DB/Visualization packages
├── stack.env                   # Live credentials configuration (git-ignored)
├── stack.env.example           # Public template for setting up credentials
├── .gitignore                  # Configured to secure stack.env
└── notebooks/                  # Volume folder mounting your notebooks
    └── postgres_visualization.py # Template notebook with credential forms and charts
```

---

## 🚀 Getting Started (Quick Setup)

### 1. Copy and Configure the Credentials
Copy the example environment configuration into a live file:
```bash
cp stack.env.example stack.env
```
Open `stack.env` and enter your preferred Marimo login password and PostgreSQL connection details:
```env
# Marimo Service Configuration
MARIMO_PORT=2718
MARIMO_TOKEN_PASSWORD=your_secure_homelab_password_here

# PostgreSQL Database (Running on Homelab Host)
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here
```

### 2. Deploy locally
Build and run the container locally:
```bash
docker compose up --build -d
```

### 3. Deploy via Portainer
When deploying as a **Portainer Stack**:
1. Copy the contents of `docker-compose.yml` into the Web editor.
2. In the "Environment variables" section, define:
   * `MARIMO_PORT` = `2718`
   * `MARIMO_TOKEN_PASSWORD` = `your_preferred_password`
3. Hit **Deploy the stack**.

---

## 🔌 Inside the Notebooks: Connecting to Postgres

Once you open your Marimo dashboard at `http://localhost:2718` (or your private domain) and enter your password, you can query your database using any of these patterns:

### A. Pandas & SQLAlchemy
```python
import pandas as pd
import sqlalchemy as sa
import os

# Grab credentials from environmental variables automatically loaded by stack.env!
db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@host.docker.internal:5432/{os.getenv('POSTGRES_DB')}"
engine = sa.create_engine(db_url)

# Read query directly to DataFrame
df = pd.read_sql("SELECT * FROM your_table LIMIT 100", engine)
```

### B. Polars & ConnectorX (Ultra-Fast)
```python
import polars as pl
import os

db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@host.docker.internal:5432/{os.getenv('POSTGRES_DB')}"
df = pl.read_database("SELECT * FROM your_table LIMIT 100", db_url)
```

---

## 🔒 Security Best Practices

* **Always use Environment Variables:** Never hardcode your Postgres password or Marimo tokens into the `.py` notebook files. They are automatically injected by `stack.env` and accessible via `os.getenv()`.
* **Private Network Bindings:** If using Cloudflare Tunnels, make sure to configure Cloudflare Access policy constraints on top of the Marimo login screen for multi-factor authentication.
* **Keep Site Packages Clean:** If you need a new Python package, simply list it in `requirements.txt` and redeploy or restart the Docker container to trigger an automatic layer update.

---

## 📄 License
MIT License. Self-hosted with ❤️ in your homelab.
