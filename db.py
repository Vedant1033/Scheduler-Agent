import sqlite3

conn = sqlite3.connect("voicebot.db")
cursor = conn.cursor()

# Create appointments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    time TEXT
)
""")

# Create policies table
cursor.execute("""
CREATE TABLE IF NOT EXISTS policies (
    policy_no TEXT PRIMARY KEY,
    status TEXT
)
""")

# Insert dummy policies
cursor.execute("INSERT OR REPLACE INTO policies VALUES (?, ?)", ("12345", "ACTIVE"))
cursor.execute("INSERT OR REPLACE INTO policies VALUES (?, ?)", ("67890", "EXPIRED"))

conn.commit()
conn.close()

print("✅ Database initialized with dummy data")