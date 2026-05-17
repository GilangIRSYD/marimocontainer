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
        mo.ui.table(query_results) if query_results is not None else None
    ])
    return query_results, query_status

@app.cell
def __(mo, px, query_results):
    # Interactive charting panel using Plotly (runs whenever query_results updates!)
    chart_output = None
    
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
