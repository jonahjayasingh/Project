"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import Navbar from "@/component/Navbar/Navbar";
import Footer from "@/component/footer/footer";
import "./home.css";
import Image from "next/image";
import Link from "next/link";
import Lenis from "lenis";

import hs1 from "@/public/images/hs1.jpeg";
import hs2 from "@/public/images/hs2.jpeg";
import hs3 from "@/public/images/hs3.jpeg";
import {
  FaClock,
  FaUser,
  FaChalkboardTeacher,
  FaLaptopCode,
  FaBriefcase,
  FaGraduationCap,
  FaAward,
  FaRocket,
  FaUsers,
  FaGlobe,
  FaBuilding,
  FaTimes,
  FaChevronLeft,
  FaChevronRight
} from "react-icons/fa";

type Courses = {
  id: number;
  course_name: string;
  image: string;
  duration: string;
  course_difficulty: string;
  Price: number;
  description: string;
}

type Gallery = {
  id: number;
  image: string;
  title: string;
}

type Placements = {
  id: number;
  name: string;
  job_title: string;
  company: string;
  image: string;
}

type Contact = {
  id: number;
  phone1: string;
  phone2: string;
  email: string;
  map: string;
  X_link: string;
  address: string;
  youtube_link: string;
  instagram_link: string;
  linkedin_link: string;
  facebook_link: string;
}

export default function Home() {
  const mainRef = useRef<HTMLDivElement>(null);
  const carouselRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);

  const [courses, setCourses] = useState<Courses[]>([]);
  const [galleryData, setGalleryData] = useState<Gallery[]>([]);
  const [placementsData, setPlacementsData] = useState<Placements[]>([]);
  const [contact, setContact] = useState<Contact>({} as Contact);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        const response = await fetch("/api/home");
        const data = await response.json();
        setCourses(data.courses || []);
        setGalleryData(data.gallerys || []);
        setPlacementsData(data.placements || []);
        setContact(data.contact || {});
      } catch (error) {
        console.error("Error fetching home data:", error);
      }
    };
    fetchHomeData();
  }, []);

  const slidesData = [
    {
      image: hs1,
      title: "Empowering Students",
      text: "Learn modern skills with mentors and real-world training.",
      button: "Get Started",
      alt: "Students engaged in learning modern skills"
    },
    {
      image: hs2,
      title: "Industry Focused Training",
      text: "Become job-ready through practical, hands-on learning.",
      button: "Explore Courses",
      alt: "Industry focused training session"
    },
    {
      image: hs3,
      title: "Success Through Placement",
      text: "Join our alumni placed in companies around the world.",
      button: "View Placements",
      alt: "Successful alumni celebrating placements"
    }
  ];

  const openGalleryModal = (index: number) => {
    setSelectedImageIndex(index);
    document.body.style.overflow = 'hidden';
  };

  const closeGalleryModal = () => {
    setSelectedImageIndex(null);
    document.body.style.overflow = 'unset';
  };

  const nextGalleryImage = () => {
    if (selectedImageIndex !== null) {
      setSelectedImageIndex((selectedImageIndex + 1) % galleryData.length);
    }
  };

  const prevGalleryImage = () => {
    if (selectedImageIndex !== null) {
      setSelectedImageIndex((selectedImageIndex - 1 + galleryData.length) % galleryData.length);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (selectedImageIndex === null) return;

      if (e.key === "Escape") closeGalleryModal();
      if (e.key === "ArrowLeft") prevGalleryImage();
      if (e.key === "ArrowRight") nextGalleryImage();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedImageIndex]);

  // Intersection Observer for Scroll Animations
  useEffect(() => {
    // Initialize Lenis
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
    });

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe all animated elements
    const animatedElements = document.querySelectorAll(
      '.section:not(#hero-carousel), .feature-item, .course-card, .placement-card, .stat, .gallery-item'
    );

    animatedElements.forEach((el) => observer.observe(el));

    return () => {
      lenis.destroy();
      observer.disconnect();
    };
  }, [courses, galleryData, placementsData]);

  const showSlide = useCallback((index: number) => {
    setCurrentSlide(index);
  }, []);

  const nextSlide = useCallback(() => {
    const nextIndex = (currentSlide + 1) % slidesData.length;
    showSlide(nextIndex);
  }, [currentSlide, slidesData.length, showSlide]);

  const prevSlide = useCallback(() => {
    const prevIndex = (currentSlide - 1 + slidesData.length) % slidesData.length;
    showSlide(prevIndex);
  }, [currentSlide, slidesData.length, showSlide]);

  const goToSlide = useCallback((index: number) => {
    if (index !== currentSlide) showSlide(index);
  }, [currentSlide, showSlide]);

  const togglePause = useCallback(() => setIsPaused(!isPaused), [isPaused]);

  // Auto-slide functionality
  useEffect(() => {
    if (isPaused) {
      if (timerRef.current) clearInterval(timerRef.current);
    } else {
      timerRef.current = setInterval(() => nextSlide(), 5000);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPaused, nextSlide]);

  // Keyboard navigation for carousel
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (selectedImageIndex !== null) return;

      if (e.key === "ArrowLeft") prevSlide();
      if (e.key === "ArrowRight") nextSlide();
      if (e.key === " ") { e.preventDefault(); togglePause(); }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [prevSlide, nextSlide, togglePause, selectedImageIndex]);

  return (
    <div className="home no-scrollbar" ref={mainRef}>
      <Navbar />

      {/* ================= HERO CAROUSEL ================= */}
      <section className="homesection hero" id="hero-carousel" aria-label="Hero carousel" role="region" ref={carouselRef}>
        <div className="carousel-container">
          {slidesData.map((slide, index) => (
            <div
              key={index}
              className={`carousel-slide ${index === currentSlide ? 'active' : ''}`}
              aria-hidden={index !== currentSlide}
              style={{
                opacity: index === currentSlide ? 1 : 0,
                zIndex: index === currentSlide ? 2 : 1
              }}
            >
              <Image 
                src={slide.image} 
                alt={slide.alt} 
                priority={index === 0} 
                placeholder="blur" 
                sizes="100vw" 
                style={{ width: "100%", height: "100%", objectFit: "cover" }} 
              />
              <div className="slide-overlay"></div>
            </div>
          ))}

          <div className="carousel-content">
            <h1 className="carousel-title">{slidesData[currentSlide].title}</h1>
            <p className="carousel-text">{slidesData[currentSlide].text}</p>
            <button className="carousel-btn">{slidesData[currentSlide].button}</button>
          </div>

          <div className="carousel-indicators">
            {slidesData.map((_, index) => (
              <button
                key={index}
                className={`carousel-indicator ${index === currentSlide ? 'active' : ''}`}
                onClick={() => goToSlide(index)}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ================= ABOUT SECTION ================= */}
      <section className="homesection about" id="about">
        <div className="container">
          <h2>About Us</h2>
          <div className="about-content">
            <div className="about-text">
              <h3>Transforming Education, Empowering Futures</h3>
              <p>Alric Infotech Pvt Ltd is an emerging software development & IT Training Services Company, established by the seasoned professionals in the year 2022. We deliver a wide range of IT services across various industries & continue to focus on developing innovative products, services, and solutions to assist our clients.</p>
              <p>We help our clients to accelerate their business growth by providing innovative digital solutions, unique ideas to solve complex business needs across various industries. We are dedicated to learning and understanding your business better to create a strategy to fulfill your commercial objectives.</p>
              <p>We focus on achieving strategic technology initiatives for our clients. Hence, we deliver the right program for your needs, within time and budget. Alric Infotech Pvt Ltd would like to become your long-term technology partner to grow your business.</p>
            </div>
            <div className="about-features">
              <div className="feature-item">
                <div className="home-feature-icon"><FaChalkboardTeacher /></div>
                <div className="feature-content">
                  <h4>Expert Instructors</h4>
                  <p>Learn from industry professionals with 10+ years of experience</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="home-feature-icon"><FaLaptopCode /></div>
                <div className="feature-content">
                  <h4>Hands-on Training</h4>
                  <p>Practical projects and real-world scenarios</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="home-feature-icon"><FaBriefcase /></div>
                <div className="feature-content">
                  <h4>Career Guidance</h4>
                  <p>Personalized career counseling and mentorship</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="home-feature-icon"><FaRocket /></div>
                <div className="feature-content">
                  <h4>Fast Track Learning</h4>
                  <p>Accelerated programs for quick career growth</p>
                </div>
              </div>
              <Link href="/contact" className="cta-button">Get In Touch</Link>
            </div>
          </div>
        </div>
      </section>

      {/* ================= TRAININGS SECTION ================= */}
      <section className="homesection trains" id="trainings">
        <div className="container">
          <h2>Our Trainings</h2>
          <p className="section-subtitle">Hands-on learning guided by experienced mentors and real-world projects that match current industry demands.</p>
          <div className="courses-grid">
            {courses.map((course) => (
              <div className="course-card" key={course.id}>
                <div className="course-image">
                  <Image 
                    src={`/courses/${course.image}`} 
                    alt={course.course_name} 
                    fill 
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    style={{ objectFit: 'cover' }} 
                  />
                  <div className="course-image-overlay">
                    <h3>{course.course_name}</h3>
                  </div>
                </div>
                <div className="course-content">
                  <h3>{course.course_name}</h3>
                  <p className="course-description">{course.description}</p>
                  <div className="course-meta">
                    <span className="course-duration"><FaClock className="course-icon" /> {course.duration}</span>
                    <span className="course-level"><FaUser  className="course-icon"/> {course.course_difficulty}</span>
                  </div>
                  <div className="course-price-container">
                    <div className="course-price"><span className="course-icon">₹</span>{course.Price}</div>
                  <button className="course-btn">Enroll Now</button>
                  </div>
                  
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= PLACEMENT SECTION ================= */}
      <section className="homesection placement" id="placement">
        <div className="parallax-bg"></div>
        <div className="container">
          <h2>Our Successful Placements</h2>
          <p className="section-subtitle">Meet our alumni who have secured positions at top companies worldwide through our placement support.</p>

          <div className="placement-stats">
            <div className="stat"><div className="stat-icon"><FaAward /></div><h3>95%</h3><p>Placement Rate</p></div>
            <div className="stat"><div className="stat-icon"><FaUsers /></div><h3>200+</h3><p>Hiring Partners</p></div>
            <div className="stat"><div className="stat-icon"><FaGlobe /></div><h3>50+</h3><p>Countries</p></div>
          </div>

          <div className="placements-grid">
            {placementsData.map((placement, index) => (
              <div key={placement.id} className="placement-card">
                <div className="placement-image">
                  <Image
                    src={`/placements/${placement.image}`}
                    alt={placement.name}
                    fill
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    style={{ objectFit: 'cover' }}
                  />
                  <div className="placement-overlay"></div>
                </div>
                <div className="placement-content">
                  <h3 className="placement-name">{placement.name}</h3>
                  <p className="placement-job">{placement.job_title}</p>
                  <div className="placement-company"><FaBuilding className="company-icon" /><span>{placement.company}</span></div>
                  <div className="placement-badge">Placed</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= GALLERY SECTION ================= */}
      <section className="homesection gallery" id="gallery">
        <div className="container">
          <h2>Gallery</h2>
          <p className="section-subtitle">Events, workshops, hackathons and project showcases throughout the year capturing our vibrant learning community.</p>
          <div className="gallery-grid">
            {galleryData.map((item, index) => (
              <div key={item.id} className="gallery-item" onClick={() => openGalleryModal(index)}>
                <Image
                  src={`/gallery/${item.image}`}
                  alt={item.title}
                  fill
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  style={{ objectFit: 'cover' }}
                />
                <div className="gallery-overlay"><span>{item.title}</span></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Gallery Modal */}
      {selectedImageIndex !== null && galleryData[selectedImageIndex] && (
        <div className="gallery-modal">
          <div className="gallery-modal-backdrop" onClick={closeGalleryModal}></div>
          <div className="gallery-modal-content">
            <button className="gallery-modal-close" onClick={closeGalleryModal}><FaTimes /></button>
            <button className="gallery-modal-nav gallery-modal-prev" onClick={prevGalleryImage}><FaChevronLeft /></button>
            <div className="gallery-modal-image">
              <Image 
                src={`/gallery/${galleryData[selectedImageIndex].image}`} 
                alt={galleryData[selectedImageIndex].title} 
                fill 
                style={{ objectFit: 'contain' }} 
                sizes="90vw" 
              />
            </div>
            <button className="gallery-modal-nav gallery-modal-next" onClick={nextGalleryImage}><FaChevronRight /></button>
            <div className="gallery-modal-info">
              <h3>{galleryData[selectedImageIndex].title}</h3>
              <div className="gallery-modal-counter">{selectedImageIndex + 1} / {galleryData.length}</div>
            </div>
          </div>
        </div>
      )}

      {/* ================= ACHIEVEMENTS SECTION ================= */}
      <section className="homesection achievements" id="achievements">
        <div className="container">
          <h2>Our Achievements</h2>
          <p className="section-subtitle">Award-winning results, high placement rates and a successful alumni network spanning across global companies.</p>
          <div className="achievements-list">
            <div className="achievement"><div className="achievement-icon"><FaAward /></div><h3>Best EdTech Startup 2023</h3><p>Recognized for innovation in education technology</p></div>
            <div className="achievement"><div className="achievement-icon"><FaGraduationCap /></div><h3>10,000+ Students Trained</h3><p>Successfully transformed careers worldwide</p></div>
            <div className="achievement"><div className="achievement-icon"><FaBriefcase /></div><h3>Industry Partnerships</h3><p>Collaborations with top tech companies</p></div>
          </div>
        </div>
      </section>

      <Footer contact={contact as Contact} />
    </div>
  );
}