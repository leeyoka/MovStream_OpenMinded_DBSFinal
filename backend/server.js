const express = require('express');
const mongoose = require('mongoose');
const neo4j = require('neo4j-driver');

const app = express();
app.use(express.json());

// 1. Koneksi MongoDB
mongoose.connect('mongodb://localhost:27017/movstream_db')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB Connection Error:', err));

// 2. Koneksi Neo4j
const driver = neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('neo4j', 'password123'));

// --- ROUTES ---

// Route: Cek Server Jalan
app.get('/', (req, res) => {
  res.send('API MovStream Berhasil Jalan!');
});

// Route: Ambil Data Film (Dari MongoDB)
app.get('/movies', async (req, res) => {
  try {
    const movies = await mongoose.connection.db.collection('movies').find().limit(20).toArray();
    res.json(movies);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route: Ambil Rekomendasi (Dari Neo4j)
app.get('/recommend/:showId', async (req, res) => {
  const session = driver.session();
  const showId = req.params.showId;
  try {
    // Mencari film dengan genre yang sama (Traversal Depth 1)
    const result = await session.run(
      `MATCH (m:Movie {id: $id})-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Movie)
       RETURN rec.title AS title, g.name AS genre LIMIT 5`,
      { id: showId }
    );
    const recommendations = result.records.map(record => ({
      title: record.get('title'),
      genre: record.get('genre')
    }));
    res.json(recommendations);
  } catch (err) {
    res.status(500).json({ error: err.message });
  } finally {
    await session.close();
  }
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));