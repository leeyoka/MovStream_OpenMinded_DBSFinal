import pandas as pd
from pymongo import MongoClient
from neo4j import GraphDatabase

print("Memulai proses ETL untuk 8.800+ data (Bisa memakan waktu beberapa detik)...")

# 1. Load Keseluruhan Data dari CSV
try:
    # Menggunakan file asli Kaggle
    df = pd.read_csv('scripts/netflix_titles.csv')
    df = df.fillna('') # Bersihkan nilai NaN
    print(f"Berhasil membaca {len(df)} baris data dari CSV.")
except FileNotFoundError:
    print("Error: File scripts/netflix_titles.csv tidak ditemukan! Pastikan file sudah di-download.")
    exit()

# 2. Masukkan ke MongoDB (Primary Catalog)
try:
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['movstream_db']
    
    db.movies.drop() # Reset koleksi
    
    # MongoDB sangat cepat untuk bulk insert, 8000+ data akan masuk dalam hitungan milidetik
    db.movies.insert_many(df.to_dict('records'))
    print("✅ Seluruh data film berhasil masuk ke MongoDB!")
except Exception as e:
    print("❌ Gagal memasukkan data ke MongoDB:", e)

# 3. Masukkan ke Neo4j (Recommendation Engine)
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password123"))

# Fungsi-fungsi Batch untuk menghindari performa lambat di Neo4j
def create_movies_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    MERGE (m:Movie {id: row.show_id, title: row.title})
    """
    tx.run(query, batch=batch)

def create_actors_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    WITH row WHERE row.cast IS NOT NULL AND row.cast <> ''
    UNWIND split(row.cast, ',') AS actorName
    WITH row, trim(actorName) AS cleanActorName
    MATCH (m:Movie {id: row.show_id})
    MERGE (a:Actor {name: cleanActorName})
    MERGE (a)-[:ACTED_IN]->(m)
    """
    tx.run(query, batch=batch)

def create_genres_batch(tx, batch):
    query = """
    UNWIND $batch AS row
    WITH row WHERE row.listed_in IS NOT NULL AND row.listed_in <> ''
    UNWIND split(row.listed_in, ',') AS genreName
    WITH row, trim(genreName) AS cleanGenreName
    MATCH (m:Movie {id: row.show_id})
    MERGE (g:Genre {name: cleanGenreName})
    MERGE (m)-[:IN_GENRE]->(g)
    """
    tx.run(query, batch=batch)

try:
    with driver.session() as session:
        # Hapus data lama (Reset Node dan Relationship)
        print("Mereset database Neo4j...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # Ubah dataframe menjadi list of dictionaries
        records = df.to_dict('records')
        
        # Eksekusi secara bertahap agar tidak terjadi Cartesian Product dan memory leak
        print("Memasukkan Node Film ke Neo4j...")
        session.execute_write(create_movies_batch, records)
        
        print("Memasukkan Node Aktor & Relasi (ACTED_IN) ke Neo4j...")
        session.execute_write(create_actors_batch, records)
        
        print("Memasukkan Node Genre & Relasi (IN_GENRE) ke Neo4j...")
        session.execute_write(create_genres_batch, records)
            
    print("✅ Seluruh Graph Nodes & Relationships berhasil dibangun di Neo4j!")
except Exception as e:
    print("❌ Gagal memproses data di Neo4j:", e)
finally:
    driver.close()

print("🎉 Proses ETL Selesai secara menyeluruh!")