const { Pool } = require("pg");
require("dotenv").config({ path: "./.env" }); // Đảm bảo dotenv được load

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

// Kiểm tra kết nối
pool.connect((err, client, release) => {
  if (err) {
    return console.error("Lỗi khi kết nối tới PostgreSQL:", err.stack);
  }
  client.release();
  console.log("Đã kết nối thành công tới PostgreSQL!");
});

module.exports = {
  query: (text, params) => pool.query(text, params),
};
