import matplotlib.pyplot as plt
import numpy as np

categories = ['Movie Lookup', 'Watch History', 'Friend Recs', 'Shortest Path']
mongodb_latency = [3, 5, 187, 0]  
neo4j_latency = [9, 18, 14, 11]

x = np.arange(len(categories)) 
width = 0.35  


fig, ax = plt.subplots(figsize=(10, 6))


rects1 = ax.bar(x - width/2, mongodb_latency, width, label='MongoDB', color='#ffeacc', edgecolor='#b3a28d')
rects2 = ax.bar(x + width/2, neo4j_latency, width, label='Neo4j', color='#f7b779', edgecolor='#c48746')


ax.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
ax.set_title('Query Latency: MongoDB vs Neo4j (ms, lower is better)', fontsize=14, pad=15)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=11)
ax.legend(fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.5) 
def autolabel(rects, is_mongodb=False):
    for rect in rects:
        height = rect.get_height()
        if height > 0:
            ax.annotate(f'{height} ms',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
        elif is_mongodb and height == 0:
            ax.annotate('Not Supported',
                        xy=(rect.get_x() + rect.get_width() / 2, 0),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color='#d9534f', fontsize=9, fontweight='bold', style='italic')

autolabel(rects1, is_mongodb=True)
autolabel(rects2)

fig.tight_layout()

output_filename = 'detailed_latency_comparison.png'
plt.savefig(output_filename, dpi=300)
print(f"✅ Grafik baru berhasil dibuat dengan nama file: '{output_filename}'")