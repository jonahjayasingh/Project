"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import Navbar from "@/component/Navbar/Navbar";
import Footer from "@/component/footer/footer";
import "./services.css";
import Image from "next/image";
import Lenis from "lenis";

import hs1 from "@/public/images/hs1.jpeg";
import hs2 from "@/public/images/hs2.jpeg";
import hs3 from "@/public/images/hs3.jpeg";
import {
  FaWhatsapp,
  FaCheckCircle
} from "react-icons/fa";

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

type Service = {
  id: number;
  name: string;
  description: string;
  image: string;
  key_points: string[];
}

type Project = {
  id: number;
  title: string;
  description: string;
}

type ProjectDomain = {
  id: number;
  name: string;
  description: string;
  image: string;
  project: Project[];
}

export default function Services() {
  const mainRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [services, setServices] = useState<Service[]>([]);
  const [domains, setDomains] = useState<ProjectDomain[]>([]);
  const [contact, setContact] = useState<Contact>({} as Contact);

  const servicesList = [
    {
      title: "Website Development",
      image: hs1,
      description: "We build responsive, fast-loading websites that convert visitors into loyal customers with modern design and SEO optimization.",
      features: [
        "Responsive, mobile-first design",
        "Advanced SEO optimization",
        "High-performance architecture",
        "Conversion-focused design"
      ]
    },
    {
      title: "Mobile Applications",
      image: hs2,
      description: "Native and cross-platform mobile apps with seamless user experience for iOS and Android devices.",
      features: [
        "iOS & Android development",
        "Cross-platform solutions",
        "Intuitive user interfaces",
        "App Store optimization"
      ]
    },
    {
      title: "E-Commerce Solutions",
      image: hs3,
      description: "Complete online stores with secure payment gateways, inventory management, and automated shipping integration.",
      features: [
        "Secure payment processing",
        "Smart inventory management",
        "Automated order fulfillment",
        "Customer analytics"
      ]
    },
    {
      title: "Cloud Solutions",
      image: hs1,
      description: "Scalable cloud infrastructure, migration services, and DevOps automation for modern businesses.",
      features: [
        "Cloud-native architecture",
        "Seamless migration services",
        "CI/CD automation",
        "24/7 monitoring & support"
      ]
    }
  ];

  const slides = [
    {
      image: hs1,
      title: "Digital Solutions",
      text: "Transform your business with cutting-edge technology and innovative digital solutions.",
      button: "Get Started",
      alt: "Digital solutions showcase",
    },
    {
      image: hs2,
      title: "Expert Development",
      text: "Professional development services with industry best practices and modern frameworks.",
      button: "Explore Services",
      alt: "Development team at work",
    },
    {
      image: hs3,
      title: "Business Growth",
      text: "Scale your business with reliable, secure, and high-performance applications.",
      button: "Contact Us",
      alt: "Business success story",
    },
  ];

  const howWork = [
    {
      number: 1,
      title: "Discovery",
      text: "We understand your needs and business goals to define the perfect solution.",
    },
    {
      number: 2,
      title: "Planning",
      text: "We create detailed project blueprints with clear milestones and timelines.",
    },
    {
      number: 3,
      title: "Development",
      text: "We build using modern technology stack and industry best practices.",
    },
    {
      number: 4,
      title: "Delivery",
      text: "We launch your product and provide comprehensive training and support.",
    },
  ];

  const projectDomains = [
    {
      number: 1,
      title: "Web Development",
      icon: hs1,
      text: "Fast, scalable and stunning business-focused websites that drive results.",
      projects: [
        {
          title: "Corporate Website",
          desc: "High-performance business website with SEO optimization.",
        },
        {
          title: "Portfolio Website",
          desc: "Elegant personal showcase with smooth animations.",
        },
        {
          title: "LMS Platform",
          desc: "Online courses with progress tracking and certifications.",
        },
        {
          title: "Booking Platform",
          desc: "Customer scheduling with automated confirmations.",
        },
        {
          title: "Membership Site",
          desc: "Subscription-based access with user dashboards.",
        },
        {
          title: "News Portal",
          desc: "Content management with categories and search.",
        },
        {
          title: "Marketplace",
          desc: "Multi-vendor platform with escrow payments.",
        },
        {
          title: "Analytics Dashboard",
          desc: "Real-time charts with user permissions.",
        },
        {
          title: "Property Listing",
          desc: "Real estate site with maps and CRM integration.",
        },
        {
          title: "Fundraising Platform",
          desc: "Donation campaigns with recurring payments.",
        },
      ],
    },
    {
      number: 2,
      title: "Mobile Applications",
      icon: hs2,
      text: "iOS and Android apps with seamless performance and intuitive interfaces.",
      projects: [
        {
          title: "Fitness Tracking App",
          desc: "Workout planning with wearable device integration.",
        },
        {
          title: "Food Delivery App",
          desc: "Restaurant ordering with real-time tracking.",
        },
        {
          title: "Ride-Sharing App",
          desc: "Driver matching with route navigation and payments.",
        },
        {
          title: "Event Ticket App",
          desc: "Ticket booking with QR code validation.",
        },
        {
          title: "Finance Manager",
          desc: "Expense tracking with smart budgeting insights.",
        },
        {
          title: "Healthcare App",
          desc: "Doctor booking with video consulting features.",
        },
        {
          title: "Gaming App",
          desc: "Mobile games with leaderboards and achievements.",
        },
        {
          title: "Marketplace App",
          desc: "Buy and sell with in-app chat and payments.",
        },
        {
          title: "Travel Planner",
          desc: "Trip planning with hotel booking and guides.",
        },
        {
          title: "Education App",
          desc: "Gamified learning with quizzes and progress tracking.",
        },
        {
          title: "Education App",
          desc: "Gamified learning with quizzes and progress tracking.",
        },
      ],
    },
    {
      number: 3,
      title: "UI/UX Design",
      icon: hs3,
      text: "User-centered designs that blend aesthetics with functionality.",
      projects: [
        {
          title: "Design System",
          desc: "Reusable component library with brand guidelines.",
        },
        {
          title: "SaaS Dashboard",
          desc: "High-clarity layouts for complex workflows.",
        },
        {
          title: "Mobile UI Kit",
          desc: "Comprehensive design kit for iOS and Android.",
        },
        {
          title: "Landing Page",
          desc: "High-conversion page with compelling CTAs.",
        },
        {
          title: "E-Commerce UX",
          desc: "Optimized checkout flows to increase sales.",
        },
        {
          title: "Onboarding Flow",
          desc: "Interactive first-time user experience.",
        },
        {
          title: "Brand Identity",
          desc: "Logo, typography, and visual guidelines.",
        },
        {
          title: "Self-Service Portal",
          desc: "Easy interfaces for support and billing.",
        },
        {
          title: "Knowledge Base",
          desc: "Well-structured help center with search.",
        },
        {
          title: "Micro-Interactions",
          desc: "Subtle animations for better engagement.",
        },
      ],
    },
    {
      number: 4,
      title: "Cloud Solutions",
      icon: hs1,
      text: "Secure, scalable, cost-efficient cloud infrastructure for digital transformation.",
      projects: [
        {
          title: "Serverless Web App",
          desc: "Event-driven cloud architecture for scalability.",
        },
        {
          title: "CI/CD Automation",
          desc: "Auto-deployment pipelines for fast releases.",
        },
        {
          title: "Cloud Migration",
          desc: "Moving legacy apps to cloud efficiently.",
        },
        {
          title: "Disaster Recovery",
          desc: "Backup strategy with rapid failover system.",
        },
        {
          title: "API Gateway",
          desc: "Centralized routing for distributed backends.",
        },
        {
          title: "IoT Platform",
          desc: "Smart device management with monitoring.",
        },
        {
          title: "Data Warehouse",
          desc: "Centralized storage with advanced analytics.",
        },
        {
          title: "Edge Computing",
          desc: "Low-latency processing at network edge.",
        },
        {
          title: "Cost Optimization",
          desc: "Resource allocation and usage forecasting.",
        },
        {
          title: "Cloud Security",
          desc: "Protected environments with Zero-Trust access.",
        },
      ],
    },
    {
      number: 5,
      title: "E-Commerce",
      icon: hs2,
      text: "Conversion-focused online stores with secure payments and automated logistics.",
      projects: [
        {
          title: "Online Store",
          desc: "Full-featured store with payment gateways.",
        },
        {
          title: "Dropshipping Platform",
          desc: "Automated shipping with supplier integration.",
        },
        {
          title: "B2B Wholesale",
          desc: "Bulk pricing with account management.",
        },
        {
          title: "Subscription Box",
          desc: "Recurring deliveries with custom options.",
        },
        {
          title: "Custom Checkout",
          desc: "Simplified conversion-focused checkout.",
        },
        {
          title: "Inventory Manager",
          desc: "Stock tracking with low-stock alerts.",
        },
        {
          title: "Commission System",
          desc: "Vendor settlements with sales tracking.",
        },
        {
          title: "Loyalty Program",
          desc: "Points, rewards, and customer tiers.",
        },
        {
          title: "Product Recommendations",
          desc: "AI-based suggestions for upselling.",
        },
        {
          title: "Order Fulfillment",
          desc: "Shipping automation with tracking.",
        },
      ],
    },
    {
      number: 6,
      title: "Enterprise Software",
      icon: hs3,
      text: "Powerful internal systems that automate processes and increase efficiency.",
      projects: [
        {
          title: "HR Management",
          desc: "Recruitment, payroll, and performance tracking.",
        },
        {
          title: "CRM Platform",
          desc: "Customer lifecycle with sales pipeline.",
        },
        {
          title: "ERP System",
          desc: "Centralized planning for all departments.",
        },
        {
          title: "Warehouse System",
          desc: "Smart inventory with RFID support.",
        },
        {
          title: "Project Management",
          desc: "Tasks, milestones, and team collaboration.",
        },
        {
          title: "BI Portal",
          desc: "Data visualization with KPI dashboards.",
        },
        {
          title: "Procurement Platform",
          desc: "Purchase requests with approval workflows.",
        },
        {
          title: "Support System",
          desc: "Ticketing with SLA management.",
        },
        {
          title: "Compliance Software",
          desc: "Risk tracking and policy enforcement.",
        },
        {
          title: "Document Management",
          desc: "Secure storage with version control.",
        },
      ],
    },
  ];

  /* Intersection Observer for Scroll Animations */
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
      '.section:not(.hero), .services-card, .how-card, .project-domain, .project-card'
    );

    animatedElements.forEach((el) => observer.observe(el));

    return () => {
      lenis.destroy();
      observer.disconnect();
    };
  }, []);



  /* Carousel */
  const nextSlide = useCallback(
    () => setCurrentSlide((i) => (i + 1) % slides.length),
    [slides.length]
  );
  const prevSlide = useCallback(
    () => setCurrentSlide((i) => (i - 1 + slides.length) % slides.length),
    [slides.length]
  );
  const togglePause = () => setIsPaused((s) => !s);

  useEffect(() => {
    if (!isPaused) {
      timerRef.current = setInterval(nextSlide, 5000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isPaused, nextSlide]);

  const handleWhatsAppEnquiry = (projectTitle: string) => {
    const message = `Hi! I'm interested in the ${projectTitle} service. Can you provide more details?`;
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, "_blank");
  };

  return (
    <div className="services-page no-scrollbar" ref={mainRef}>
      <Navbar />

      {/* HERO */}
      <section className="section hero" id="services-hero">
        {slides.map((s, i) => (
          <div
            key={i}
            className={`carousel-slide ${i === currentSlide ? "active" : ""}`}
            style={{
              opacity: i === currentSlide ? 1 : 0,
              zIndex: i === currentSlide ? 2 : 1,
            }}
          >
            <Image
              src={s.image}
              alt={s.alt}
              fill
              priority={i === 0}
              sizes="100vw"
              style={{ objectFit: "cover" }}
            />

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
              className={`carousel-indicator ${i === currentSlide ? "active" : ""
                }`}
              onClick={() => setCurrentSlide(i)}
            />
          ))}
        </div>
      </section>

      {/* WHAT WE DO */}
      <section className="section what-we-do">
        <div className="parallax-bg-element"></div>
        <div className="container">
          <h2>What We Do</h2>
          <div className="section-subtitle">
            We transform businesses with cutting-edge digital products and
            innovative solutions.
          </div>

          <div className="services-grid">
            {servicesList.map((service, index) => (
              <div className="services-card" key={index}>
                <div className="service-img-container">
                  <Image
                    src={service.image}
                    alt={service.title}
                    className="service-img"
                    fill
                    style={{ objectFit: "cover" }}
                  />
                </div>
                <div className="service-content">
                  <h3>{service.title}</h3>
                  <p>{service.description}</p>
                  <ul>
                    {service.features.map((feature, idx) => (
                      <li key={idx}>
                        <FaCheckCircle size={20} className="feature-icon" /> {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW WE WORK */}
      <section className="section how-we-work">
        <div className="container">
          <h2>How We Work</h2>
          <div className="section-subtitle">
            A clean, transparent, and milestone-driven workflow that ensures
            project success.
          </div>

          <div className="how-grid">
            {howWork.map((step) => (
              <div key={step.number} className="how-card">
                <div className="how-number">{step.number}</div>
                <h3>{step.title}</h3>
                <p>{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROJECTS */}
      <section className="section projects" id="projects">
        <div className="container">
          <h2>Our Projects Portfolio</h2>
          <div className="section-subtitle">
            Explore the different digital domains we specialize in for our
            clients
          </div>

          <div className="project-wrapper">
            {projectDomains.map((domain) => (
              <div key={domain.number} className="project-domain">
                <div className="domain-img">
                  <Image
                    src={domain.icon}
                    alt={domain.title}
                    width={90}
                    height={90}
                  />
                </div>
                <div className="project-domain-header">
                  <h3>{domain.title}</h3>
                  <p>{domain.text}</p>
                </div>
                <div className="project-card-grid">
                  {domain.projects.map((item, i) => (
                    <div key={i} className="project-card">
                      <div>
                        <h4>{item.title}</h4>
                        <p>{item.desc}</p>
                      </div>
                      <button
                        className="enquire-btn"
                        onClick={() => handleWhatsAppEnquiry(item.title)}
                      >
                        <FaWhatsapp /> Enquire Now
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer contact={contact} />
    </div>
  );
}
