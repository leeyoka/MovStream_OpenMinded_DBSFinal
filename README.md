# MovStream — Streaming Platform Backend with Polyglot Persistence

## Overview

MovStream is a streaming platform backend developed as the Final Project for the Database Systems Practicum 2025/2026.

The system manages movies, users, watch history, social graphs, and personalized recommendations using a hybrid NoSQL database architecture. It mirrors how real-world platforms like Netflix and Letterboxd handle massive, interconnected data at scale.

MovStream implements a polyglot persistence strategy: **MongoDB** as the primary document store for catalog and user-generated content, and **Neo4j** as the graph engine for social relationships and recommendation traversal. The backend is built with **FastAPI (Python 3.11)**, exposing a clean REST API with built-in Swagger documentation.

---

## Features

### User Management
- User registration and authentication
- Profile management
- Watchlist management

### Movie Catalog
- Movie browsing with genres, cast, and metadata
- Full-text search support
- Average rating displayed via denormalized field (updated on each review insert)

### Reviews & Watch Logs
- Submit reviews with nested reply threads
- Rate movies
- Track watch history with device and session metadata
- Aggregation pipeline for analytics (top-rated movies, most-watched genres)

### Social Graph
- Follow / unfollow other users
- Friend activity feed (movies watched by people you follow)
- Shortest connection path between users

### Recommendation Engine
- Collaborative filtering via graph traversal (friends-of-friends WATCHED edges)
- Genre affinity scoring based on your social circle's viewing habits

---

## Technology Stack

### Backend
- Python 3.11
- FastAPI (async REST API with auto Swagger docs)
- pymongo 4.x
- neo4j-driver 5.x

### Primary Database
- MongoDB (document store — users, movies, reviews, watch_logs)

### Graph Database
- Neo4j (graph engine — social relationships and recommendations)

### Benchmarking
- k6 (load testing)
- pandas + matplotlib (result visualization)

---

## System Architecture

```text
Client (Postman / Frontend App)
              ↓
        HTTP REST API
              ↓
   FastAPI Backend (Python 3.11)
              ↓
     Service Layer — Business Logic
     + Dual-Write Orchestration
       ↙                   ↘
MongoDB                  Neo4j
(Primary Store)       (Graph Engine)
users · movies        User · Movie · Genre nodes
reviews · watch_logs  FOLLOWS · WATCHED · RATED · IN_GENRE edges
              ↓ (on Neo4j write failure)
         Retry Queue
    (eventual consistency)
```

**Dual-Write Rule:** MongoDB is always written first as the source of truth. Only after MongoDB confirms success does the service layer proceed to write to Neo4j. If the Neo4j write fails, the operation is logged to a retry queue for later replay — MongoDB remains authoritative at all times.

---

## Database Design

### MongoDB Collections

| Collection | Purpose | Key Fields |
|---|---|---|
| `users` | Account and profile data | `_id`, `username`, `email`, `password_hash`, `watchlist[]` |
| `movies` | Film catalog | `_id`, `title`, `release_year`, `genres[]`, `avg_rating`, `review_count` |
| `reviews` | User reviews with embedded replies | `_id`, `user_id`, `movie_id`, `rating`, `text`, `tags[]`, `replies[]` |
| `watch_logs` | Every viewing event | `_id`, `user_id`, `movie_id`, `watched_at`, `duration_watched`, `device` |

### Neo4j Graph Model

**Nodes:**

| Label | Properties | Purpose |
|---|---|---|
| `(:User)` | userId, name, email | Platform user in the social graph |
| `(:Movie)` | movieId, title, year | Film node; minimal properties only |
| `(:Genre)` | name | Genre taxonomy for affinity analysis |

**Relationships:**

| Relationship | Direction | Properties |
|---|---|---|
| `[:FOLLOWS]` | User → User | — |
| `[:WATCHED]` | User → Movie | watchedAt |
| `[:RATED]` | User → Movie | score |
| `[:IN_GENRE]` | Movie → Genre | — |

---

## Project Structure

```bash
MovStream-Project/
│
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # MongoDB + Neo4j connection setup
│   ├── routers/
│   │   ├── users.py
│   │   ├── movies.py
│   │   ├── reviews.py
│   │   ├── watch_logs.py
│   │   └── recommendations.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── movie_service.py
│   │   └── recommendation_service.py
│   └── models/
│       ├── user.py
│       ├── movie.py
│       └── review.py
│
├── benchmarks/
│   ├── k6_script.js             # k6 load test script
│   ├── raw_results.csv          # Raw benchmark output
│   ├── generate_plot.py         # Plot generator (bar chart)
│   ├── plot_results.py          # Alternative plot script
│   └── latency_plot.png         # Generated benchmark chart
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## API Endpoints

### Users
- `POST /users/register` — Register a new user
- `POST /users/login` — User login
- `GET /users/{user_id}` — Get user profile
- `POST /users/{user_id}/follow/{target_id}` — Follow a user

### Movies
- `GET /movies` — Browse movie catalog (MongoDB)
- `GET /movies/{movie_id}` — Get movie detail
- `POST /movies` — Add a movie

### Reviews
- `POST /reviews` — Submit a review (with rating)
- `GET /reviews/{movie_id}` — Get reviews for a movie

### Watch Logs
- `POST /watch` — Log a watch event
- `GET /watch/{user_id}` — Get user watch history

### Recommendations
- `GET /recommend/{user_id}` — Get personalized recommendations (Neo4j)
- `GET /feed/{user_id}` — Get friend activity feed (Neo4j)
- `GET /path/{user_id_a}/{user_id_b}` — Get shortest social connection path (Neo4j)

---

## Installation Guide

### Prerequisites

Make sure the following are installed:
- Python 3.11+
- MongoDB (local or MongoDB Atlas)
- Neo4j Desktop or Neo4j AuraDB
- pip
- k6 *(optional, for running benchmarks)*

---

### 1. Clone the Repository

```bash
git clone https://github.com/leeyoka/MovStream_OpenMinded_DBSFinal.git
cd MovStream_OpenMinded_DBSFinal
```

---

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure `.env`

Create a `.env` file in the root directory:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=movstream

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

SECRET_KEY=your_jwt_secret_key
```

---

### 5. Start Neo4j

- Open **Neo4j Desktop**
- Create or start a local DBMS instance
- Make sure the URI, username, and password match your `.env`

---

### 6. Run the Backend Server

```bash
uvicorn app.main:app --reload --port 3000
```

If successful, you should see:

```text
INFO:     Uvicorn running on http://127.0.0.1:3000
✅ Connected to MongoDB
✅ Connected to Neo4j
```

---

### 7. Access the API Docs

FastAPI provides built-in Swagger documentation:

```
http://localhost:3000/docs
```

---

## Running the Benchmark

The `benchmarks/` folder contains the load test script and result visualization tools used to empirically validate the polyglot design.

### Run the k6 Load Test

> Requires the backend server to be running on `http://localhost:3000`

Install k6: https://k6.io/docs/getting-started/installation/

```bash
cd benchmarks
k6 run k6_script.js --out csv=raw_results.csv
```

The script simulates **10 concurrent virtual users** for **10 seconds**, hitting:
- `GET /movies` — tagged as `MongoDB` (catalog query)
- `GET /recommend/s1` — tagged as `Neo4j` (graph traversal)

---

### Generate the Latency Plot

```bash
cd benchmarks
pip install pandas matplotlib
python generate_plot.py
```

This reads `raw_results.csv` and outputs `latency_plot.png` — a bar chart comparing average response latency between MongoDB and Neo4j endpoints.

---

### Benchmark Results Summary

| Query | MongoDB (ms) | Neo4j (ms) | Winner |
|---|---|---|---|
| Movie lookup by ID | 3 | 9 | MongoDB |
| User watch history | 5 | 18 | MongoDB |
| Top 10 by avg rating | 42 | — | MongoDB |
| Friend recommendations (2 hops) | 187 | 14 | **Neo4j (13×)** |
| Shortest path (3–5 hops) | not supported | 11 | **Neo4j** |

**Key findings:**
- MongoDB wins on document retrieval and aggregation — direct B-tree index reads with no traversal overhead.
- Neo4j is **13× faster** than MongoDB's `$lookup` approach for friend recommendation queries at this dataset size. The gap widens as the social graph grows.
- Shortest path traversal is not natively supported in MongoDB; implementing it in application code makes it impractical for real-time use.
- The two-database design is not over-engineering — it is the minimum architecture needed to serve all query patterns the application requires.

---

## Authors

| Name | Student ID |
|---|---|
| Nayla Pramesti Adhina | 2406368901 |
| Yohana Indah Nathania Br. Sihotang | 2406368946 |
| Rafael Raditya Setyono | 2406369040 |

**Project Name:** MovStream
**Course:** Database Systems Practicum 2025/2026 — Group 3
