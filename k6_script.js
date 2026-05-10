import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 10, // Simulasi 10 user akses barengan
    duration: '10s', // Dijalankan selama 10 detik
};

export default function () {
    // Request 1: Ambil data dari MongoDB
    http.get('http://localhost:3000/movies', { tags: { my_custom_tag: 'MongoDB' } });

    // Request 2: Ambil rekomendasi dari Neo4j
    http.get('http://localhost:3000/recommend/s1', { tags: { my_custom_tag: 'Neo4j' } });

    sleep(1); // Jeda 1 detik tiap user sebelum nge-hit lagi
}