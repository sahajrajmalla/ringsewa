const express = require("express");
const http = require("http");
const socketIo = require("socket.io"); // Import socket.io
const cors = require("cors");

// Create an Express application
const app = express();
app.use(
  cors({
    origin: "*", // Allow all origins for simplicity, adjust this as needed
  }),
);

// Define the HTTP port
const HTTP_PORT = process.env.PORT || 8088;

// Create an HTTP server using Express
const httpServer = http.createServer(app);

// All connected users
const users = new Map();
const allUsers = new Set();

// Create a Socket.IO instance attached to the HTTP server
const io = socketIo(httpServer, {
  cors: {
    origin: "*", // Allow all origins for simplicity, adjust this as needed
    methods: ["GET", "POST"],
  },
});

// Function to validate message structure
function isValidMessage(data) {
  const requiredFields = {
    login: ["name"],
    offer: ["name", "offer"],
    answer: ["name", "answer"],
    candidate: ["name", "candidate"],
    leave: ["name"],
  };

  if (!data || !data.type) return false;

  const fields = requiredFields[data.type];
  return fields ? fields.every((field) => data[field] !== undefined) : false;
}

// Handle incoming Socket.IO connections
io.on("connection", (socket) => {
  console.log("New Socket.io connection established.");

  // Handle messages from clients
  socket.on("message", (message) => {
    try {
      let data;

      // Parse JSON messages
      data = message;

      console.log("Received data:", data);

      // Handle different message types
      switch (data.type) {
        case "login":
          handleLogin(socket, data);
          break;

        case "offer":
          handleOffer(socket, data);
          break;

        case "answer":
          handleAnswer(socket, data);
          break;

        case "candidate":
          handleCandidate(socket, data);
          break;

        case "leave":
          handleLeave(socket, data);
          break;

        default:
          console.warn("Unknown command:", data.type);
          sendTo(socket, {
            type: "error",
            message: "Command not found: " + data.type,
          });
          break;
      }
    } catch (err) {
      console.error("Error handling message:", err);
      sendTo(socket, {
        type: "error",
        message: "An unexpected error occurred.",
      });
    }
  });

  // Handle disconnection
  socket.on("disconnect", () => {
    try {
      if (socket.username) {
        console.log("Closing connection for:", socket.username);

        users.delete(socket.username);
        allUsers.delete(socket.username);

        if (socket.otherUsername) {
          console.log("Disconnecting from:", socket.otherUsername);
          const conn = users.get(socket.otherUsername);
          if (conn) {
            conn.otherUsername = null;
            sendTo(conn, { type: "leave" });
          }
        }
      }
    } catch (err) {
      console.error("Error handling Socket.io disconnection:", err);
    }
  });
});

// Function to send messages to clients
function sendTo(connection, message) {
  try {
    console.log("hello message", message);
    connection.emit("message", JSON.stringify(message)); // Use emit for Socket.io
  } catch (err) {
    console.error("Error sending message:", err);
  }
}

// Function to handle user login
function handleLogin(socket, data) {
  console.log("User logged in:", data.name);
  if (users.has(data.name)) {
    sendTo(socket, {
      type: "login",
      success: false,
      allUsers: Array.from(allUsers),
    });
  } else {
    users.set(data.name, socket);
    allUsers.add(data.name);
    socket.username = data.name;

    sendTo(socket, {
      type: "login",
      success: true,
      allUsers: Array.from(allUsers),
    });
  }
}

// Function to handle offer messages
function handleOffer(socket, data) {
  console.log("Sending offer to:", data.name);
  const conn = users.get(data.name);
  if (conn) {
    socket.otherUsername = data.name;
    sendTo(conn, { type: "offer", offer: data.offer, name: socket.username });
  } else {
    sendTo(socket, { type: "error", message: "User not found: " + data.name });
  }
}

// Function to handle answer messages
function handleAnswer(socket, data) {
  console.log("Sending answer to:", data.name);
  const conn = users.get(data.name);
  if (conn) {
    socket.otherUsername = data.name;
    sendTo(conn, { type: "answer", answer: data.answer });
  } else {
    sendTo(socket, { type: "error", message: "User not found: " + data.name });
  }
}

// Function to handle candidate messages
function handleCandidate(socket, data) {
  console.log("Sending candidate to:", data.name);
  const conn = users.get(data.name);
  if (conn) {
    sendTo(conn, { type: "candidate", candidate: data.candidate });
  } else {
    sendTo(socket, { type: "error", message: "User not found: " + data.name });
  }
}

// Function to handle leave messages
function handleLeave(socket, data) {
  console.log("Disconnecting from:", data.name);
  const conn = users.get(data.name);
  if (conn) {
    conn.otherUsername = null;
    sendTo(conn, { type: "leave" });
  }
}

// Start the HTTP server on the defined port
httpServer.listen(HTTP_PORT, "0.0.0.0", () => {
  console.log(
    `Server running. Visit http://localhost:${HTTP_PORT} in your browser.`,
  );
});
