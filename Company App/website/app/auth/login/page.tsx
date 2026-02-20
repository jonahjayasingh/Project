"use client";

import "./login.css";
import Link from "next/link";
import { IoLogInOutline, IoEye, IoEyeOff } from "react-icons/io5";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";

export default function Login() {
  const router = useRouter();

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    password: "",
  });

  // GSAP refs
  const cardRef = useRef<HTMLDivElement | null>(null);
  const titleRef = useRef<HTMLHeadingElement | null>(null);

  useEffect(() => {
    if (!cardRef.current || !titleRef.current) return;

    // ⭐ Reset before animation to avoid full white screen
    gsap.set(cardRef.current, { opacity: 1, y: 0 });
    gsap.set(titleRef.current, { opacity: 1, y: 0 });

    const anim1 = gsap.from(cardRef.current, {
      opacity: 0,
      y: 40,
      duration: 0.8,
      ease: "power3.out",
    });

    const anim2 = gsap.from(titleRef.current, {
      opacity: 0,
      y: -20,
      duration: 0.6,
      delay: 0.2,
      ease: "power2.out",
    });

    return () => {
      anim1.kill();
      anim2.kill();
      // ⭐ Reset after cleanup (prevents freeze on logout)
      if (cardRef.current) gsap.set(cardRef.current, { opacity: 1, y: 0 });
      if (titleRef.current) gsap.set(titleRef.current, { opacity: 1, y: 0 });
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!formData.name || !formData.password) {
      alert("Please fill in all fields");
      return;
    }

    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.role === "staff") router.push("/staff/dashboard");
      else if (data.role === "admin") router.push("/admin/dashboard");
      else router.push("/");
    } else {
      const errorData = await response.json();
      setError(errorData.error || "Login failed");
    }
  };

  return (
    <div className="login-page">
      <div className="login-card" ref={cardRef}>
        <h1 className="login-title" ref={titleRef}>
          Welcome Back
        </h1>

        <div className="login-icon-wrapper">
          <IoLogInOutline className="login-icon" />
        </div>

        <p className="login-subtitle">Sign in to continue</p>

        <form className="login-form" onSubmit={handleSubmit}>
          {/* Name */}
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              placeholder="Enter your name"
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
              placeholder="Enter your password"
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

          <button type="submit" className="login-button">
            Login
          </button>

          {error && <p className="error-message">{error}</p>}
        </form>

        <p className="register-text">
          Don’t have an account? <Link href="/auth/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}
