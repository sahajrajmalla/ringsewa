import React, { useState, useEffect } from "react";
import { useRef } from "react";
import { io } from "socket.io-client"; // Import socket.io-client

function RTCApp() {
  const [socket, setSocket] = useState(io("http://localhost:8088")); // Socket connection
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState("");
  const [offerUser, setOfferUser] = useState("");
  const [allUsers, setAllUsers] = useState([]);
  const [offerReceived, setOfferReceived] = useState({});
  const [connectedUser, setConnectedUser] = useState(null);
  const [offerOfUser, setOfferOfUser] = useState(null);

  const [isCallOngoing, setIsCallOngoing] = useState(false);
  const [isReceivingCall, setIsReceivingCall] = useState(false);

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
          handleOffer(data.name, data.offer);
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
    if (socket && socket.connected) {
      socket.emit("message", message); // Send the message to the server
    } else {
      console.error("Socket is not connected");
    }
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

  const handleOffer = (name, offer) => {
    setConnectedUser(name);
    setIsReceivingCall(true);
    setOfferReceived({ name: name, received: true });
    setOfferOfUser(offer);

    connectionRef.current.setRemoteDescription(
      new RTCSessionDescription(offer),
    );

    connectionRef.current.createAnswer().then((answer) => {
      connectionRef.current.setLocalDescription(answer);
      send({ type: "answer", answer });
    });
  };
  const handleAnswerButton = () => {
    connectionRef.current.setRemoteDescription(
      new RTCSessionDescription(offerOfUser),
    );
    connectionRef.current.createAnswer().then((answer) => {
      connectionRef.current.setLocalDescription(answer);
      send({ type: "answer", answer });
    });
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

  const initiateCall = () => {
    if (!offerUser) {
      alert("Username can't be blank!");
      return;
    }
    console.log(offerUser);

    setConnectedUser(offerUser);
    console.log("connecte", connectionRef.current);
    //
    connectionRef.current.createOffer().then((offer) => {
      connectionRef.current.setLocalDescription(offer);
      console.log("offer", offer);
      send({ type: "offer", offer, name: offerUser });
      setIsCallOngoing(true);
    });
  };

  const handleLeave = () => {
    setConnectedUser(null);
    setIsCallOngoing(false);
    remoteVideoRef.current.srcObject = null;
    connectionRef.current.close();
    connectionRef.current = null;
  };

  const hangUp = () => {
    send({ type: "leave" });
    handleLeave();
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

      {isReceivingCall && (
        <>
          <button
            onClick={() => {
              handleAnswerButton();
              setIsCallOngoing(true);
              setIsReceivingCall(false);
            }}
          >
            Answer
          </button>
          <button
            onClick={() => {
              setConnectedUser(null);
              setIsReceivingCall(false);
            }}
          >
            Decline
          </button>
        </>
      )}

      {isCallOngoing && (
        <div id="callOngoing">
          <button onClick={hangUp}>Hang Up</button>
        </div>
      )}
      <div>
        <input
          type="text"
          value={offerUser}
          onChange={(e) => setOfferUser(e.target.value)}
          placeholder="Enter who to offer "
        />
        <button onClick={() => initiateCall()}>Send Offer to User</button>
      </div>
    </div>
  );
}

export default RTCApp;
