"use client";

import "./register.css";
import Link from "next/link";
import { IoPersonAddOutline, IoEye, IoEyeOff } from "react-icons/io5";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";

export default function Register() {
  const router = useRouter();

  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // GSAP refs
  const cardRef = useRef<HTMLDivElement | null>(null);
  const titleRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    gsap.from(cardRef.current, {
      opacity: 0,
      y: 40,
      duration: 0.8,
      ease: "power3.out",
    });

    gsap.from(titleRef.current, {
      opacity: 0,
      y: -20,
      duration: 0.6,
      delay: 0.2,
      ease: "power2.out",
    });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    if (!formData.name || !formData.email || !formData.password) {
      alert("Please fill in all fields");
      return;
    }

    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: formData.name,
        email: formData.email,
        password: formData.password,
      }),
    });

    if (response.ok) {
      router.push("/auth/login");
    } else {
      const errorData = await response.json();
      console.log(errorData);
      setError(errorData.error || "Registration failed");
      return;
    }
  };

  return (
    <div className="register-page">
      <div className="register-card" ref={cardRef}>
        <h1 className="register-title" ref={titleRef}>
          Create an Account
        </h1>

        <div className="register-icon-wrapper">
          <IoPersonAddOutline className="register-icon" />
        </div>

        <p className="register-subtitle">Join our community today</p>

        <form className="register-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              placeholder="Enter your full name"
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              placeholder="Enter your email"
              onChange={handleChange}
              required
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              placeholder="Create a password"
              onChange={handleChange}
              required
            />
            <span
              className="password-inside-icon"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <IoEyeOff /> : <IoEye />}
            </span>
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type={showConfirmPassword ? "text" : "password"}
              id="confirmPassword"
              placeholder="Confirm your password"
              onChange={handleChange}
              required
            />
            <span
              className="password-inside-icon"
              onClick={() =>
                setShowConfirmPassword(!showConfirmPassword)
              }
            >
              {showConfirmPassword ? <IoEyeOff /> : <IoEye />}
            </span>
          </div>

          <button type="submit" className="register-button">
            Create Account
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}

        <p className="login-text">
          Already have an account? <Link href="/auth/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
