"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { RefreshContext } from "@/component/RefreshContext";

import AdminSidebar from "./adminSidebar";
import AddCourse from "@/component/websitedata/AddCourse/AddCourse";
import AddGallery from "@/component/websitedata/AddGallery/AddGallery";
import AddServices from "@/component/websitedata/AddServices/AddServices";
import AddProjectDomain from "@/component/websitedata/AddProjecDomain/AddProjecDomain";
import AddTestimonial from "@/component/websitedata/AddTestimonial/AddTestimonial";
import AddProject from "@/component/websitedata/AddProject/AddProject";
import AddContact from "@/component/websitedata/AddContact/AddContact";

export default function AdminSidebarWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // Sidebar only on /admin pages
  if (!pathname.startsWith("/admin")) return children;

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  const [addCourseOpen, setAddCourseOpen] = useState(false);
  const [addGalleryOpen, setAddGalleryOpen] = useState(false);
  const [addServicesOpen, setAddServicesOpen] = useState(false);
  const [addTestimonialOpen, setAddTestimonialOpen] = useState(false);
  const [addProjectDomainOpen, setAddProjectDomainOpen] = useState(false);
  const [addProjectOpen, setAddProjectOpen] = useState(false);
  const [addContactOpen, setAddContactOpen] = useState(false);

  // refresh state (increases when a modal closes)
  const [refreshFlag, setRefreshFlag] = useState(0);

  // Detect mobile
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 900);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  // Lock scroll when modal is open
  useEffect(() => {
    const anyModalOpen =
      addCourseOpen ||
      addGalleryOpen ||
      addServicesOpen ||
      addTestimonialOpen ||
      addProjectDomainOpen ||
      addProjectOpen ||
      addContactOpen;

    document.body.style.overflow = anyModalOpen ? "hidden" : "auto";
  }, [
    addCourseOpen,
    addGalleryOpen,
    addServicesOpen,
    addTestimonialOpen,
    addProjectDomainOpen,
    addProjectOpen,
    addContactOpen
  ]);

  // Trigger UI refresh when modal closes (no page reload)
  useEffect(() => {
    const allClosed =
      !addCourseOpen &&
      !addGalleryOpen &&
      !addServicesOpen &&
      !addTestimonialOpen &&
      !addProjectDomainOpen &&
      !addProjectOpen &&
      !addContactOpen;

    if (allClosed) {
      setRefreshFlag(prev => prev + 1);
    }
  }, [
    addCourseOpen,
    addGalleryOpen,
    addServicesOpen,
    addTestimonialOpen,
    addProjectDomainOpen,
    addProjectOpen,
    addContactOpen
  ]);

  const contentMargin = isMobile ? "0px" : sidebarOpen ? "260px" : "80px";

  const modalOverlay = {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.45)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 2000
  } as const;

  const modalBox = {
    background: "white",
    padding: 30,
    borderRadius: 8,
    width: "600px",
    maxHeight: "90vh",
    overflowY: "auto"
  } as const;

  return (
    <>
      <AdminSidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        openAddCourse={() => setAddCourseOpen(true)}
        openAddGallery={() => setAddGalleryOpen(true)}
        openAddServices={() => setAddServicesOpen(true)}
        openAddTestimonial={() => setAddTestimonialOpen(true)}
        openAddProjectDomain={() => setAddProjectDomainOpen(true)}
        openAddProject={() => setAddProjectOpen(true)}
        openAddContact={() => setAddContactOpen(true)}
      />

      {isMobile && (
        <div
          className={`mobile-overlay ${sidebarOpen ? "show" : ""}`}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <RefreshContext.Provider value={refreshFlag}>
        <div
          className="dashboard-content"
          style={{
            marginLeft: contentMargin,
            transition: "margin-left 0.3s ease",
            padding: "40px 0",
            overflowY: "auto"
          }}
        >
          {children}
        </div>
      </RefreshContext.Provider>

      {addCourseOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddCourse onClose={() => setAddCourseOpen(false)} />
          </div>
        </div>
      )}
      {addGalleryOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddGallery onClose={() => setAddGalleryOpen(false)} />
          </div>
        </div>
      )}
      {addServicesOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddServices onClose={() => setAddServicesOpen(false)} />
          </div>
        </div>
      )}
      {addTestimonialOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddTestimonial onClose={() => setAddTestimonialOpen(false)} />
          </div>
        </div>
      )}
      {addProjectDomainOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddProjectDomain onClose={() => setAddProjectDomainOpen(false)} />
          </div>
        </div>
      )}
      {addProjectOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddProject onClose={() => setAddProjectOpen(false)} />
          </div>
        </div>
      )}
      {addContactOpen && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <AddContact onClose={() => setAddContactOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}
