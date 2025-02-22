import React, { useState } from "react";
import "./Auth.css";

const Auth = () => {
	const [isSignup, setIsSignup] = useState(false);
	const [formData, setFormData] = useState({
		name: "",
		email: "",
		password: "",
	});

	const handleChange = (e) => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		console.log(isSignup ? "Signup Data: " : "Login Data: ", formData);
	};

	const toggleForm = () => {
		setIsSignup(!isSignup);
		setFormData({ name: "", email: "", password: "" });
	};

	return (
		<div className='auth-container'>
			<div className='auth-box'>
				<h2>{isSignup ? "Sign Up" : "Login"}</h2>
				<form onSubmit={handleSubmit}>
					{isSignup && (
						<input
							type='text'
							name='name'
							placeholder='Full Name'
							value={formData.name}
							onChange={handleChange}
							required
						/>
					)}
					<input
						type='email'
						name='email'
						placeholder='Email'
						value={formData.email}
						onChange={handleChange}
						required
					/>
					<input
						type='password'
						name='password'
						placeholder='Password'
						value={formData.password}
						onChange={handleChange}
						required
					/>
					<button type='submit'>{isSignup ? "Sign Up" : "Login"}</button>
				</form>
				<p
					onClick={toggleForm}
					className='toggle-text'>
					{isSignup
						? "Already have an account? Login"
						: "Don't have an account? Sign Up"}
				</p>
			</div>
		</div>
	);
};

export default Auth;
