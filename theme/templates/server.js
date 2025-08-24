const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

const db = new sqlite3.Database('./streamline_care.db', (err) => {
  if (err) {
    console.error('Error opening database', err);
  } else {
    console.log('Connected to SQLite database.');
  }
});

// Create tables
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS hospitals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      address TEXT NOT NULL
    )
  `);
  db.run(`
    CREATE TABLE IF NOT EXISTS doctors (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      specialty TEXT NOT NULL,
      hospital_id INTEGER,
      availability TEXT,
      FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
    )
  `);
  db.run(`
    CREATE TABLE IF NOT EXISTS appointments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      full_name TEXT NOT NULL,
      email TEXT NOT NULL,
      phone TEXT NOT NULL,
      hospital_id INTEGER,
      doctor_id INTEGER,
      date TEXT NOT NULL,
      time TEXT NOT NULL,
      reason TEXT,
      FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
      FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    )
  `);

  // Add sample hospitals if empty
  db.get('SELECT COUNT(*) as count FROM hospitals', (err, row) => {
    if (row.count === 0) {
      db.run('INSERT INTO hospitals (name, address) VALUES (?, ?)', ['Korle Bu Teaching Hospital', 'Accra']);
      db.run('INSERT INTO hospitals (name, address) VALUES (?, ?)', ['Komfo Anokye Teaching Hospital', 'Kumasi']);
      console.log('Sample hospitals added.');
    }
  });

  // Add sample doctors with availability
  db.get('SELECT COUNT(*) as count FROM doctors', (err, row) => {
    if (row.count === 0) {
      db.run(
        `INSERT INTO doctors (name, specialty, hospital_id, availability) VALUES (?, ?, ?, ?)`,
        ['Dr. Kwame Mensah', 'Cardiologist', 1, JSON.stringify({
          Monday: ['09:00 AM', '10:00 AM', '11:00 AM'],
          Wednesday: ['02:00 PM', '03:00 PM'],
          Friday: ['09:00 AM', '11:00 AM']
        })]
      );
      db.run(
        `INSERT INTO doctors (name, specialty, hospital_id, availability) VALUES (?, ?, ?, ?)`,
        ['Dr. Akua Boateng', 'Pediatrician', 2, JSON.stringify({
          Tuesday: ['08:30 AM', '09:30 AM'],
          Thursday: ['01:00 PM', '02:30 PM']
        })]
      );
      console.log('Sample doctors with availability added.');
    }
  });
});

// API Endpoints
app.get('/', (req, res) => {
  res.send('Welcome to Streamline Care API');
});

app.get('/api/hospitals', (req, res) => {
  db.all('SELECT * FROM hospitals', [], (err, rows) => {
    if (err) {
      res.status(500).send(err.message);
    } else {
      res.json(rows);
    }
  });
});

app.get('/api/doctors', (req, res) => {
  const hospitalId = req.query.hospitalId;
  db.all('SELECT * FROM doctors WHERE hospital_id = ?', [hospitalId], (err, rows) => {
    if (err) {
      res.status(500).send(err.message);
    } else {
      const doctors = rows.map(row => ({
        id: row.id,
        name: row.name,
        specialty: row.specialty,
        availability: JSON.parse(row.availability)
      }));
      res.json(doctors);
    }
  });
});

app.post('/api/appointments', (req, res) => {
  const { full_name, email, phone, hospital_id, doctor_id, date, time, reason } = req.body;
  const sql = `
    INSERT INTO appointments (full_name, email, phone, hospital_id, doctor_id, date, time, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;
  db.run(sql, [full_name, email, phone, hospital_id, doctor_id, date, time, reason], function(err) {
    if (err) {
      res.status(500).send(err.message);
    } else {
      res.json({ success: true, appointmentId: this.lastID });
    }
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
