"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { useRefresh } from "@/component/RefreshContext";
import "./websiteData.css";

import AddContact from "@/component/websitedata/AddContact/AddContact";
import AddGallery from "@/component/websitedata/AddGallery/AddGallery";
import AddCourse from "@/component/websitedata/AddCourse/AddCourse";
import AddTestimonial from "@/component/websitedata/AddTestimonial/AddTestimonial";

export default function WebsiteData() {
  const [websiteData, setWebsiteData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("contact");
  const sectionRef = useRef<HTMLDivElement>(null);
  const refresh = useRefresh();

  // CONTACT
  const [showContactModal, setShowContactModal] = useState(false);
  const [selectedContact, setSelectedContact] = useState<any>(null);

  // GALLERY
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const [selectedGallery, setSelectedGallery] = useState<any>(null);

  // COURSES
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<any>(null);

  const [showTestimonialModal, setShowTestimonialModal] = useState(false);
  const [selectedTestimonial, setSelectedTestimonial] = useState<any>(null);

  const fetchWebsiteData = async () => {
    const res = await fetch("/api/dashboard/websiteData");
    const body = await res.json();
    setWebsiteData(body);
  };

  useEffect(() => {
    fetchWebsiteData();
  }, [refresh]);

  useEffect(() => {
    if (sectionRef.current) {
      gsap.fromTo(
        sectionRef.current,
        { opacity: 0, y: 35 },
        { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }
      );
    }
  }, [activeTab, websiteData]);

  const handleDelete = async (id: number, type: string) => {
    const data = new FormData();
    data.append("id", String(id));
    await fetch(`/api/dashboard/${type}`, {
      method: "DELETE",
      body: data,
    });

    fetchWebsiteData();
  };

  if (!websiteData) return <p className="loading">Loading website data...</p>;

const renderAutoFields = (item: any) =>
  Object.entries(item).map(([k, v]) => {
    console.log(k,v);
    
    if (k === "image" || k === "id" || k === "userId") return null;

    return (
      <p key={k}>
        <strong>{k.replace(/_/g, " ")}:</strong> {String(v)}
      </p>
    );
  });


  return (
    <div className="container">
      <h1 className="heading">Website Data</h1>

      {/* TABS */}
      <div className="tabs">
        {["contact", "courses", "gallery", "placements", "domains", "projects"].map((tab) => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? "tab-active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* CONTENT SECTION */}
      <div ref={sectionRef}>
        {/* CONTACT TAB */}
        {activeTab === "contact" && websiteData?.contact && (
          <div className="card">
            <div className="top-actions">
              <button
                className="btn-action"
                onClick={() => {  
                  setSelectedContact(websiteData.contact);
                  setShowContactModal(true);
                }}
              >
                Edit
              </button>
            </div>
            {Object.entries(websiteData.contact).map(([k, v]) =>
              k !== "map" && k !== "id" && k !== "userId" ? (
                <p key={k}>
                  <strong>{k.replace(/_/g, " ")}:</strong>{" "}
                  {typeof v === "string" && v.startsWith("http") ? (
                    <a href={v} target="_blank"> Click Me </a>
                  ) : (
                    String(v)
                  )}
                </p>
              ) : null
            )}



            <div className="map" dangerouslySetInnerHTML={{ __html: websiteData.contact.map }} />
          </div>
        )}

        {/* AUTO-RENDER TABS (COURSES, GALLERY, etc.) */}
        {[
          { key: "courses", type: "courses" },
          { key: "gallerys", type: "gallery" },
          { key: "placements", type: "placements" },
          { key: "projectDomains", type: "domains" },
          { key: "projects", type: "projects" },
        ].map(({ key, type }) =>
          activeTab === type ? (
            websiteData?.[key]?.length > 0 ? (
              <div className="grid" key={type}>
                {websiteData[key].map((item: any) => (
                  <div key={item.id} className="card">
                    {item.image && (
                      <img
                        src={`http://localhost:3000/${type}/${item.image}`}
                        alt={item.name || "item"}
                        className="gallery-img"
                      />
                    )}

                    {renderAutoFields(item)}

                    <div className="card-actions">
                      {type === "gallery" ? (
                        <button
                          className="btn-action"
                          onClick={() => {
                            setSelectedGallery(item);
                            setShowGalleryModal(true);
                          }}
                        >
                          Edit
                        </button>
                      ) : type === "courses" ? (
                        <button
                          className="btn-action"
                          onClick={() => {
                            setSelectedCourse(item);
                            setShowCourseModal(true);
                          }}
                        >
                          Edit
                        </button>
                      ) : type ==="placements"?(
                          <button
                          className="btn-action"
                          onClick={() => {
                            setSelectedTestimonial(item);
                            setShowTestimonialModal(true);
                          }}
                        >
                          Edit
                        </button>
                      ): (
                        <button className="btn-action">Edit</button>
                      )}

                      <button
                        className="btn-action btn-delete"
                        onClick={() => handleDelete(item.id, type)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p key={type} className="msg">No data available</p>
            )
          ) : null
        )}
      </div>

      {/* CONTACT MODAL */}
      {showContactModal && (
        <div className="modal-overlay" onClick={() => setShowContactModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <AddContact
              contact={selectedContact}
              onClose={() => {
                setShowContactModal(false);
                fetchWebsiteData();
              }}
            />
          </div>
        </div>
      )}

      {/* GALLERY MODAL */}
      {showGalleryModal && (
        <div className="modal-overlay" onClick={() => setShowGalleryModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <AddGallery
              gallery={selectedGallery}
              onClose={() => {
                setShowGalleryModal(false);
                fetchWebsiteData();
              }}
            />
          </div>
        </div>
      )}

      {/* COURSE MODAL */}
      {showCourseModal && (
        <div className="modal-overlay" onClick={() => setShowCourseModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <AddCourse
              course={selectedCourse}
              onClose={() => {
                setShowCourseModal(false);
                fetchWebsiteData();
              }}
            />
          </div>
        </div>
      )}

      {/* Testimonial MODAL */}
      {showTestimonialModal && (
        <div className="modal-overlay" onClick={() => setShowTestimonialModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <AddTestimonial
              testimonial={selectedTestimonial}
              onClose={() => {
                setShowTestimonialModal(false);
                fetchWebsiteData();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
