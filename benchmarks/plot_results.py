import pandas as pd
import matplotlib.pyplot as plt

print("Menjana graf kependaman (latency plot)...")

try:
    # Muat data CSV
    df = pd.read_csv('benchmarks/raw_results.csv')

    # Tetapkan saiz rajah
    plt.figure(figsize=(10, 6))

    # Plot garisan untuk MongoDB dan Neo4j
    plt.plot(df['users'], df['mongodb_latency_ms'], marker='o', linestyle='-', color='green', label='MongoDB (Katalog Utama)')
    plt.plot(df['users'], df['neo4j_latency_ms'], marker='s', linestyle='--', color='blue', label='Neo4j (Enjin Pengesyoran)')

    # Label dan tajuk
    plt.title('Analisis Kependaman: MongoDB lwn Neo4j (Ujian Beban K6)')
    plt.xlabel('Bilangan Pengguna Serentak')
    plt.ylabel('Masa Respons / Kependaman (ms)')
    plt.legend()
    plt.grid(True)

    # Simpan graf sebagai imej
    output_file = 'benchmarks/latency_plot.png'
    plt.savefig(output_file)
    print(f"Graf berjaya dijana dan disimpan sebagai '{output_file}'!")
    
    # Tunjukkan graf di skrin
    plt.show()

except FileNotFoundError:
    print("Ralat: Fail 'benchmarks/raw_results.csv' tidak dijumpai.")