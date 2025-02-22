import React from "react";
import { MessageCircle, ThumbsUp } from "lucide-react";
import "./Feedback.css"; // Import the CSS file

const feedbacks = [
  { id: 1, user: "John Doe", date: "Feb 22, 2025", message: "Great platform!", likes: 10 },
  { id: 2, user: "Jane Smith", date: "Feb 21, 2025", message: "Very helpful!", likes: 8 },
];

function Feedback() {
  return (
    
    <div className="feedback-container">
      <div className="feedback-wrapper">
        <h1 className="feedback-title">Community Feedback</h1>

        {/* Feedback Form */}
        <div className="feedback-form">
          <h2 className="form-title">Share Your Experience</h2>
          <textarea className="feedback-input" rows={4} placeholder="Write your feedback here..." />
          <button className="submit-button">
            <MessageCircle className="icon" />
            Submit Feedback
          </button>
        </div>

        {/* Feedback List */}
        <div className="feedback-list">
          {feedbacks.map((feedback) => (
            <div key={feedback.id} className="feedback-item">
              <div className="feedback-header">
                <div>
                  <h3 className="feedback-user">{feedback.user}</h3>
                  <p className="feedback-date">{feedback.date}</p>
                </div>
                <button className="like-button">
                  <ThumbsUp className="icon" />
                  <span>{feedback.likes}</span>
                </button>
              </div>
              <p className="feedback-message">{feedback.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Feedback;
