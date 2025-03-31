UNIBASE ✨

The Unified AI-Powered Database CLI to manage SQL, NoSQL, Graph, Vector, Image, and Multi-modal Databases in one place.

🚀 Features

✨ Unified CLI for all major DB types: SQL, NoSQL, Vector, Graph, Image, Multi-modal

🧠 AI-Powered Query Guidance & Optimizations (GROQ + Llama)

📂 Migrate data between different DB types (e.g., SQL → NoSQL)

📤 Insert, query, update, delete, deactivate, and download data

🔄 Multi-database querying & auto schema detection

🌍 Graph visualization using NetworkX

⚡ Auto-Connect All DBs with init --type all

🛡️ Secure with API key support, extensible & pluggable

⚙️ Installation

pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple \
            unibase

🔧 CLI Endpoints & Commands

✉ unibase connect

unibase connect --db mongo,postgres --host localhost --user user --password secret

Connects to databases and registers them for unified use.

📲 unibase show-connected

unibase show-connected

Lists all currently connected databases.

➕ unibase insert

unibase insert --data '{"name": "Dhruv", "age": 25}'

Inserts data into all connected databases.

❓ unibase query

unibase query --db sql,nosql --query "SELECT * FROM users"

Runs query across databases and shows results (tabulated for SQL).

✍️ unibase update

unibase update --db sql --key name --value Dhruv --update-data '{"age": 26}'

Updates records based on key/value pair.

🗑 unibase delete

unibase delete --db mongo --key name --value Dhruv

Deletes records from a DB based on key and value.

⏸ unibase deactivate

unibase deactivate --db mysql,vector

Deactivates databases (excluded from future operations).

📄 unibase download

unibase download --db postgres --format json

Downloads data from DB in JSON/CSV format.

⚒️ unibase init

unibase init --type all

Instantly connects to all supported DBs.

📊 unibase visualize-graph-ui

unibase visualize-graph-ui

Displays graph DB data as a visual network using Matplotlib.

🧠 unibase insights

unibase insights --query "How to improve this SQL query for performance?"

Provides AI-driven insights for your query.

🧑‍💻 unibase guide-db

unibase guide-db --query "Store embeddings with captions and run similarity search"

Suggests best DB type based on your use case.

↺ unibase migrate

unibase migrate --source sql --target nosql --query "SELECT * FROM users"

Migrates data between DBs. If migration is unsupported, user is informed.

🌐 unibase sync --cloud

unibase sync --cloud

Syncs local DB state to the cloud (planned/experimental).

❌ unibase disconnect-all

unibase disconnect-all

Clears all database connections from the registry.

🧩 Sample Workflow

# Connect to PostgreSQL and MongoDB
unibase connect --db postgres,mongo --host localhost --user admin --password secret

# Insert record into all DBs
unibase insert --data '{"name": "Riya", "score": 98}'

# Query everything
unibase query --db sql,nosql --query "SELECT * FROM students"

# Migrate data from SQL to NoSQL
unibase migrate --source sql --target nosql --query "SELECT * FROM users"

# Visualize Graph
unibase visualize-graph-ui

🚀 Coming Soon

Cloud-native persistence & backups

Auto-detect schema changes

Natural language querying (LLM-powered)

Web Dashboard UI with real-time stats

🚀 Author

Made with ❤️ by Dhruv DawarMIT License | LinkedIn | GitHub

