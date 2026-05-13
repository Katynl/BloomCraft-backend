// utils/multer.js
const multer = require("multer");
const storage = multer.memoryStorage(); // Сохраняем файл во временной памяти
const upload = multer({ storage: storage });
module.exports = upload;
