import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import WebRTCApp from "./components/WebRTCApp";
import RTCApp from "./components/RTCApp";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      {/* <WebRTCApp /> */}
      <RTCApp />
    </>
  );
}

export default App;
