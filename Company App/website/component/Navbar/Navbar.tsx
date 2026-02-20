"use client";
import "./Navbar.css";
import logo from "@/public/images/logo.png";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { FaBars, FaTimes } from "react-icons/fa";
import { FaChevronDown, FaGraduationCap, FaPhone, FaUserTie } from "react-icons/fa";
import { FaHome, FaInfo, FaLaptopCode } from "react-icons/fa";
import { FaDiagramProject } from "react-icons/fa6";
import { GrGallery } from "react-icons/gr";
import { MdOutlineMiscellaneousServices, MdOutlineQuestionMark } from "react-icons/md";
import { PiStudentFill } from "react-icons/pi";
import { RiVerifiedBadgeFill } from "react-icons/ri";
import { SiReaddotcv } from "react-icons/si";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <div className="navbar-container">
      <div className="nav-logo">
        <Image src={logo} alt="logo" width={150} priority />
      </div>

      {/* Hamburger */}
      <button className="hamburger" onClick={() => setOpen(!open)}>
        {open ? <FaTimes /> : <FaBars />}
      </button>

      <div className={`navbar-link-container ${open ? "active" : ""}`}>
        <Link className="link" href="/"> <FaHome /> Home </Link>
        <Link className="link" href="/#about"> <FaInfo /> About </Link>
        <Link className="link" href="/services"> <MdOutlineMiscellaneousServices /> Services </Link>
        <Link className="link" href="/portfolio"> <SiReaddotcv /> Portfolio </Link>

        {/* Dropdown */}
        <div className="dropdown">
          <button
            className="dropdown-btn link"
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            <FaLaptopCode />
            <span>Internship Training & Placement</span>
            <FaChevronDown className={`dropdown-icon ${dropdownOpen ? "rotate" : ""}`} />
          </button>

          <div className={`dropdown-content ${dropdownOpen ? "show" : ""}`}>
            <Link className="link" href="/#trainings"><FaGraduationCap /> Internship Training</Link>
            <Link className="link" href="/interview_preparation"><MdOutlineQuestionMark /> Interview Preparation</Link>
            <Link className="link" href="/#placement"><FaUserTie /> Placement</Link>
            <Link className="link" href="/"><RiVerifiedBadgeFill /> Verify Certificate</Link>
          </div>
        </div>

        <Link className="link" href="/services#projects"><FaDiagramProject /> Project</Link>
        <Link className="link" href="/#gallery"><GrGallery /> Gallery</Link>
        <Link className="link" href="/careers"><PiStudentFill /> Careers</Link>
        <Link className="contact-btn" href="/"> <FaPhone /> Contact</Link>
      </div>
    </div>
  );
}
