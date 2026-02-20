"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import gsap from "gsap";

import "./adminsidebar.css";

import { TfiWorld } from "react-icons/tfi";
import { FiHome, FiInfo, FiLogOut, FiUserPlus } from "react-icons/fi";
import { ImProfile } from "react-icons/im";
import { FaDatabase, FaServer } from "react-icons/fa";
import { BiBookAdd } from "react-icons/bi";
import { MdOutlineReviews, MdContactPhone, MdOutlineWorkOutline } from "react-icons/md";
import { FaDiagramProject } from "react-icons/fa6";
import { GrDomain, GrGallery } from "react-icons/gr";
import { PiStudentBold } from "react-icons/pi";
import { RiPaypalLine } from "react-icons/ri";
import { CiDatabase } from "react-icons/ci";

interface AdminSidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (value: boolean) => void;
    openAddCourse: () => void;   // 🔥 add this
    openAddGallery: () => void;   // 🔥 add this
    openAddServices: () => void;   // 🔥 add this
    openAddTestimonial: () => void;   // 🔥 add this
    openAddProjectDomain: () => void;   // 🔥 add this
    openAddProject: () => void;   // 🔥 add this
    openAddContact: () => void;   // 🔥 add this
}

export default function AdminSidebar({ sidebarOpen, setSidebarOpen,openAddCourse,openAddGallery,openAddServices,openAddTestimonial,openAddProjectDomain,openAddProject,openAddContact }: AdminSidebarProps) {
  const [websiteOpen, setWebsiteOpen] = useState(false);
  const sidebarRef = useRef<HTMLElement | null>(null);
  const router = useRouter();

  useEffect(() => {
    const textItems = sidebarRef.current?.querySelectorAll(".text") || [];

    if (sidebarOpen) {
      gsap.to(textItems, { opacity: 1, x: 0, duration: 0., stagger: 0.05 });
    } else {
      gsap.to(textItems, { opacity: 0, x: -20, duration: 0.2 });
    }
  }, [sidebarOpen]);

  async function handleLogout() {
  await fetch("/api/auth/logout", { method: "POST" });
  setSidebarOpen(false);
  gsap.set("*", { filter: "none", backdropFilter: "none" });

  setTimeout(() => router.push("/auth/login"), 50);
}


  return (
    <>
      {/* Mobile toggle button */}
      <button className="mobile-toggle" onClick={() => setSidebarOpen(true)}>
        <svg width="32" height="32" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <aside ref={sidebarRef} className={`sidebar ${sidebarOpen ? "open" : "collapsed"}`}>
        <div className="sidebar-scroll">
          <div className="sidebar-header internal-toggle">
            <button className="sidebar-toggle-btn desktop-only" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <svg width="26" height="26" stroke="currentColor" strokeWidth="2">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>

            {sidebarOpen && <img src="/images/logo.png" alt="logo" width={80} height={80} />}
          </div>

          <nav>
            <Link href="/admin/dashboard" className="sidebar-link">
              <FiHome className="icon" />
              <span className="text">Dashboard</span>
            </Link>

            <Link href="/" className="sidebar-link">
              <FiUserPlus className="icon" />
              <span className="text">Add Student</span>
            </Link>

            <div className="sidebar-parent" onClick={() => setWebsiteOpen(!websiteOpen)}>
              <TfiWorld className="icon" />
              <span className="text">Website Data {sidebarOpen && <span className="arrow">{websiteOpen ? "▲" : "▼"}</span>}</span>
              
            </div>

            {websiteOpen && (

              <div className="sidebar-sub">
                  <Link href= "/admin/dashboard/websiteData" className="sidebar-link sub">
                  <TfiWorld className="icon" /><span className="text">Website Data</span>
                  </Link>

                <div className="sidebar-link sub" onClick={openAddCourse}>
                  <BiBookAdd className="icon" /> <span className="text">Add Course</span>
                </div>

                <div  className="sidebar-link sub" onClick={openAddGallery}>
                  <GrGallery className="icon" /> <span className="text">Add Gallery</span>
                </div>
                <div className="sidebar-link sub" onClick={openAddServices}>
                  <FaServer className="icon" /> <span className="text">Add Services</span>
                </div>
                <div className="sidebar-link sub" onClick={openAddTestimonial}>
                  <MdOutlineReviews className="icon" /> <span className="text">Add Testimonial</span>
                </div>
                <div className="sidebar-link sub" onClick={openAddProjectDomain}>
                  <GrDomain className="icon" /> <span className="text">Add Project Domain</span>
                </div>
                <div className="sidebar-link sub" onClick={openAddProject}>
                  <FaDiagramProject className="icon" /> <span className="text">Add Project</span>
                </div>
                <div className="sidebar-link sub" onClick={openAddContact}>
                  <MdContactPhone className="icon" /> <span className="text">Add Contact</span>
                </div>
                <Link href="/" className="sidebar-link sub">
                  <PiStudentBold className="icon" /> <span className="text">Add Career</span>
                </Link>
                <Link href="/" className="sidebar-link sub">
                  <ImProfile className="icon" /> <span className="text">Add Portfolio</span>
                </Link>
              </div>
            )}

            <Link href="/" className="sidebar-link">
              <RiPaypalLine className="icon" /> <span className="text">Payment</span>
            </Link>
            <Link href="/" className="sidebar-link">
              <PiStudentBold className="icon" /> <span className="text">Completed Students</span>
            </Link>
            <Link href="/" className="sidebar-link">
              <FiInfo className="icon" /> <span className="text">Staff</span>
            </Link>
            <Link href="/" className="sidebar-link">
              <CiDatabase className="icon" /> <span className="text">Attendance</span>
            </Link>
            <Link href="/" className="sidebar-link">
              <MdOutlineWorkOutline className="icon" /> <span className="text">Work Updation</span>
            </Link>
            <Link href="/" className="sidebar-link">
              <FaDatabase className="icon" /> <span className="text">Student Data</span>
            </Link>
          </nav>
        </div>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            <FiLogOut className="icon" />
            <span className="text">Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
}
