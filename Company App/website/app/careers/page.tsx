"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Navbar from "@/component/Navbar/Navbar";
import Footer from "@/component/footer/footer";
import Image from "next/image";
import "./style.css";
import { FaTimes, FaWhatsapp, FaRocket, FaGraduationCap, FaUsers, FaTrophy, FaBalanceScale, FaGift, FaCheckCircle, FaMapMarkerAlt, FaClock, FaBriefcase, FaPaperPlane } from "react-icons/fa";
import Lenis from "lenis";

// Import images
import hs1 from "@/public/images/hs1.jpeg";
import hs2 from "@/public/images/hs2.jpeg";
import hs3 from "@/public/images/hs3.jpeg";

if (typeof window !== "undefined") gsap.registerPlugin(ScrollTrigger);

export default function Careers() {
    const mainRef = useRef<HTMLDivElement>(null);
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const [currentSlide, setCurrentSlide] = useState(0);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedJob, setSelectedJob] = useState<string>("");
    const [formData, setFormData] = useState({
        fullName: "",
        phone: "",
        email: "",
        resume: null as File | null,
        coverLetter: ""
    });

    const slides = [
        { image: hs1, title: "Build Your Career With Us", text: "Join our team of innovators and help shape the future of technology", button: "View Open Positions", alt: "Career opportunities" },
        { image: hs2, title: "Grow With Innovation", text: "Work on cutting-edge projects that make a real impact in the industry", button: "Explore Roles", alt: "Innovation at work" },
        { image: hs3, title: "Join Our Team", text: "Be part of a collaborative culture that values creativity and excellence", button: "Apply Now", alt: "Team collaboration" }
    ];

    const benefits = [
        {
            icon: <FaRocket />,
            title: "Innovative Projects",
            description: "Work on cutting-edge technologies and challenging projects that make a real impact."
        },
        {
            icon: <FaGraduationCap />,
            title: "Continuous Learning",
            description: "Access to training programs, workshops, and certifications to enhance your skills."
        },
        {
            icon: <FaUsers />,
            title: "Collaborative Culture",
            description: "Join a supportive team that values collaboration, creativity, and diverse perspectives."
        },
        {
            icon: <FaTrophy />,
            title: "Career Growth",
            description: "Clear career progression paths and opportunities for advancement within the company."
        },
        {
            icon: <FaBalanceScale />,
            title: "Work-Life Balance",
            description: "Flexible work arrangements and policies that support your personal and professional life."
        },
        {
            icon: <FaGift />,
            title: "Competitive Benefits",
            description: "Comprehensive health insurance, retirement plans, and performance-based bonuses."
        }
    ];

    const openPositions = [
        {
            title: "Senior Full Stack Developer",
            location: "Bangalore, India",
            type: "Full-time",
            experience: "5+ years",
            description: "We're looking for an experienced full stack developer to join our engineering team.",
            responsibilities: [
                "Design and develop scalable web applications",
                "Collaborate with cross-functional teams",
                "Mentor junior developers",
                "Implement best practices and coding standards"
            ]
        },
        {
            title: "UI/UX Designer",
            location: "Remote",
            type: "Full-time",
            experience: "3+ years",
            description: "Join our design team to create beautiful and intuitive user experiences.",
            responsibilities: [
                "Create user-centered designs for web and mobile applications",
                "Conduct user research and usability testing",
                "Develop wireframes, prototypes, and design systems",
                "Collaborate with developers to ensure design implementation"
            ]
        },
        {
            title: "DevOps Engineer",
            location: "Hyderabad, India",
            type: "Full-time",
            experience: "4+ years",
            description: "Help us build and maintain robust infrastructure and deployment pipelines.",
            responsibilities: [
                "Design and implement CI/CD pipelines",
                "Manage cloud infrastructure and services",
                "Monitor system performance and reliability",
                "Automate deployment and scaling processes"
            ]
        },
        {
            title: "Data Scientist",
            location: "Bangalore, India",
            type: "Full-time",
            experience: "3+ years",
            description: "Apply machine learning and data analysis to solve complex business problems.",
            responsibilities: [
                "Develop and deploy machine learning models",
                "Analyze large datasets to extract insights",
                "Collaborate with stakeholders to define requirements",
                "Present findings and recommendations"
            ]
        }
    ];

    const hiringProcess = [
        {
            step: "1",
            title: "Application Review",
            description: "We carefully review each application to find the best match for our team."
        },
        {
            step: "2",
            title: "Initial Screening",
            description: "A quick phone call to discuss your background and career goals."
        },
        {
            step: "3",
            title: "Technical Assessment",
            description: "A skills-based assessment relevant to the position you're applying for."
        },
        {
            step: "4",
            title: "Team Interviews",
            description: "Meet with team members and managers to assess cultural fit."
        },
        {
            step: "5",
            title: "Offer",
            description: "Receive an offer and welcome to the Alric Infotech family!"
        }
    ];

    // GSAP & Lenis Integration
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

        // Integrate Lenis with GSAP ScrollTrigger
        lenis.on('scroll', ScrollTrigger.update);

        gsap.ticker.add((time) => {
            lenis.raf(time * 1000);
        });

        gsap.ticker.lagSmoothing(0);

        const ctx = gsap.context(() => {
            // Section fade-in animations
            gsap.fromTo(
                ".careers-section",
                { opacity: 0, y: 40 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    scrollTrigger: {
                        trigger: ".careers-section",
                        start: "top 85%",
                        once: true
                    }
                }
            );

            // Benefits cards animation
            gsap.fromTo(
                ".benefit-card",
                {
                    opacity: 0,
                    y: 60,
                    scale: 0.95
                },
                {
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    duration: 0.6,
                    stagger: 0.1,
                    ease: "back.out(1.2)",
                    scrollTrigger: {
                        trigger: ".benefits-grid",
                        start: "top 75%",
                        once: true
                    }
                }
            );

            // Job cards animation
            gsap.fromTo(
                ".job-card",
                {
                    opacity: 0,
                    x: -40
                },
                {
                    opacity: 1,
                    x: 0,
                    duration: 0.7,
                    stagger: 0.15,
                    scrollTrigger: {
                        trigger: ".jobs-list",
                        start: "top 75%",
                        once: true
                    }
                }
            );

            // Process steps animation
            gsap.fromTo(
                ".process-step",
                {
                    opacity: 0,
                    y: 40,
                    scale: 0.9
                },
                {
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    duration: 0.6,
                    stagger: 0.1,
                    ease: "back.out(1.3)",
                    scrollTrigger: {
                        trigger: ".process-grid",
                        start: "top 75%",
                        once: true
                    }
                }
            );
        }, mainRef);

        // Cleanup
        return () => {
            lenis.destroy();
            gsap.ticker.remove((time) => {
                lenis.raf(time * 1000);
            });
            ctx.revert();
            ScrollTrigger.getAll().forEach((t) => t.kill());
        };
    }, []);

    // Carousel functionality
    const nextSlide = useCallback(() => setCurrentSlide((i) => (i + 1) % slides.length), [slides.length]);

    useEffect(() => {
        timerRef.current = setInterval(nextSlide, 5000);

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, [nextSlide]);

    // Modal and form handlers
    const openModal = (jobTitle: string) => {
        setSelectedJob(jobTitle);
        setIsModalOpen(true);
        document.body.style.overflow = 'hidden';
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedJob("");
        setFormData({
            fullName: "",
            phone: "",
            email: "",
            resume: null,
            coverLetter: ""
        });
        document.body.style.overflow = 'unset';
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFormData(prev => ({ ...prev, resume: e.target.files![0] }));
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Create WhatsApp message
        const message = `Job Application for: ${selectedJob}

Full Name: ${formData.fullName}
Phone: ${formData.phone}
Email: ${formData.email}
${formData.coverLetter ? `\nCover Letter:\n${formData.coverLetter}` : ''}

Note: Resume attached separately`;

        const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
        window.open(whatsappUrl, '_blank');

        closeModal();
    };

    return (
        <div className="careers-page" ref={mainRef}>
            <Navbar />

            {/* Hero Carousel Section */}
            <section className="careers-hero">
                {slides.map((s, i) => (
                    <div key={i} className={`carousel-slide ${i === currentSlide ? "active" : ""}`}>
                        <Image src={s.image} alt={s.alt} fill priority={i === 0} style={{ objectFit: 'cover' }} />
                        <div className="slide-overlay" />
                    </div>
                ))}

                <div className="carousel-content">
                    <h2 className="carousel-title">{slides[currentSlide].title}</h2>
                    <p className="carousel-text">{slides[currentSlide].text}</p>
                    <a href="#open-positions" className="carousel-btn">{slides[currentSlide].button}</a>
                </div>

                <div className="carousel-indicators">
                    {slides.map((_, i) => (
                        <button key={i} className={`carousel-indicator ${i === currentSlide ? "active" : ""}`} onClick={() => setCurrentSlide(i)} />
                    ))}
                </div>
            </section>

            {/* Why Join Section */}
            <section className="careers-section why-join">
                <div className="careers-container">
                    <h2 className="section-title">Why Join Alric Infotech?</h2>
                    <p className="section-subtitle">Discover the benefits of being part of our innovative team</p>
                    <div className="benefits-grid">
                        {benefits.map((benefit, index) => (
                            <div key={index} className="benefit-card">
                                <div className="benefit-icon">{benefit.icon}</div>
                                <h3>{benefit.title}</h3>
                                <p>{benefit.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Open Positions Section */}
            <section className="careers-section open-positions" id="open-positions">
                <div className="careers-container">
                    <h2 className="section-title">Open Positions</h2>
                    <p className="section-subtitle">Find your perfect role and join our growing team</p>
                    <div className="jobs-list">
                        {openPositions.map((job, index) => (
                            <div key={index} className="job-card">
                                <div className="job-header">
                                    <h3>{job.title}</h3>
                                    <div className="job-meta">
                                        <span className="job-location"><FaMapMarkerAlt /> {job.location}</span>
                                        <span className="job-type"><FaClock /> {job.type}</span>
                                        <span className="job-experience"><FaBriefcase /> {job.experience}</span>
                                    </div>
                                </div>
                                <p className="job-description">{job.description}</p>
                                <div className="job-details">
                                    <div className="job-section">
                                        <h4>Key Responsibilities:</h4>
                                        <ul>
                                            {job.responsibilities.map((resp, i) => (
                                                <li key={i}><FaCheckCircle /> {resp}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                                <button className="apply-btn" onClick={() => openModal(job.title)}>
                                    <FaPaperPlane /> Apply Now
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Hiring Process Section */}
            <section className="careers-section hiring-process">
                <div className="careers-container">
                    <h2 className="section-title">Our Hiring Process</h2>
                    <p className="section-subtitle">A transparent and straightforward journey to joining our team</p>
                    <div className="process-grid">
                        {hiringProcess.map((process, index) => (
                            <div key={index} className="process-step">
                                <div className="process-number">{process.step}</div>
                                <h3>{process.title}</h3>
                                <p>{process.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="careers-section cta-section">
                <div className="careers-container">
                    <div className="cta-content">
                        <h2>Ready to Join Our Team?</h2>
                        <p>Take the first step towards an exciting career with Alric Infotech</p>
                        <a href="#open-positions" className="cta-button">View Open Positions</a>
                    </div>
                </div>
            </section>

            {/* Application Modal */}
            {isModalOpen && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={closeModal}>
                            <FaTimes />
                        </button>

                        <h2 className="modal-title">Apply for {selectedJob}</h2>
                        <p className="modal-subtitle">Fill in your details to submit your application</p>

                        <form onSubmit={handleSubmit} className="application-form">
                            <div className="form-group">
                                <label htmlFor="fullName">Full Name *</label>
                                <input
                                    type="text"
                                    id="fullName"
                                    name="fullName"
                                    value={formData.fullName}
                                    onChange={handleInputChange}
                                    required
                                    placeholder="Enter your full name"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="phone">Phone Number *</label>
                                <input
                                    type="tel"
                                    id="phone"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleInputChange}
                                    required
                                    placeholder="Enter your phone number"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="email">Email Address *</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    required
                                    placeholder="Enter your email address"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="resume">Resume *</label>
                                <input
                                    type="file"
                                    id="resume"
                                    name="resume"
                                    onChange={handleFileChange}
                                    required
                                    accept=".pdf,.doc,.docx"
                                    className="file-input"
                                />
                                {formData.resume && (
                                    <p className="file-name">Selected: {formData.resume.name}</p>
                                )}
                            </div>

                            <div className="form-group">
                                <label htmlFor="coverLetter">Cover Letter (Optional)</label>
                                <textarea
                                    id="coverLetter"
                                    name="coverLetter"
                                    value={formData.coverLetter}
                                    onChange={handleInputChange}
                                    rows={5}
                                    placeholder="Tell us why you're a great fit for this role..."
                                />
                            </div>

                            <button type="submit" className="submit-btn">
                                <FaPaperPlane /> Submit Application
                            </button>
                        </form>
                    </div>
                </div>
            )}

            <Footer contact={{} as any} />
        </div>
    );
}
