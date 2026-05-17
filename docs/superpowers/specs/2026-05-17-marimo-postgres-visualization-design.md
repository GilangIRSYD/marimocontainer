# Design Spec: Dockerized Marimo Visualization Service for PostgreSQL

This document outlines the architecture, configuration, and implementation design for deploying a Marimo reactive notebook service connected to a PostgreSQL database on a homelab server.

## 1. Objectives & Success Criteria

- **Target Service:** Marimo running in a Docker container in **Edit Mode**.
- **Security:** Protected by password-token authentication loaded via environment variables (`stack.env`).
- **Database Integration:** Connects to an existing PostgreSQL database container running on the same host (exposed on host `localhost:5432`).
- **Libraries:** Pre-installed packages for Postgres connectivity, database tools, data science, and advanced data visualization.
- **Portability & Deployment:** Easy to build locally and deploy via **Portainer Stack** using Docker Compose.
- **Persistence:** Notebooks are stored and modified inside a host-mounted directory (`./notebooks`) to prevent data loss.

---

## 2. Directory Layout

The service will be structured in the project directory as follows:

```
/Users/gilangsafera/Documents/gilang/code/notebook/
├── Dockerfile                   # Custom Docker image building on Marimo SQL base
├── docker-compose.yml           # Configuration for local container and Portainer
├── requirements.txt             # Pre-installed Python libraries
├── stack.env                    # Live environment credentials (git-ignored)
├── stack.env.example            # Example template for setting up credentials
├── .gitignore                   # Configured to ignore stack.env and prevent leaking secrets
└── notebooks/                   # Volume mapping directory for notebook storage
    └── postgres_visualization.py # Default template notebook showing database visualization
```

---

## 3. Configuration Specifications

### 3.1. Requirements (`requirements.txt`)
Provides all libraries requested for robust data analysis and charting.

```text
# Database Connection & SQL tools
psycopg2-binary>=2.9.9
asyncpg>=0.29.0
sqlalchemy>=2.0.30
sqlmodel>=0.0.19

# Data Manipulation
pandas>=2.2.2
polars>=0.20.26
numpy>=1.26.4

# Advanced Visualizations
plotly>=5.22.0
altair>=5.3.0
matplotlib>=3.9.0
seaborn>=0.13.2
plotnine>=0.13.6
```

### 3.2. Dockerfile (`Dockerfile`)
Uses the official SQL-optimized Marimo image as the base to speed up builds and provide out-of-the-box SQL editor integrations.

```dockerfile
FROM ghcr.io/marimo-team/marimo:latest-sql

WORKDIR /app

# Copy dependency definition and install standard packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Create volume target folder
RUN mkdir -p /app/notebooks

# Expose default Marimo port
EXPOSE 2718

# Default run command pointing to notebooks folder
CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "notebooks/"]
```

### 3.3. Environment Configuration (`stack.env` and `stack.env.example`)
Establishes the configuration variables for Portainer.

**`stack.env.example`**
```env
# Marimo Server Port Mapping on Host
MARIMO_PORT=2718

# Secure Token for Accessing Marimo Editor
MARIMO_TOKEN_PASSWORD=replace_with_your_secure_password
```

### 3.4. Docker Compose (`docker-compose.yml`)
Configures the network host gateway mapping (`host.docker.internal`), volume persistence, port mappings, and passes the password token to the Marimo process.

```yaml
version: '3.8'

services:
  marimo:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: marimo-visualization-service
    ports:
      - "${MARIMO_PORT:-2718}:2718"
    volumes:
      - ./notebooks:/app/notebooks
    env_file:
      - stack.env
    extra_hosts:
      - "host.docker.internal:host-gateway"
    command: >
      marimo edit 
      --host 0.0.0.0 
      --port 2718 
      --token 
      --token-password=${MARIMO_TOKEN_PASSWORD} 
      notebooks/
    restart: unless-stopped
```

---

## 4. Marimo Template Notebook (`notebooks/postgres_visualization.py`)

A preconfigured Marimo notebook template written in pure Python that will showcase connection and plotting patterns.

```python
import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium", title="PostgreSQL Data Visualizer")

@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import sqlalchemy as sa
    import plotly.express as px
    import altair as alt
    return alt, mo, pd, px, sa

@app.cell
def __(mo):
    mo.md(
        r"""
        # 📊 PostgreSQL Data Visualizer Template
        Welcome to your preconfigured Marimo visualization dashboard. This notebook is designed to query and visualize data from your homelab PostgreSQL database.
        
        ### 🔌 Database Connection Configuration
        Enter your PostgreSQL connection parameters below to connect via the host gateway (`host.docker.internal`).
        """
    )
    return

@app.cell
def __(mo):
    # Form UI elements for credentials input
    username_input = mo.ui.text(value="postgres", label="Username")
    password_input = mo.ui.text(value="", label="Password", kind="password")
    db_name_input = mo.ui.text(value="postgres", label="Database Name")
    
    mo.vstack([
        mo.md("#### Database Credentials"),
        username_input,
        password_input,
        db_name_input
    ])
    return db_name_input, password_input, username_input

@app.cell
def __(db_name_input, mo, password_input, sa, username_input):
    # Initialize SQLAlchemy connection engine reactively
    db_url = f"postgresql://{username_input.value}:{password_input.value}@host.docker.internal:5432/{db_name_input.value}"
    
    connection_status = mo.md("⚠️ Input your database password to connect.")
    engine = None
    
    if password_input.value:
        try:
            engine = sa.create_engine(db_url)
            # Simple connection test query
            with engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
            connection_status = mo.md("✅ **Successfully connected to PostgreSQL at host.docker.internal:5432!**")
        except Exception as e:
            connection_status = mo.md(f"❌ **Failed to connect:** `{str(e)}` ")
            engine = None
            
    connection_status
    return connection_status, db_url, engine

@app.cell
def __(engine, mo, pd):
    # UI input for running custom queries
    query_text = mo.ui.text_area(
        value="SELECT NOW() as current_time;", 
        label="SQL Query",
        placeholder="Enter your visualization query here..."
    )
    
    run_button = mo.ui.button(label="Execute Query", value=False)
    
    mo.vstack([
        mo.md("### 🔍 SQL Query Panel"),
        query_text,
        run_button
    ])
    return run_button, query_text

@app.cell
def __(engine, mo, pd, query_text, run_button):
    # Execute query and hold data reactively
    query_results = None
    query_status = mo.md("*Query has not been executed yet.*")
    
    if run_button.value and engine is not None:
        try:
            df = pd.read_sql(query_text.value, engine)
            query_results = df
            query_status = mo.md(f"🎉 **Query returned {len(df)} rows.**")
        except Exception as e:
            query_status = mo.md(f"🚨 **Query Error:** `{str(e)}` ")
    elif engine is None:
        query_status = mo.md("⚠️ *Please establish a working database connection first.*")
        
    mo.vstack([
        query_status,
        mo.ui.table(query_results) if query_results is not None else mo.empty()
    ])
    return query_results, query_status

@app.cell
def __(mo, px, query_results):
    # Interactive charting panel using Plotly (runs whenever query_results updates!)
    chart_output = mo.empty()
    
    if query_results is not None and not query_results.empty:
        # Check if there are at least two columns to plot
        cols = list(query_results.columns)
        if len(cols) >= 2:
            x_col = mo.ui.dropdown(options=cols, value=cols[0], label="X-Axis")
            y_col = mo.ui.dropdown(options=cols, value=cols[1], label="Y-Axis")
            chart_type = mo.ui.dropdown(options=["Bar", "Line", "Scatter"], value="Bar", label="Chart Type")
            
            # Interactive visualization controls
            chart_controls = mo.hstack([x_col, y_col, chart_type])
            
            # Reactively plot
            fig = None
            if chart_type.value == "Bar":
                fig = px.bar(query_results, x=x_col.value, y=y_col.value, title=f"{y_col.value} by {x_col.value}")
            elif chart_type.value == "Line":
                fig = px.line(query_results, x=x_col.value, y=y_col.value, title=f"{y_col.value} over {x_col.value}")
            else:
                fig = px.scatter(query_results, x=x_col.value, y=y_col.value, title=f"{x_col.value} vs {y_col.value}")
                
            chart_output = mo.vstack([
                mo.md("### 📊 Interactive Visualization"),
                chart_controls,
                mo.as_html(fig)
            ])
        else:
            chart_output = mo.md("ℹ️ *Your query needs at least 2 columns to generate a plot.*")
            
    chart_output
    return chart_output,

if __name__ == "__main__":
    app.run()
