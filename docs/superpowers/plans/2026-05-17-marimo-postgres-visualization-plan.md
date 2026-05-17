# Marimo PostgreSQL Visualization Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a custom Docker-based Marimo visualization service that connects to a PostgreSQL database on the homelab host, pre-installs data science/visualization packages, implements secure token login, and mounts persistent storage.

**Architecture:** Extend Marimo's official `latest-sql` Docker image, layer requested database and visualization dependencies, and coordinate local host network gateway mapping (`host.docker.internal`) via Docker Compose. Use a git-ignored environment file (`stack.env`) to dynamically configure port mapping and the login token password.

**Tech Stack:** Docker, Docker Compose, Marimo, Python, SQLAlchemy, SQLModel, Pandas, Polars, Plotly, Altair, Seaborn, psycopg2-binary, asyncpg.

---

## File Structure Map
Before executing, this plan expects the creation and configuration of these files:
1. `docs/superpowers/plans/2026-05-17-marimo-postgres-visualization-plan.md` (This Plan)
2. `.gitignore` (Modified to ignore `stack.env`)
3. `stack.env.example` (Created, containing example configuration variables)
4. `stack.env` (Created, containing local secrets for deployment)
5. `requirements.txt` (Created, defining database and data science libraries)
6. `Dockerfile` (Created, extending `latest-sql` base and installing dependencies)
7. `docker-compose.yml` (Created, configuring ports, network gateway mapping, env file, and commands)
8. `notebooks/postgres_visualization.py` (Created, templated Python notebook showing Postgres connecting and interactive Plotly visualization)

---

## Tasks

### Task 1: Project Setup and Ignored Credentials

**Files:**
- Modify: `/Users/gilangsafera/Documents/gilang/code/notebook/.gitignore`
- Create: `/Users/gilangsafera/Documents/gilang/code/notebook/stack.env.example`
- Create: `/Users/gilangsafera/Documents/gilang/code/notebook/stack.env`

- [ ] **Step 1: Update `.gitignore`**
  Modify `.gitignore` to ignore the live `stack.env` file to prevent committing local passwords and ports to GitHub.
  
  Replace the contents of `/Users/gilangsafera/Documents/gilang/code/notebook/.gitignore` with:
  ```
  .agents/*
  stack.env
  ```

- [ ] **Step 2: Create `stack.env.example`**
  Write the sample env configuration file to `/Users/gilangsafera/Documents/gilang/code/notebook/stack.env.example`:
  ```env
  # Marimo Server Port Mapping on Host
  MARIMO_PORT=2718
  
  # Secure Token for Accessing Marimo Editor
  MARIMO_TOKEN_PASSWORD=replace_with_your_secure_password
  ```

- [ ] **Step 3: Create local development `stack.env`**
  Write the actual live local configuration to `/Users/gilangsafera/Documents/gilang/code/notebook/stack.env`:
  ```env
  # Marimo Server Port Mapping on Host
  MARIMO_PORT=2718
  
  # Secure Token for Accessing Marimo Editor
  MARIMO_TOKEN_PASSWORD=postgresvis123!
  ```

- [ ] **Step 4: Verify git ignore configuration**
  Run: `git status --ignored`
  Expected Output: Verify that `.gitignore` is modified, `stack.env.example` is untracked, and `stack.env` is correctly marked as **ignored** (under the "Ignored files:" section).

- [ ] **Step 5: Commit changes**
  ```bash
  git add .gitignore stack.env.example
  git commit -m "feat: configure gitignore and env templates"
  ```

---

### Task 2: Service Dependency Specification

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/notebook/requirements.txt`

- [ ] **Step 1: Create `requirements.txt`**
  Write the full set of database and plotting libraries to `/Users/gilangsafera/Documents/gilang/code/notebook/requirements.txt`:
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

- [ ] **Step 2: Verify file existence and contents**
  Run: `cat /Users/gilangsafera/Documents/gilang/code/notebook/requirements.txt`
  Expected Output: Display the list of requirements successfully.

- [ ] **Step 3: Commit changes**
  ```bash
  git add requirements.txt
  git commit -m "feat: add python requirements file"
  ```

---

### Task 3: Container Definition (`Dockerfile`)

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/notebook/Dockerfile`

- [ ] **Step 1: Create `Dockerfile`**
  Write the image recipe extending Marimo's base to `/Users/gilangsafera/Documents/gilang/code/notebook/Dockerfile`:
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

- [ ] **Step 2: Validate Dockerfile syntax**
  Check the formatting and existance of the file.
  Run: `cat /Users/gilangsafera/Documents/gilang/code/notebook/Dockerfile`
  Expected Output: Shows the file contents correctly.

- [ ] **Step 3: Commit changes**
  ```bash
  git add Dockerfile
  git commit -m "feat: create Dockerfile extending latest-sql image"
  ```

---

### Task 4: Orchestration Configuration (`docker-compose.yml`)

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/notebook/docker-compose.yml`

- [ ] **Step 1: Create `docker-compose.yml`**
  Write the compose file mapping variables, volume, host-gateway and start command to `/Users/gilangsafera/Documents/gilang/code/notebook/docker-compose.yml`:
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

- [ ] **Step 2: Validate docker-compose config syntax**
  Verify the correctness of the environment variable loading and docker-compose schema using the dry-run CLI:
  Run: `docker compose config`
  Expected Output: Shows compiled compose configuration with env variables populated without errors. (Note: Since docker daemon may not be running locally or docker compose isn't installed globally on some test runners, if this command fails due to 'command not found', verify syntax manually).

- [ ] **Step 3: Commit changes**
  ```bash
  git add docker-compose.yml
  git commit -m "feat: add docker-compose orchestration file"
  ```

---

### Task 5: Visualization Template Notebook

**Files:**
- Create: `/Users/gilangsafera/Documents/gilang/code/notebook/notebooks/postgres_visualization.py`

- [ ] **Step 1: Create notebooks directory**
  Create the folder to house notebooks.
  Run: `mkdir -p /Users/gilangsafera/Documents/gilang/code/notebook/notebooks`

- [ ] **Step 2: Create `postgres_visualization.py` template**
  Write the complete, loadable Marimo Python notebook showing reactive connections to PostgreSQL and interactive plotting with Plotly:
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
  ```

- [ ] **Step 3: Commit changes**
  ```bash
  git add notebooks/postgres_visualization.py
  git commit -m "feat: add template visualization notebook"
  ```

---

### Task 6: Final Verification

**Files:**
- Create: N/A

- [ ] **Step 1: Check full workspace file list**
  Verify all files are exactly where they should be in the repository.
  Run: `find . -maxdepth 2 -not -path '*/.*'`
  Expected Output:
  ```
  .
  ./Dockerfile
  ./docker-compose.yml
  ./requirements.txt
  ./stack.env
  ./stack.env.example
  ./notebooks
  ./notebooks/postgres_visualization.py
  ./docs
  ./docs/superpowers
  ```

- [ ] **Step 2: Commit verified structure**
  Final check to make sure workspace is clean.
  Run: `git status`
  Expected Output: Working tree clean (except maybe `stack.env` which is ignored).
