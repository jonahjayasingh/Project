const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const path = require("path");

const app = express();
const port = 3000;

app.use(bodyParser.json());

const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: "./whatsapp_session",
  }),
  puppeteer: {
    headless: true,
    args: [
        "--no-sandbox", 
        "--disable-setuid-sandbox",
        "--disable-extensions",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--single-process", // <- This can help with memory/frame issues on shared environments
        "--disable-gpu"
    ],
  },
});

let isReady = false;

client.on("qr", (qr) => {
  console.log("SCAN THIS QR CODE WITH WHATSAPP:");
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("WhatsApp Client is ready!");
  isReady = true;
});

client.on("authenticated", () => {
  console.log("AUTHENTICATED");
});

client.on("auth_failure", (msg) => {
  console.error("AUTHENTICATION FAILURE", msg);
});

client.on("disconnected", (reason) => {
  console.log("Client was logged out", reason);
  isReady = false;
});

client.initialize();

// API Endpoints
app.post("/send-message", async (req, res) => {
  if (!isReady) {
    return res
      .status(503)
      .json({ success: false, message: "WhatsApp client is not ready" });
  }

  const { number, message, filePath } = req.body;

  if (!number || (!message && !filePath)) {
    return res
      .status(400)
      .json({ success: false, message: "Missing number, message or filePath" });
  }

  try {
    // Format number: remove all non-digits
    let formattedNumber = number.replace(/[^\d]/g, "");
    
    // Add country code 91 if it's a 10-digit number
    if (formattedNumber.length === 10) {
        formattedNumber = "91" + formattedNumber;
    }
    
    // Ensure it ends with @c.us
    if (!formattedNumber.endsWith("@c.us")) {
      formattedNumber += "@c.us";
    }

    if (filePath) {
      if (fs.existsSync(filePath)) {
        const media = MessageMedia.fromFilePath(filePath);
        await client.sendMessage(formattedNumber, media, {
          caption: message || "",
        });
      } else {
        return res
          .status(404)
          .json({ success: false, message: "File not found at " + filePath });
      }
    } else {
      // Use getNumberId to verify the number is valid and get the correct ID if possible
      // This can help avoid some 'detached frame' issues by ensuring context is active
      await client.sendMessage(formattedNumber, message);
    }

    res.json({ success: true, message: "Message sent successfully" });
  } catch (error) {
    console.error("Error sending message:", error);
    res.status(500).json({ success: false, message: error.message });
  }
});

app.get("/status", (req, res) => {
  res.json({ ready: isReady });
});

app.listen(port, () => {
  console.log(`WhatsApp API service listening at http://localhost:${port}`);
});
