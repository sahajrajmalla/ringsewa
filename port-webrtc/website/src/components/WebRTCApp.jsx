import React, { useState, useRef, useEffect } from "react";
import { io } from "socket.io-client";

const WebRTCApp = () => {
  const [name, setName] = useState("");
  const [connectedUser, setConnectedUser] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [callToUsername, setCallToUsername] = useState("");
  const [isCallOngoing, setIsCallOngoing] = useState(false);
  const [isReceivingCall, setIsReceivingCall] = useState(false);

  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const connectionRef = useRef(null);
  const localStreamRef = useRef(null);

  const serverConnection = useRef(io(`http://localhost:8088`));

  useEffect(() => {
    const handleServerMessage = (message) => {
      const data = JSON.parse(message.data);

      switch (data.type) {
        case "login":
          handleLogin(data.success, data.allUsers);
          break;
        case "offer":
          handleOffer(data.offer, data.name);
          break;
        case "answer":
          handleAnswer(data.answer);
          break;
        case "candidate":
          handleCandidate(data.candidate);
          break;
        case "leave":
          handleLeave();
          break;
        default:
          break;
      }
    };

    serverConnection.current.onopen = () => {
      console.log("Connected to the signaling server");
    };
    serverConnection.current.onmessage = handleServerMessage;
    serverConnection.current.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => {
      serverConnection.current.close();
    };
  }, []);

  const handleLogin = (success, users) => {
    if (!success) {
      alert("Oops...try a different username");
      return;
    }
    console.log(users);
    setAllUsers(users);
    navigator.mediaDevices
      .getUserMedia({ video: true, audio: true })
      .then((stream) => {
        localStreamRef.current = stream;
        localVideoRef.current.srcObject = stream;
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
  };

  const send = (message) => {
    if (connectedUser) message.name = connectedUser;
    serverConnection.current.send(JSON.stringify(message));
    console.log("Message sent:", message);
  };

  const handleOffer = (offer, name) => {
    setConnectedUser(name);
    setIsReceivingCall(true);

    connectionRef.current.setRemoteDescription(
      new RTCSessionDescription(offer),
    );

    connectionRef.current.createAnswer().then((answer) => {
      connectionRef.current.setLocalDescription(answer);
      send({ type: "answer", answer });
    });
  };

  const handleAnswer = (answer) => {
    connectionRef.current.setRemoteDescription(
      new RTCSessionDescription(answer),
    );
  };

  const handleCandidate = (candidate) => {
    connectionRef.current.addIceCandidate(new RTCIceCandidate(candidate));
  };

  const handleLeave = () => {
    setConnectedUser(null);
    setIsCallOngoing(false);
    remoteVideoRef.current.srcObject = null;
    connectionRef.current.close();
    connectionRef.current = null;
  };

  const initiateCall = () => {
    if (!callToUsername) {
      alert("Username can't be blank!");
      return;
    }
    setConnectedUser(callToUsername);

    connectionRef.current.createOffer().then((offer) => {
      connectionRef.current.setLocalDescription(offer);
      send({ type: "offer", offer });
      setIsCallOngoing(true);
    });
  };

  const hangUp = () => {
    send({ type: "leave" });
    handleLeave();
  };

  return (
    <div>
      {!connectedUser && (
        <div id="myName">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My name"
          />
          <button onClick={() => send({ type: "login", name })}>Save</button>
        </div>
      )}

      {connectedUser && (
        <div id="otherElements">
          <b>Hello, {name}</b>
          <video ref={localVideoRef} autoPlay muted style={{ width: "40%" }} />
          <video ref={remoteVideoRef} autoPlay style={{ width: "40%" }} />

          {!isCallOngoing && !isReceivingCall && (
            <div id="callInitiator">
              <input
                type="text"
                value={callToUsername}
                onChange={(e) => setCallToUsername(e.target.value)}
                placeholder="Username to call"
              />
              <button onClick={initiateCall}>Call</button>
            </div>
          )}

          {isReceivingCall && (
            <div id="callReceiver">
              <button
                onClick={() => {
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
            </div>
          )}

          {isCallOngoing && (
            <div id="callOngoing">
              <button onClick={hangUp}>Hang Up</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WebRTCApp;
