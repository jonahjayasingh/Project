"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Navbar from "@/component/Navbar/Navbar";
import Footer from "@/component/footer/footer";
import Image from "next/image";
import "./style.css";
import { FaWhatsapp } from "react-icons/fa";
import Lenis from "lenis";

// Import images
import iotImage from "@/public/images/hs1.jpeg";
import webImage from "@/public/images/hs2.jpeg";
import aiImage from "@/public/images/hs3.jpeg";

export default function Portfolio() {
    const mainRef = useRef<HTMLDivElement>(null);
    const [activeFilter, setActiveFilter] = useState("All Projects");
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const [isPaused, setIsPaused] = useState(false);
    const [currentSlide, setCurrentSlide] = useState(0);
    const observerRef = useRef<IntersectionObserver | null>(null);

    const slides = [
        { image: iotImage, title: "Our Portfolio", text: "Explore our diverse range of successful projects across multiple domains", button: "View Projects", alt: "Portfolio showcase" },
        { image: webImage, title: "Innovation & Excellence", text: "Delivering cutting-edge solutions that transform businesses and drive growth", button: "Learn More", alt: "Innovation showcase" },
        { image: aiImage, title: "Proven Success", text: "Trusted by clients worldwide for quality, reliability, and exceptional results", button: "Get Started", alt: "Success stories" }
    ];

    const projects = [
        { id: 1, title: "Smart Home Automation", description: "IoT-based home automation system with real-time monitoring and control", category: "IoT", image: iotImage },
        { id: 2, title: "E-Commerce Platform", description: "Full-featured online store with payment integration and inventory management", category: "Website", image: webImage },
        { id: 3, title: "AI Chatbot Assistant", description: "Intelligent chatbot powered by machine learning for customer support", category: "AI & ML", image: aiImage },
        { id: 4, title: "Climate Data Analysis", description: "Research project analyzing climate patterns using big data analytics", category: "Research", image: aiImage },
        { id: 5, title: "Industrial IoT Monitoring", description: "Real-time monitoring system for industrial equipment and sensors", category: "IoT", image: iotImage },
        { id: 6, title: "Corporate Website", description: "Modern responsive website with SEO optimization and CMS integration", category: "Website", image: webImage },
        { id: 7, title: "Predictive Analytics Engine", description: "Machine learning model for sales forecasting and trend prediction", category: "AI & ML", image: aiImage },
        { id: 8, title: "Healthcare Data Study", description: "Research on patient data patterns for improved treatment outcomes", category: "Research", image: aiImage },
        { id: 9, title: "Smart Agriculture System", description: "IoT sensors for soil monitoring and automated irrigation control", category: "IoT", image: iotImage },
        { id: 10, title: "Portfolio Website", description: "Creative portfolio showcase with smooth animations and modern design", category: "Website", image: webImage },
        { id: 11, title: "Image Recognition System", description: "Deep learning model for object detection and classification", category: "AI & ML", image: aiImage },
        { id: 12, title: "Urban Planning Research", description: "Data-driven research on sustainable urban development strategies", category: "Research", image: aiImage },
    ];

    const categories = ["All Projects", "Website", "Research", "AI & ML", "IoT"];
    const filteredProjects = activeFilter === "All Projects"
        ? projects
        : projects.filter((project) => project.category === activeFilter);

    /* Initialize Lenis for smooth scrolling */
    useEffect(() => {
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

        return () => lenis.destroy();
    }, []);

    /* IntersectionObserver for animations */
    useEffect(() => {
        observerRef.current = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("animate-in");
                    observerRef.current?.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll(".project-card").forEach((el) => observerRef.current?.observe(el));
        document.querySelectorAll(".filter-btn").forEach((el) => observerRef.current?.observe(el));
        document.querySelector(".portfolio-filter-section") && observerRef.current?.observe(document.querySelector(".portfolio-filter-section")!);

        return () => observerRef.current?.disconnect();
    }, []);

    /* RE-RUN animation observer whenever filtering changes */
    useEffect(() => {
        document.querySelectorAll(".project-card").forEach((el) => {
            el.classList.remove("animate-in");
            observerRef.current?.observe(el);
        });
    }, [filteredProjects]);

    /* Carousel functionality */
    const nextSlide = useCallback(() => {
        setCurrentSlide((i) => (i + 1) % slides.length);
    }, []);
    const prevSlide = useCallback(() => {
        setCurrentSlide((i) => (i - 1 + slides.length) % slides.length);
    }, []);
    const togglePause = () => setIsPaused((s) => !s);

    useEffect(() => {
  if (!isPaused) {
    timerRef.current = setInterval(nextSlide, 5000);
  }

  return () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null; // <- set to null, but DO NOT *return* null
    }
  };
}, [isPaused, nextSlide]);


    const handleWhatsAppEnquiry = (projectTitle: string) => {
        const message = `Hi! I'm interested in the ${projectTitle} project. Can you provide more details?`;
        const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
        window.open(whatsappUrl, "_blank");
    };

    return (
        <div className="portfolio-page" ref={mainRef}>
            <Navbar />

            {/* Hero Carousel Section */}
            <section className="portfolio-hero">
                {slides.map((s, i) => (
                    <div key={i} className={`carousel-slide ${i === currentSlide ? "active" : ""}`}>
                        <Image src={s.image} alt={s.alt} fill priority={i === 0} style={{ objectFit: "cover" }} />
                        <div className="slide-overlay" />
                    </div>
                ))}

                <div className="carousel-content">
                    <h1 className="carousel-title">{slides[currentSlide].title}</h1>
                    <p className="carousel-text">{slides[currentSlide].text}</p>
                    <button className="carousel-btn">{slides[currentSlide].button}</button>
                </div>

                <div className="carousel-indicators">
                    {slides.map((_, i) => (
                        <button
                            key={i}
                            className={`carousel-indicator ${i === currentSlide ? "active" : ""}`}
                            onClick={() => setCurrentSlide(i)}
                        />
                    ))}
                </div>
            </section>

            {/* Filter Section */}
            <section className="portfolio-filter-section">
                <div className="portfolio-container">
                    <h2 className="featured-title">Featured Projects</h2>
                    <div className="filter-buttons">
                        {categories.map((category) => (
                            <button
                                key={category}
                                className={`filter-btn ${activeFilter === category ? "active" : ""}`}
                                onClick={() => setActiveFilter(category)}
                            >
                                {category}
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* Projects Grid */}
            <section className="portfolio-projects-section">
                <div className="portfolio-container">
                    <div className="projects-grid">
                        {filteredProjects.map((project) => (
                            <div key={project.id} className="project-card">
                                <div className="project-image-wrapper">
                                    <Image
                                        src={project.image}
                                        alt={project.title}
                                        width={400}
                                        height={250}
                                        className="project-image"
                                    />
                                    <div className="project-overlay">
                                        <span className="project-category">{project.category}</span>
                                    </div>
                                </div>
                                <div className="project-content">
                                    <h3 className="project-title">{project.title}</h3>
                                    <p className="project-description">{project.description}</p>
                                    <button className="enquire-btn" onClick={() => handleWhatsAppEnquiry(project.title)}>
                                        <FaWhatsapp /> Enquire Now
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <Footer contact={{} as any} />
        </div>
    );
}
