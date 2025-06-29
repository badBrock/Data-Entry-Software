import psycopg2
import uuid
from datetime import date

# --- STEP 1: Set your Supabase database credentials ---
HOST = "Us"
DB_NAME = "postgres"
USER = "https://lzqdcimuvxhhedufnioy.supabase.co"         # Found in Supabase → Settings → Database
PASSWORD = "8c9vp9ljy"     # Same as above
PORT = 5432

# --- STEP 2: Connect to Supabase database ---
conn = psycopg2.connect(
    host=HOST,
    database=DB_NAME,
    user=USER,
    password=PASSWORD,
    port=PORT
)
cur = conn.cursor()

# --- STEP 3: Create the table if it doesn't exist ---
cur.execute("""
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS patients (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    age INTEGER,
    symptoms TEXT,
    visit_date DATE,
    created_at TIMESTAMP DEFAULT now()
);
""")

# --- STEP 4: Insert sample data ---
sample_patient = {
    "name": "John Doe",
    "age": 68,
    "symptoms": "Fatigue, Shortness of breath",
    "visit_date": date.today()
}

cur.execute("""
INSERT INTO patients (id, name, age, symptoms, visit_date)
VALUES (%s, %s, %s, %s, %s);
""", (
    str(uuid.uuid4()),
    sample_patient["name"],
    sample_patient["age"],
    sample_patient["symptoms"],
    sample_patient["visit_date"]
))

# --- STEP 5: Commit and close ---
conn.commit()
cur.close()
conn.close()

print("✅ Table created and data inserted successfully!")
