import { useState, useRef } from "react";
import Webcam from "react-webcam";
import { Upload, Camera, Play, Video } from "lucide-react";
import "./Compare.css";

function Compare() {
	const [referenceVideo, setReferenceVideo] = useState(null);
	const [userVideo, setUserVideo] = useState(null);
	const [isRecording, setIsRecording] = useState(false);
	const [showCamera, setShowCamera] = useState(false);
	const [processing, setProcessing] = useState(false);
	const [accuracyMessage, setAccuracyMessage] = useState(null);
	const webcamRef = useRef(null);
	const mediaRecorderRef = useRef(null);
	const [recordedChunks, setRecordedChunks] = useState([]);

	const handleReferenceUpload = (event) => {
		const file = event.target.files?.[0];
		if (file) {
			const url = URL.createObjectURL(file);
			setReferenceVideo(url);
		}
	};

	const handleReferenceURL = (event) => {
		setReferenceVideo(event.target.value);
	};

	const handleUserUpload = (event) => {
		const file = event.target.files?.[0];
		if (file) {
			const url = URL.createObjectURL(file);
			setUserVideo(url);
		}
	};

	const startRecording = () => {
		setRecordedChunks([]);
		if (webcamRef.current?.stream) {
			mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
				mimeType: "video/webm",
			});
			mediaRecorderRef.current.addEventListener(
				"dataavailable",
				handleDataAvailable
			);
			mediaRecorderRef.current.start();
			setIsRecording(true);
		}
	};

	const stopRecording = () => {
		if (mediaRecorderRef.current) {
			mediaRecorderRef.current.stop();
			setIsRecording(false);
		}
	};

	const handleDataAvailable = ({ data }) => {
		if (data.size > 0) {
			setRecordedChunks((prev) => [...prev, data]);
		}
	};

	const handleDownload = () => {
		if (recordedChunks.length) {
			const blob = new Blob(recordedChunks, { type: "video/webm" });
			const url = URL.createObjectURL(blob);
			setUserVideo(url);
			setShowCamera(false);
		}
	};

	const handleComparison = () => {
		setProcessing(true);
		setTimeout(() => {
			const accuracy = Math.random() > 0.5 ? "well-done" : "please try again";
			setAccuracyMessage(
				accuracy === "well-done"
					? "Accuracy correct! Well done!"
					: "Accuracy error - please try again with a new video."
			);
			setProcessing(false);
		}, 3000);
	};

	return (
		<div className='container'>
			<header className='header'>
				<h1>Dance Comparison Platform</h1>
			</header>
			<main className='content'>
				<div className='video-section'>
					{/* Reference Video */}
					<div className='video-box'>
						<h2>Reference Dance</h2>
						{referenceVideo ? (
							<video
								src={referenceVideo}
								controls
								className='video'
							/>
						) : (
							<div className='video-placeholder'>
								<Video className='icon' />
							</div>
						)}
						<div className='upload-section'>
							<label>
								Upload Video
								<input
									type='file'
									accept='video/*'
									onChange={handleReferenceUpload}
								/>
							</label>
							<input
								type='url'
								placeholder='Enter Video URL'
								onChange={handleReferenceURL}
								className='url-input'
							/>
						</div>
					</div>

					{/* User Video */}
					<div className='video-box'>
						<h2>Your Dance</h2>
						{showCamera ? (
							<div className='camera-section'>
								<Webcam
									ref={webcamRef}
									audio={true}
									className='video'
								/>
								<div className='camera-buttons'>
									{!isRecording ? (
										<button
											onClick={startRecording}
											className='btn record'>
											<Camera className='icon' />
											Start Recording
										</button>
									) : (
										<button
											onClick={stopRecording}
											className='btn stop'>
											Stop Recording
										</button>
									)}
									{recordedChunks.length > 0 && (
										<button
											onClick={handleDownload}
											className='btn use-recording'>
											Use Recording
										</button>
									)}
								</div>
							</div>
						) : userVideo ? (
							<video
								src={userVideo}
								controls
								className='video'
							/>
						) : (
							<div className='video-placeholder'>
								<Video className='icon' />
							</div>
						)}

						{!showCamera && (
							<div className='upload-section'>
								<label>
									Upload Video
									<input
										type='file'
										accept='video/*'
										onChange={handleUserUpload}
									/>
								</label>
								<button
									onClick={() => setShowCamera(true)}
									className='btn camera'>
									<Camera className='icon' />
									Use Camera
								</button>
							</div>
						)}
					</div>
				</div>

				{/* Compare Button */}
				<button
					disabled={!referenceVideo || !userVideo || processing}
					onClick={handleComparison}
					className={`btn compare ${
						referenceVideo && userVideo && !processing ? "active" : "disabled"
					}`}>
					<Play className='icon' />
					Start Comparison
				</button>

				{/* Accuracy Message */}
				{accuracyMessage && (
					<p className='accuracy-message'>{accuracyMessage}</p>
				)}
			</main>
		</div>
	);
}

export default Compare;
