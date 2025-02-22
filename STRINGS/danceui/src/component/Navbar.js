import React, { useState, useEffect } from "react";
import "./Navbar.css";
import icon from "../assets/icon.png"; // Importing the image

const Navbar = () => {
	const [prevScrollY, setPrevScrollY] = useState(0);
	const [isHidden, setIsHidden] = useState(false);

	useEffect(() => {
		const handleScroll = () => {
			const currentScrollY = window.scrollY;
			if (currentScrollY > prevScrollY) {
				setIsHidden(true); // Flip up and hide when scrolling down
			} else {
				setIsHidden(false); // Flip down and show when scrolling up
			}
			setPrevScrollY(currentScrollY);
		};

		window.addEventListener("scroll", handleScroll);
		return () => window.removeEventListener("scroll", handleScroll);
	}, [prevScrollY]);

	return (
		<header className={`navbar ${isHidden ? "hidden" : ""}`}>
			<div className='logo'>
				<a href='/'>
					<img
						className='icon'
						src={icon}
					/>
					Dance Zero
				</a>
			</div>
			<nav className='nav-links'>
				<a href='/home'>Home</a>
				<a href='/compare'>Dance-Compare</a>
				<a href='/feedback'>Feedback</a>
				<a href='/improve'>Improve</a>

				<a
					href='/login'
					className='login-btn'>
					<i className='fa fa-user'></i> Logout
				</a>
				<button className='search-btn'>
					<i className='fa fa-search'></i>
				</button>
			</nav>
		</header>
	);
};

export default Navbar;
