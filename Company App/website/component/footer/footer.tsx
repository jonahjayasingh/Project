"use client";

import "./footer.css";
import { FaFacebookF, FaTwitter, FaLinkedinIn, FaInstagram, FaMapMarkerAlt, FaPhone, FaEnvelope, FaWhatsapp } from "react-icons/fa";
import Link from "next/link";
import gaafs from "@/public/images/gaafs.png";
import qva from "@/public/images/qva.png";
import iso from "@/public/images/iso.png";
import Image from "next/image";
import { useEffect } from "react";
import { FaMessage } from "react-icons/fa6";
import { AiFillMessage } from "react-icons/ai";

type Contact = {
  id: number;
  phone1: string;
  phone2: string;
  email: string;
  map: string;
  X_link: string;
  address: string;
  youtube_link : string;
  instagram_link: string;
  linkedin_link: string;
  facebook_link: string;
}
export default function Footer({ contact }: { contact: Contact }) {

  useEffect(() => {
    const messageBtn = document.querySelector(".floating-message-btn");
    const options = document.querySelector(".floating-options");
    const widget = document.querySelector(".floating-widget");

    messageBtn?.addEventListener("click", () => {
      options?.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!widget?.contains(e.target as Node)) {
        options?.classList.remove("show");
      }
    });
    console.log(contact);
  }, []);

  return (
    <>
      <footer className="footer">
        <div className="footer-top">
          <div className="footer-container">
            <div className="footer-section">
              <div className="footer-brand">
                <h2>Alric Infotech Pvt Ltd.</h2>
                <p>Advancing tech skills through high-quality, accessible education.</p>

                <div className="social-links">
                  <Link href={`${contact.facebook_link}`} aria-label="Facebook"><FaFacebookF /></Link>
                  <Link href={`${contact.X_link}`} aria-label="Twitter"><FaTwitter /></Link>
                  <Link href={`${contact.linkedin_link}`} aria-label="LinkedIn"><FaLinkedinIn /></Link>
                  <Link href={`${contact.instagram_link}`} aria-label="Instagram"><FaInstagram /></Link>
                </div>

                <div className="certifications">
                  <Image src={gaafs} alt="gaafs" width={60} height={60} />
                  <Image src={qva} alt="qva" width={60} height={60} />
                  <Image src={iso} alt="iso" width={60} height={60} />
                </div>
              </div>
            </div>

            <div className="footer-section">
              <h3>Quick Links</h3>
              <div className="footer-links">
                <Link href="/">Home</Link>
                <Link href="/#about">About</Link>
                <Link href="/services">Services</Link>
                <Link href="/portfolio">Portfolio</Link>
                <Link href="/#trainings">Internship Trainings</Link>
                <Link href="/#placement">Placements</Link>
                <Link href="/">Verify Certificate</Link>
                <Link href="/services#projects">Project</Link>
                <Link href="/#gallery">Gallery</Link>
                <Link href="/">Contact</Link>
              </div>
            </div>

            <div className="footer-section">
              <h3>Contact Us</h3>
              <div className="contact-info">
                <div className="contact-item">
                  <FaMapMarkerAlt className="contact-icon" />
                  <p>{contact.address}</p>
                </div>
                <div className="contact-item">
                  <FaPhone className="contact-icon" />
                  <p>{contact.phone1}</p>
                </div>
                <div className="contact-item">
                  <FaPhone className="contact-icon" />
                  <p>{contact.phone2}</p>
                </div>
                <div className="contact-item">
                  <FaEnvelope className="contact-icon" />
                  <p>{contact.email}</p>
                </div>
              </div>

              <div
                className="map-container"
                style={{ width: "100%", height: "400px" }}
                dangerouslySetInnerHTML={{ __html: contact.map }}
              />

            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-container">
            <p>&copy; 2025 Alric Infotech Pvt Ltd. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Floating WhatsApp */}
      <a
        href="https://wa.me/911234567890?text=Hi, I'm interested!"
        target="_blank"
        className="floating-whatsapp"
        aria-label="WhatsApp Chat"
      >
        <FaWhatsapp className="floating-whatsapp-icon" />
      </a>

      {/* Floating Message widget */}
      <div className="floating-widget">
        <button className="floating-message-btn" aria-label="Message Options">
          <AiFillMessage className="floating-message-icon" />
        </button>

        <div className="floating-options">
          <a href="tel:+911234567890">📞 Call</a>
          <a href="mailto:info@alricinfotech.com">📧 Email</a>
          <a href="https://wa.me/911234567890" target="_blank">💬 WhatsApp</a>
        </div>
      </div>
    </>
  );
}
