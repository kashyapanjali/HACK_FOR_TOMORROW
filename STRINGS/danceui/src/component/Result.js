import React, { useEffect, useState } from "react";
import { CheckCircle, XCircle } from "lucide-react";
import "./Result.css";

function Result({ comparisonData }) {
	const [feedback, setFeedback] = useState([]);

	useEffect(() => {
		if (comparisonData) {
			processFeedback(comparisonData);
		}
	}, [comparisonData]);

	const processFeedback = (data) => {
		const feedbackList = data.frames
			.map((frame, index) => {
				if (frame.similarity < 0.7) {
					return {
						timestamp: frame.timestamp,
						message: `Frame ${index + 1}: ${frame.feedback}`,
					};
				}
				return null;
			})
			.filter((item) => item !== null);
		setFeedback(feedbackList);
	};

	return (
		<div className='result-container'>
			<header className='header'>
				<h1>Comparison Results</h1>
			</header>
			<main className='content'>
				<div className='accuracy-section'>
					<h2>Overall Accuracy</h2>
					<p
						className={`accuracy ${
							comparisonData.accuracy > 0.7 ? "high" : "low"
						}`}>
						{Math.round(comparisonData.accuracy * 100)}%
					</p>
				</div>

				<div className='feedback-section'>
					<h2>Improvement Areas</h2>
					{feedback.length > 0 ? (
						<ul>
							{feedback.map((item, index) => (
								<li key={index}>
									<XCircle className='icon error' /> {item.timestamp}s -{" "}
									{item.message}
								</li>
							))}
						</ul>
					) : (
						<p>
							<CheckCircle className='icon success' /> Great job! No major
							improvements needed.
						</p>
					)}
				</div>
			</main>
		</div>
	);
}

export default Result;
