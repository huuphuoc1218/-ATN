const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const db = require("./db");

// 2. Load biến môi trường từ .env
dotenv.config({ path: "./.env" });

const app = express();
const port = process.env.PORT || 3000;

// 3. Thiết lập Middleware
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static("uploads"));

// 5. Khởi động Server
app.listen(port, () => {
  console.log(`Server đang chạy tại http://localhost:${port}`);
});
