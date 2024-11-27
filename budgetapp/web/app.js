// Import necessary modules
const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const moment = require('moment');
const { engine } = require('express-handlebars');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const session = require('express-session');
const bcrypt = require('bcryptjs');
const app = express();
const port = process.env.PORT || 3000;

// Set up middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Set up session management
app.use(session({
  secret: 'secret',
  resave: false,
  saveUninitialized: true
}));

// Initialize Passport.js
app.use(passport.initialize());
app.use(passport.session());

// Connect to SQLite database in the parent directory
const dbPath = path.resolve(__dirname, '..', 'budget_tracker.db');
const db = new sqlite3.Database(dbPath);

// Set up Handlebars view engine
app.engine('handlebars', engine({ defaultLayout: 'main' }));
app.set('view engine', 'handlebars');
app.set('views', path.join(__dirname, 'views'));

// Configure Passport.js
passport.use(new LocalStrategy((username, password, done) => {
  db.get('SELECT id, username, password FROM users WHERE username = ?', [username], (err, user) => {
    if (err) return done(err);
    if (!user) return done(null, false, { message: 'Incorrect username.' });

    bcrypt.compare(password, user.password, (err, res) => {
      if (res) {
        return done(null, user);
      } else {
        return done(null, false, { message: 'Incorrect password.' });
      }
    });
  });
}));

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser((id, done) => {
  db.get('SELECT id, username FROM users WHERE id = ?', [id], (err, user) => {
    done(err, user);
  });
});

// Function to get the current balance
const getCurrentBalance = (callback) => {
  db.get("SELECT SUM(amount) AS total_income FROM income", (err, incomeRow) => {
    if (err) {
      console.error(err);
      callback(0); // Return zero in case of error
      return;
    }
    const totalIncome = incomeRow ? incomeRow.total_income : 0;
    db.get("SELECT SUM(amount) AS total_expenses FROM expenses", (err, expenseRow) => {
      if (err) {
        console.error(err);
        callback(totalIncome); // Return income as balance in case of error
        return;
      }
      const totalExpenses = expenseRow ? expenseRow.total_expenses : 0;
      callback(totalIncome - totalExpenses);
    });
  });
};

// Route for the homepage
app.get('/', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  getCurrentBalance((balance) => {
    res.render('home', { balance: balance.toFixed(2), user: req.user });
  });
});

// Route for login
app.get('/login', (req, res) => {
  res.render('login');
});

app.post('/login', passport.authenticate('local', {
  successRedirect: '/',
  failureRedirect: '/login'
}));

// Route for signup
app.get('/signup', (req, res) => {
  res.render('signup');
});

app.post('/signup', (req, res) => {
  const { username, password } = req.body;
  bcrypt.hash(password, 10, (err, hash) => {
    if (err) {
      res.status(500).send('Failed to sign up');
    } else {
      db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, hash], (err) => {
        if (err) {
          res.status(500).send('Failed to sign up');
        } else {
          res.redirect('/login');
        }
      });
    }
  });
});

// Route for logout
app.get('/logout', (req, res) => {
  req.logout(() => {
    res.redirect('/login');
  });
});

// Route to show the form for adding an expense
app.get('/add-expense-form', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  res.render('add-expense-form');
});

// Route to show the form for adding income
app.get('/add-income-form', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  res.render('add-income-form');
});

// Route to add an expense
app.post('/add-expense', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  const { description, amount, category, larger_category, feeling } = req.body;
  const timestamp = moment().format('YYYY-MM-DD HH:mm:ss'); // Format timestamp
  db.run(`
    INSERT INTO expenses (description, amount, category, larger_category, timestamp, feeling)
    VALUES (?, ?, ?, ?, ?, ?)
  `, [description, amount, category, larger_category, timestamp, feeling], (err) => {
    if (err) {
      res.status(500).send('Failed to add expense');
    } else {
      getCurrentBalance((balance) => {
        res.render('expense-success', { balance: balance.toFixed(2), user: req.user });
      });
    }
  });
});

// Route to add income
app.post('/add-income', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  const { amount, category } = req.body;
  const timestamp = moment().format('YYYY-MM-DD HH:mm:ss'); // Format timestamp
  db.run(`
    INSERT INTO income (amount, category, timestamp)
    VALUES (?, ?, ?)
  `, [amount, category, timestamp], (err) => {
    if (err) {
      res.status(500).send('Failed to add income');
    } else {
      getCurrentBalance((balance) => {
        res.render('income-success', { balance: balance.toFixed(2), user: req.user });
      });
    }
  });
});

// Route to view expenses
app.get('/expenses', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  db.all("SELECT * FROM expenses ORDER BY timestamp DESC", (err, rows) => {
    if (err) {
      res.status(500).send('Failed to retrieve expenses');
    } else {
      res.render('expenses', { expenses: rows, user: req.user });
    }
  });
});

// Route to view income
app.get('/income', (req, res) => {
  if (!req.isAuthenticated()) {
    return res.redirect('/login');
  }
  db.all("SELECT * FROM income ORDER BY timestamp DESC", (err, rows) => {
    if (err) {
      res.status(500).send('Failed to retrieve income');
    } else {
      res.render('income', { income: rows, user: req.user });
    }
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
