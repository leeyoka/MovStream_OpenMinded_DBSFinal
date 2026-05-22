const express = require('express');
const app = express();

app.use(express.json());

app.get('/users/register', (req, res) => {
  res.json({
    message: 'Register page works'
  });
});

// Login user
app.get('/users/login', (req, res) => {
  res.json({
    message: 'Login page works'
  });
});

// Get user profile
app.get('/users/:id', (req, res) => {
  res.json({
    user_id: req.params.id,
    username: 'felicia',
    email: 'felicia@ui.ac.id'
  });
});

// Follow user
app.get('/users/:id/follow/:targetId', (req, res) => {
  res.json({
    message: `${req.params.id} followed ${req.params.targetId}`
  });
});

// Get all movies
app.get('/movies', (req, res) => {
  res.json([
    {
      movieId: 'm_001',
      title: 'Dune Part Two'
    },
    {
      movieId: 'm_002',
      title: 'Interstellar'
    }
  ]);
});

// Get movie by ID
app.get('/movies/:id', (req, res) => {
  res.json({
    movieId: req.params.id,
    title: 'Dune Part Two'
  });
});

// Add movie
app.get('/movies/add', (req, res) => {
  res.json({
    message: 'Movie added successfully'
  });
});

// Submit review
app.get('/reviews/add', (req, res) => {
  res.json({
    message: 'Review submitted'
  });
});

// Get reviews for a movie
app.get('/reviews/:movieId', (req, res) => {
  res.json({
    movie_id: req.params.movieId,
    reviews: [
      {
        user: 'felicia',
        rating: 4.5,
        text: 'Amazing movie'
      }
    ]
  });
});

// Log watch event
app.get('/watch/add', (req, res) => {
  res.json({
    message: 'Watch log added'
  });
});

// Get watch history
app.get('/watch/:userId', (req, res) => {
  res.json({
    user_id: req.params.userId,
    history: [
      {
        movie: 'Dune Part Two',
        completed: true
      }
    ]
  });
});


app.listen(3000, () => {
  console.log('Server running on port 3000');
});
