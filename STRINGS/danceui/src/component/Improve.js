import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";
import './Improve.css'; // Import your CSS file

const AreaOfImprovements = () => {
  return (
    <div className="area-improvements">
      <h2>Area of Improvements</h2>
      <ul>
        <li>Bend your leg</li>
        <li>Your movements are mostly accurate</li>
      </ul>
    </div>
  );
};

const DetailedFeedback = () => {
  return (
    <div className="detailed-feedback">
      <h2>Detailed Feedback</h2>
      <ul>
        <li>0:00 Bend left leg</li>
        <li>0:05 Bend right arm</li>
        <li>0:10 Bend right hand</li>
      </ul>
    </div>
  );
};

const ChatPopup = () => {
  const openChatGPT = () => {
    window.open("https://chat.openai.com/", "_blank");
  };
  return <button className="chat-btn" onClick={openChatGPT}>Open ChatGPT</button>;
};

const AccuracyGraph = () => {
  const [showGraph, setShowGraph] = useState(false);
  const data = {
    labels: ["0s", "5s", "10s", "15s"],
    datasets: [
      {
        label: "Accuracy Over Time",
        data: [80, 85, 90, 95],
        borderColor: "blue",
        fill: false,
      },
    ],
  };
  return (
    <div className="accuracy-section">
      <button onClick={() => setShowGraph(!showGraph)}>
        Show Accuracy Graph
      </button>
      {showGraph && <Line data={data} />}
    </div>
  );
};

const Improve = () => {
  return (
    <div className="container">
      <AreaOfImprovements />
      <DetailedFeedback />
      <ChatPopup />
      <AccuracyGraph />
    </div>
  );
};

export default Improve;
