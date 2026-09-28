const http = require("http");
const express = require("express");
const path = require("path");
const Database = require("better-sqlite3");

const app = express();

app.use(express.static(path.join(__dirname, "public")));

const dbPath = path.join(__dirname, "data.db");
const db = new Database(dbPath);

db.exec(
  "CREATE TABLE IF NOT EXISTS notes (" +
    "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
    "title TEXT, " +
    "body TEXT" +
    ")"
);
db.exec("CREATE TABLE IF NOT EXISTS flag (flag TEXT)");

const noteCount = db.prepare("SELECT COUNT(*) AS c FROM notes").get().c;
if (noteCount === 0) {
  const insert = db.prepare("INSERT INTO notes (title, body) VALUES (?, ?)");
  insert.run("Weekly plan", "Review deployments and rotate logs.");
  insert.run("Meeting notes", "Discuss Q2 roadmap and customer feedback.");
  insert.run("Shopping list", "HDMI cable, SSD enclosure, thermal paste.");
  insert.run("Ideas", "Add pagination to admin search results.");
  insert.run("Reminder", "Check backup integrity on Friday.");
}

const flagCount = db.prepare("SELECT COUNT(*) AS c FROM flag").get().c;
if (flagCount === 0) {
  db.prepare("INSERT INTO flag (flag) VALUES (?)").run(
    "PETIR{go_90_c4rl1t0_j9d1823}"
  );
}

app.get("/admin", (req, res) => {
  res.sendFile(path.join(__dirname, "public/admin.html"));
});

app.get("/admin/search", (req, res) => {
  const q = String(req.query.q || "");
  const sql =
    "SELECT id FROM notes WHERE title LIKE '%" +
    q +
    "%' OR body LIKE '%" +
    q +
    "%'";
  let rows = [];
  try {
    rows = db.prepare(sql).all();
  } catch (err) {
    res.status(500).send("Query error");
    return;
  }

  if (rows.length > 0) {
    res.send("Found results");
  } else {
    res.send("No results");
  }
});

const server = http.createServer({ insecureHTTPParser: true }, app);
server.listen(3000);
