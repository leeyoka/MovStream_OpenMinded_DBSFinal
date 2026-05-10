import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = 'raw_results.csv'

if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' tidak ditemukan!")
    exit()

df = pd.read_csv(file_path)

# Filter hanya untuk metric durasi request
df_duration = df[df['metric_name'] == 'http_req_duration'].copy()

# FUNGSI PENCARIAN LABEL YANG LEBIH KUAT
def get_db_label(row):
    # Cek di kolom 'extra_tags', 'url', atau 'name'
    text_to_search = f"{row.get('extra_tags', '')} {row.get('url', '')} {row.get('name', '')}"
    if 'MongoDB' in text_to_search or 'mongo' in text_to_search.lower():
        return 'MongoDB'
    if 'Neo4j' in text_to_search or 'neo4j' in text_to_search.lower():
        return 'Neo4j'
    return 'Other'

df_duration['database'] = df_duration.apply(get_db_label, axis=1)

# --- DEBUG: Cetak jumlah data yang ditemukan ke terminal ---
count_mongo = len(df_duration[df_duration['database'] == 'MongoDB'])
count_neo = len(df_duration[df_duration['database'] == 'Neo4j'])
print(f"Data ditemukan -> MongoDB: {count_mongo} baris, Neo4j: {count_neo} baris")

if count_mongo == 0 and count_neo == 0:
    print("!!! PERINGATAN: Tidak ada data MongoDB/Neo4j yang terdeteksi.")
    print("Coba jalankan ulang K6-nya dulu ya.")
    exit()

# Hitung rata-rata latency
avg_latency = df_duration.groupby('database')['metric_value'].mean()
avg_latency = avg_latency.reindex(['MongoDB', 'Neo4j']).fillna(0)

# --- Gambar Grafik ---
plt.figure(figsize=(9, 6))
colors = ['#47A248', '#018BFF']
bars = plt.bar(avg_latency.index, avg_latency.values, color=colors)

plt.title('Hasil Uji Kecepatan: MongoDB vs Neo4j', fontsize=14, fontweight='bold')
plt.ylabel('Rata-rata Waktu Respon (ms)', fontweight='bold')
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + (yval*0.01), f'{yval:.2f} ms', 
             ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.savefig('latency_plot.png')
print("Selesai! Sekarang cek lagi 'latency_plot.png'.")