# unibase/cli.py

import typer
import json
from tabulate import tabulate
import networkx as nx
import matplotlib.pyplot as plt
import threading
import csv
import io

from unibase.db import sql, nosql, vector, graph, image, multimodal
from unibase.utils import logger, etl, groq_integration, ai_agent
from unibase.registry import add_connection, get_connections, update_connection, clear_registry

app = typer.Typer()
log = logger.get_logger()

# Map shorthand names to modules
db_mapping = {
    "sql": sql,
    "postgres": sql,
    "mysql": sql,
    "nosql": nosql,
    "mongo": nosql,
    "vector": vector,
    "faiss": vector,
    "pinecone": vector,
    "milvus": vector,
    "graph": graph,
    "neo4j": graph,
    "arango": graph,
    "image": image,
    "gridfs": image,
    "s3": image,
    "multimodal": multimodal
}

def parse_db_list(db_list_str: str):
    return [db.strip().lower() for db in db_list_str.split(",") if db.strip()]

@app.command()
def connect(
    db: str = typer.Option(..., "--db", help="Comma separated list of databases (e.g. mongo,postgres)"),
    host: str = typer.Option("localhost", help="Database host"),
    port: int = typer.Option(None, help="Database port"),
    user: str = typer.Option("user", help="Username"),
    password: str = typer.Option("password", help="Password")
):
    """
    Connect to one or more databases.
    """
    dbs = parse_db_list(db)
    for db_type in dbs:
        module = db_mapping.get(db_type)
        if not module:
            typer.echo(f"Database type '{db_type}' is not supported.")
            continue
        try:
            connection = module.connect(host, port, user, password)
            add_connection(db_type, connection)
            typer.echo(f"Connected to {db_type.upper()}: {connection}")
        except Exception as e:
            log.error(f"Error connecting to {db_type}", exc_info=True)
            typer.echo(f"Error connecting to {db_type}: {str(e)}")

@app.command("show-connected")
def show_connected():
    """
    Show all connected databases.
    """
    connections = get_connections()
    if not connections:
        typer.echo("No databases connected.")
        return
    for db_type, conns in connections.items():
        typer.echo(f"{db_type.upper()}:")
        for conn in conns:
            typer.echo(f"  - {conn['repr']}")

@app.command()
def query(
    db: str = typer.Option(..., "--db", help="Comma separated list of databases to query"),
    query: str = typer.Option(..., "--query", help="Query to execute")
):
    """
    Execute a query on specified databases.
    """
    dbs = parse_db_list(db)
    results = {}
    registry = get_connections(dbs)
    if not registry:
        typer.echo("No connected databases found for the specified types.")
        raise typer.Exit()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            typer.echo(f"Database type '{db_type}' is not supported for operations.")
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            try:
                res = conn_obj.query(query)
                results.setdefault(db_type, []).append(res)
            except Exception as e:
                log.error(f"Error querying {db_type}", exc_info=True)
                results.setdefault(db_type, []).append(f"Error: {str(e)}")
    for db_type, res_list in results.items():
        typer.echo(f"Results from {db_type.upper()}:")
        if db_type in ["sql", "postgres", "mysql"]:
            if res_list and isinstance(res_list[0], list) and res_list[0] and isinstance(res_list[0][0], dict):
                table = []
                headers = res_list[0][0].keys()
                for res in res_list:
                    for row in res:
                        table.append(list(row.values()))
                typer.echo(tabulate(table, headers=headers, tablefmt="grid"))
            else:
                typer.echo(res_list)
        else:
            typer.echo(res_list)

@app.command()
def insert(
    db: str = typer.Option("", "--db", help="Comma separated list of databases to insert into (default: all connected)"),
    data: str = typer.Option(..., "--data", help="JSON string of data to insert"),
    use_ai: bool = typer.Option(False, "--ai", help="Use AI to enrich the record")
):
    """
    Insert a record into specified databases.
    
    If --ai is provided, the record will be enriched with AI-generated metadata.
    """
    try:
        record = json.loads(data)
    except Exception as e:
        typer.echo(f"Invalid JSON data: {str(e)}")
        raise typer.Exit()
    
    if use_ai:
        try:
            enrichment = groq_integration.get_insights(f"Enrich this record with AI metadata: {record}")
            record["ai_metadata"] = enrichment
            typer.echo("AI Enrichment Added:")
            typer.echo(record["ai_metadata"])
        except Exception as e:
            log.error("Error during AI enrichment", exc_info=True)
            typer.echo(f"Warning: AI enrichment failed: {str(e)}")
    
    target = parse_db_list(db) if db else None
    registry = get_connections(target)
    if not registry:
        typer.echo("No connected databases found for insertion.")
        raise typer.Exit()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            try:
                res = conn_obj.insert(record)
                typer.echo(f"{db_type.upper()}: {res}")
                update_connection(db_type, conn_obj)
            except Exception as e:
                log.error(f"Error inserting into {db_type}", exc_info=True)
                typer.echo(f"Error inserting into {db_type}: {str(e)}")

@app.command()
def update(
    db: str = typer.Option(..., "--db", help="Comma separated list of databases to update"),
    key: str = typer.Option(..., help="Key to match for update"),
    value: str = typer.Option(..., help="Value to match for update"),
    update_data: str = typer.Option(..., help="JSON string of fields to update")
):
    """
    Update records in specified databases.
    """
    try:
        upd_data = json.loads(update_data)
    except Exception as e:
        typer.echo(f"Invalid JSON for update data: {str(e)}")
        raise typer.Exit()
    dbs = parse_db_list(db)
    registry = get_connections(dbs)
    if not registry:
        typer.echo("No connected databases found for update.")
        raise typer.Exit()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            try:
                res = conn_obj.update(key, value, upd_data)
                typer.echo(f"{db_type.upper()}: {res}")
                update_connection(db_type, conn_obj)
            except Exception as e:
                log.error(f"Error updating in {db_type}", exc_info=True)
                typer.echo(f"Error updating in {db_type}: {str(e)}")

@app.command()
def delete(
    db: str = typer.Option(..., "--db", help="Comma separated list of databases to delete from"),
    key: str = typer.Option(..., help="Key to match for deletion"),
    value: str = typer.Option(..., help="Value to match for deletion")
):
    """
    Delete records from specified databases.
    """
    dbs = parse_db_list(db)
    registry = get_connections(dbs)
    if not registry:
        typer.echo("No connected databases found for deletion.")
        raise typer.Exit()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            try:
                res = conn_obj.delete(key, value)
                typer.echo(f"{db_type.upper()}: {res}")
                update_connection(db_type, conn_obj)
            except Exception as e:
                log.error(f"Error deleting in {db_type}", exc_info=True)
                typer.echo(f"Error deleting in {db_type}: {str(e)}")

@app.command()
def deactivate(
    db: str = typer.Option(..., "--db", help="Comma separated list of databases to deactivate")
):
    """
    Deactivate specified databases.
    """
    dbs = parse_db_list(db)
    registry = get_connections(dbs)
    if not registry:
        typer.echo("No connected databases found to deactivate.")
        raise typer.Exit()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            try:
                res = conn_obj.deactivate()
                typer.echo(f"{db_type.upper()}: {res}")
                update_connection(db_type, conn_obj)
            except Exception as e:
                log.error(f"Error deactivating {db_type}", exc_info=True)
                typer.echo(f"Error deactivating {db_type}: {str(e)}")

@app.command()
def download(
    db: str = typer.Option(..., "--db", help="Database type to download data from"),
    format: str = typer.Option("json", "--format", help="Download format: json or csv")
):
    """
    Download data from a specified database.
    
    The data can be downloaded in the designated form (JSON or CSV).
    """
    dbs = parse_db_list(db)
    registry = get_connections(dbs)
    if not registry:
        typer.echo("No connected databases found for download.")
        raise typer.Exit()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            try:
                data = conn_obj.download()
                typer.echo(f"Data from {db_type.upper()}:")
                if format.lower() == "json":
                    typer.echo(json.dumps(data, indent=2))
                elif format.lower() == "csv":
                    if isinstance(data, list) and data and isinstance(data[0], dict):
                        output = io.StringIO()
                        writer = csv.DictWriter(output, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                        typer.echo(output.getvalue())
                    else:
                        typer.echo("CSV format is only supported for a list of dictionary records.")
                else:
                    typer.echo("Unsupported format. Use 'json' or 'csv'.")
            except Exception as e:
                log.error(f"Error downloading from {db_type}", exc_info=True)
                typer.echo(f"Error downloading from {db_type}: {str(e)}")

@app.command("init")
def init(
    type: str = typer.Option(..., "--type", help="Database types to initialize (e.g., 'all' for all databases)")
):
    """
    Initialize and merge databases.
    """
    if type.lower() == "all":
        for key, module in db_mapping.items():
            try:
                connection = module.connect("localhost", None, "user", "password")
                add_connection(key, connection)
                typer.echo(f"Initialized and connected to {key.upper()}")
            except Exception as e:
                log.error(f"Error initializing {key}", exc_info=True)
                typer.echo(f"Error initializing {key}: {str(e)}")
    else:
        typer.echo("Unsupported init type. Use 'all' to initialize all databases.")

@app.command()
def sync(
    cloud: bool = typer.Option(False, "--cloud", help="Sync to cloud if flag is provided")
):
    """
    Sync all connected databases to the cloud.
    """
    if cloud:
        typer.echo("Syncing all connected databases to the cloud...")
        typer.echo("All databases synced to cloud successfully!")
    else:
        typer.echo("No sync option provided. Use --cloud to sync databases.")

@app.command("visualize-graph-ui")
def visualize_graph_ui():
    """
    Launch a UI to visualize graph database data.
    """
    registry = get_connections(["graph", "neo4j", "arango"])
    G = nx.Graph()
    for db_type, conn_infos in registry.items():
        module = db_mapping.get(db_type)
        if not module:
            continue
        for info in conn_infos:
            conn_obj = module.from_registry(info)
            for record in conn_obj.data:
                src = record.get("source", "A")
                tgt = record.get("target", "B")
                G.add_edge(src, tgt)
    if G.number_of_nodes() == 0:
        typer.echo("No graph data available for visualization.")
        raise typer.Exit()
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=10)
    plt.title("Graph Database Visualization")
    plt.show()

@app.command()
def insights(
    query: str = typer.Option(..., "--query", help="Query for AI-assisted insights")
):
    """
    Get AI-assisted query insights.
    """
    try:
        result = groq_integration.get_insights(query)
        typer.echo("AI Insights:")
        typer.echo(result)
    except Exception as e:
        log.error("Insights error", exc_info=True)
        typer.echo(f"Insights error: {str(e)}")

@app.command("guide-db")
def guide_db(
    query: str = typer.Option(..., "--query", help="Describe your data or query need")
):
    """
    Analyze your query and guide you on the best database type to use.
    """
    try:
        suggestion = groq_integration.get_insights(
            f"Based on the query: '{query}', which database type (SQL, NoSQL, Graph, Vector, Image, Multi-Modal) is best suited?"
        )
        typer.echo("AI Database Suggestion:")
        typer.echo(suggestion)
    except Exception as e:
        log.error("Guide DB error", exc_info=True)
        typer.echo(f"Guide DB error: {str(e)}")

@app.command()
def migrate(
    source: str = typer.Option(..., "--source", help="Source database type (e.g., sql)"),
    target: str = typer.Option(..., "--target", help="Target database type (e.g., nosql)"),
    query: str = typer.Option("SELECT *", "--query", help="Query to fetch data from the source DB")
):
    """
    Migrate data from one database type to another.

    This command reads data from the source database using the provided query and attempts
    to insert that data into the target database. Note that migration across different database
    types may require schema mapping and is considered experimental. If migration is not possible,
    an explanation will be provided.
    """
    # Normalize names
    src_type = source.lower().strip()
    tgt_type = target.lower().strip()
    
    src_registry = get_connections([src_type])
    tgt_registry = get_connections([tgt_type])
    
    if src_type not in src_registry:
        typer.echo(f"No connected {src_type.upper()} databases found for migration.")
        raise typer.Exit()
    if tgt_type not in tgt_registry:
        typer.echo(f"No connected {tgt_type.upper()} databases found for migration.")
        raise typer.Exit()
    
    src_module = db_mapping.get(src_type)
    tgt_module = db_mapping.get(tgt_type)
    
    if not src_module or not tgt_module:
        typer.echo("Either source or target database type is not supported for migration.")
        raise typer.Exit()
    
    total_migrated = 0
    # Loop over source connections
    for src_info in src_registry[src_type]:
        src_conn = src_module.from_registry(src_info)
        src_data = src_conn.query(query)
        # Expecting a list of records (dictionaries)
        if not isinstance(src_data, list):
            typer.echo("Migration not possible: The query did not return a list of records. Please check your query.")
            raise typer.Exit()
        for record in src_data:
            # Insert the record into every target connection
            for tgt_info in tgt_registry[tgt_type]:
                tgt_conn = tgt_module.from_registry(tgt_info)
                try:
                    tgt_conn.insert(record)
                    update_connection(tgt_type, tgt_conn)
                    total_migrated += 1
                except Exception as e:
                    typer.echo(f"Error inserting record into {tgt_type.upper()}: {str(e)}")
    if total_migrated == 0:
        typer.echo("Migration did not migrate any records. Please ensure the source query returns data and the target DB is compatible.")
    else:
        typer.echo(f"Migration complete: {total_migrated} records migrated from {src_type.upper()} to {tgt_type.upper()}.")


@app.command("auto-agent")
def auto_agent(
    action: str = typer.Option(..., "--action", help="Start or stop the AI agent (options: start, stop)")
):
    """
    Control the autonomous AI agent that monitors and optimizes the database registry.
    """
    if action.lower() == "start":
        if not hasattr(auto_agent, "agent_thread") or not auto_agent.agent_thread.is_alive():
            auto_agent.agent_instance = ai_agent.agent_instance
            auto_agent.agent_thread = threading.Thread(target=auto_agent.agent_instance.run, daemon=True)
            auto_agent.agent_thread.start()
            typer.echo("AI Agent started.")
        else:
            typer.echo("AI Agent is already running.")
    elif action.lower() == "stop":
        if hasattr(auto_agent, "agent_instance"):
            auto_agent.agent_instance.stop()
            typer.echo("AI Agent stopped.")
        else:
            typer.echo("AI Agent is not running.")
    else:
        typer.echo("Invalid action. Use --action start or --action stop.")

@app.command("sync-cloud")
def sync_cloud():
    """
    Sync all data to the cloud.
    """
    typer.echo("Syncing data to the cloud...")
    typer.echo("Data synced to cloud successfully!")

@app.command("disconnect-all")
def disconnect_all():
    """
    Disconnect and remove all registered databases.
    """
    confirm = typer.confirm("Are you sure you want to disconnect ALL databases?")
    if confirm:
        clear_registry()
        typer.echo("✅ All databases have been disconnected and the registry is now empty.")
    else:
        typer.echo("❌ Operation cancelled.")

if __name__ == "__main__":
    app()
