const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');

// Schema MongoDB sederhana (Flexible) [cite: 76]
const Movie = mongoose.model('Movie', new mongoose.Schema({}, { strict: false }), 'movies');

// A. Endpoint: Browse/Search (Source: MongoDB) [cite: 57, 58]
router.get('/movies', async (req, res) => {
    try {
        const movies = await Movie.find().limit(20); // Ambil 20 data untuk contoh
        res.json(movies);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// B. Endpoint: Get Recommendation (Source: Neo4j) [cite: 63, 64]
router.get('/recommend/:userId', async (req, res) => {
    const driver = req.app.locals.neo4jDriver;
    const session = driver.session();
    try {
        const userId = req.params.userId;
        // Cypher query untuk mencari rekomendasi berdasarkan genre/aktor [cite: 64, 88]
        const result = await session.run(
            `MATCH (u:User {id: $userId})-[:WATCHED]->(m:Movie)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Movie)
             WHERE NOT (u)-[:WATCHED]->(rec)
             RETURN rec.title AS title, rec.id AS id LIMIT 10`,
            { userId: userId }
        );
        const recommendations = result.records.map(record => ({
            id: record.get('id'),
            title: record.get('title')
        }));
        res.json(recommendations);
    } catch (err) {
        res.status(500).json({ error: err.message });
    } finally {
        await session.close();
    }
});

// C. Endpoint: Watch Movie (Sync ke MongoDB & Neo4j) [cite: 68, 69, 71]
router.post('/watch', async (req, res) => {
    const { userId, movieId } = req.body;
    const driver = req.app.locals.neo4jDriver;
    const session = driver.session();
    try {
        // 1. Simpan riwayat di MongoDB (Logic aplikasi kalian) [cite: 69]
        // ... kode simpan ke koleksi 'users' ...

        // 2. Update relationship di Neo4j [cite: 71, 87]
        await session.run(
            `MATCH (u:User {id: $userId}), (m:Movie {id: $movieId})
             MERGE (u)-[:WATCHED]->(m)`,
            { userId, movieId }
        );
        res.json({ message: "Movie watched and synced to both DBs!" });
    } catch (err) {
        res.status(500).json({ error: err.message });
    } finally {
        await session.close();
    }
});

module.exports = router;