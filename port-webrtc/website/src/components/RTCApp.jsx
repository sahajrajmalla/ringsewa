import React, { useState, useEffect } from "react";
import { useRef } from "react";
import { io } from "socket.io-client"; // Import socket.io-client

function RTCApp() {
  const [socket, setSocket] = useState(null); // Socket connection
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState("");
  const [offerUser, setOfferUser] = useState("");
  const [allUsers, setAllUsers] = useState([]);
  const [offerReceived, setOfferReceived] = useState({});
  const [connectedUser, setConnectedUser] = useState(null);

  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const connectionRef = useRef(null);
  const localStreamRef = useRef(null);

  useEffect(() => {
    // Establish socket.io connection
    const socketConnection = io("http://localhost:8088");

    socketConnection.on("connect", () => {
      console.log("Socket.io connection established");
    });
    setSocket(socketConnection);

    socketConnection.on("message", (stringData) => {
      const data = JSON.parse(stringData);
      console.log("Received:", data);
      if (!data.type) {
        console.error("Message type not found");
        return;
      }

      switch (data.type) {
        case "login":
          console.log("All users:", data.allUsers);
          setAllUsers(data.allUsers);

          navigator.mediaDevices
            .getUserMedia({ video: true, audio: true })
            .then((stream) => {
              console.log(stream);
              localStreamRef.current = stream;
              localVideoRef.current.srcObject = stream;
              console.log("sexy bot");
              const yourConn = new RTCPeerConnection({
                iceServers: [
                  { urls: "stun:stun.stunprotocol.org:3478" },
                  { urls: "stun:stun.l.google.com:19302" },
                ],
              });

              yourConn.addStream(stream);
              yourConn.onicecandidate = (event) => {
                if (event.candidate) {
                  send({ type: "candidate", candidate: event.candidate });
                }
              };
              yourConn.ontrack = (event) => {
                remoteVideoRef.current.srcObject = event.streams[0];
              };
              connectionRef.current = yourConn;
            })
            .catch((err) => {
              console.error("Error accessing media devices:", err);
            });
          break;

        case "offer":
          console.log("Received offer from:", data.name);
          setConnectedUser(data.name);
          setOfferReceived({ name: data.name, received: true });

          connectionRef.current.setRemoteDescription(
            new RTCSessionDescription(data.offer),
          );

          connectionRef.current.createAnswer().then((answer) => {
            connectionRef.current.setLocalDescription(answer);
            send({ type: "answer", answer });
          });

          break;

        case "answer":
          console.log("Received answer:", data.answer);
          handleAnswer(data.answer);
          break;

        case "candidate":
          console.log("Received candidate:", data.candidate);
          break;

        case "leave":
          console.log("User left");
          break;

        case "error":
          console.error("Error:", data.message);
          break;

        default:
          console.warn("Unknown message type:", data.type);
          break;
      }
    });

    // Clean up socket connection on unmount
    return () => {
      socketConnection.disconnect();
    };
  }, []);

  const send = (message) => {
    socket.send(JSON.stringify(message));
    console.log("Message sent:", message);
  };
  const handleAnswer = (answer) => {
    connectionRef.current.setRemoteDescription(
      new RTCSessionDescription(answer),
    );
  };

  // Function to handle login
  const handleLogin = () => {
    if (!username) return;

    const loginMessage = {
      type: "login",
      name: username,
    };
    socket.emit("message", loginMessage); // Use socket.emit to send a message
  };

  // Function to handle sending an offer
  const sendOffer = (targetUsername, offer) => {
    console.log(":hheolkw rowld");
    const offerMessage = {
      type: "offer",
      name: targetUsername,
      offer: offer,
    };

    console.log(":hheolkw rowld", offerMessage);
    socket.emit("message", offerMessage); // Use socket.emit to send an offer
  };

  return (
    <div>
      <h1>Socket.io React Client</h1>

      <div>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter your username"
        />
        <button onClick={handleLogin}>Login</button>
      </div>

      <div>
        <h3 onClick={() => console.log(allUsers)}>All Users</h3>
        <ul>
          {allUsers.map((user, index) => (
            <li key={index}>{user}</li>
          ))}
        </ul>
      </div>
      <video ref={localVideoRef} autoPlay muted style={{ width: "40%" }} />
      <video ref={remoteVideoRef} autoPlay style={{ width: "40%" }} />

      <div>
        offer aayo randi ko: {offerReceived.received ? offerReceived.name : ""}
      </div>

      <button>Accept offer</button>
      <div>
        <input
          type="text"
          value={offerUser}
          onChange={(e) => setOfferUser(e.target.value)}
          placeholder="Enter who to offer "
        />
        <button onClick={() => sendOffer(offerUser, "Special Offer")}>
          Send Offer to User
        </button>
      </div>
    </div>
  );
}

export default RTCApp;
