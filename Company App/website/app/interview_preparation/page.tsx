"use client";

import "./style.css";
import Navbar from "@/component/Navbar/Navbar";
import Footer from "@/component/footer/footer";
import {
  FiSearch,
  FiCode,
  FiDatabase,
  FiServer,
  FiLayout,
  FiTerminal,
  FiCpu,
  FiGlobe,
  FiLock,
  FiX,
  FiChevronDown,
  FiChevronUp,
} from "react-icons/fi";
import { useState, useMemo, useRef, useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";

if (typeof window !== "undefined") gsap.registerPlugin(ScrollTrigger);

export default function InterviewPreparation() {
  const mainRef = useRef<HTMLDivElement>(null);
  const [selectedTopic, setSelectedTopic] = useState<string | null>("Python");
  const [openQuestionIndex, setOpenQuestionIndex] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Refs for GSAP animations
  const heroRef = useRef<HTMLDivElement>(null);
  const topicsRef = useRef<HTMLDivElement>(null);
  const topicListRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const topicCardsRef = useRef<HTMLDivElement[]>([]);

  const topics = [

    { title: "Python", description: "Beginner to advanced Python concepts.", icon: <FiCode size={20} />, key: "Python" },
    { title: "HTML", description: "Learn the structure of web pages.", icon: <FiLayout size={20} />, key: "HTML" },
    { title: "CSS", description: "Styling, layouts, Flexbox and Grid.", icon: <FiLayout size={20} />, key: "CSS" },
    { title: "Bootstrap", description: "Responsive UI with Bootstrap.", icon: <FiLayout size={20} />, key: "Bootstrap" },
    { title: "JavaScript", description: "Dynamic and interactive web applications.", icon: <FiCode size={20} />, key: "JavaScript" },
    { title: "Java", description: "OOP & enterprise-level programming with Java.", icon: <FiCode size={20} />, key: "Java" },
    { title: "Django", description: "Full-stack web development using Django.", icon: <FiServer size={20} />, key: "Django" },
    { title: "React", description: "Modern UI development using React.", icon: <FiCode size={20} />, key: "React" },
    { title: "C", description: "Low-level programming using C.", icon: <FiCode size={20} />, key: "C" },
    { title: "C++", description: "OOP & system programming using C++.", icon: <FiCode size={20} />, key: "C++" },
  ];

  const interview_questions: Record<string, { question: string; answer: string }[]> = {
    "Data Structures": [
      { question: "What is an Array?", answer: "An array is a collection of items stored at contiguous memory locations." },
      { question: "Explain Linked Lists.", answer: "A linked list is a linear data structure where elements are linked using pointers." },
      { question: "What are Trees?", answer: "Trees are hierarchical data structures with a root value and subtrees of children." },
      { question: "What is a Graph?", answer: "A graph is a collection of nodes connected by edges." },
      { question: "Difference between Stack and Queue?", answer: "Stack is LIFO, Queue is FIFO." },
    ],
    "Algorithms": [
      { question: "What is Time Complexity?", answer: "Time complexity measures the time taken by an algorithm to run as a function of input size." },
      { question: "Explain Binary Search.", answer: "Binary search efficiently finds an item in a sorted array by repeatedly dividing the search interval in half." },
      { question: "What is Dynamic Programming?", answer: "DP solves complex problems by breaking them into simpler subproblems and storing their solutions." },
      { question: "What are Sorting Algorithms?", answer: "Algorithms that arrange elements in a particular order, like QuickSort, MergeSort, etc." },
      { question: "What is Greedy Algorithm?", answer: "A greedy algorithm makes locally optimal choices at each step to find a global optimum." },
    ],
    "System Design": [
      { question: "What is Scalability?", answer: "Scalability is the ability of a system to handle growing amounts of work by adding resources." },
      { question: "Explain Load Balancing.", answer: "Load balancing distributes network traffic across multiple servers to ensure reliability." },
      { question: "What is Caching?", answer: "Caching stores frequently accessed data in fast memory to improve performance." },
      { question: "What are Microservices?", answer: "Microservices architecture structures an application as a collection of loosely coupled services." },
      { question: "What is Database Sharding?", answer: "Sharding splits a database into smaller, faster, more easily managed parts called shards." },
    ],
    Python: [
      { question: "What is Python?", answer: "Python is a high-level, interpreted programming language with dynamic semantics." },
      { question: "Explain Python's pass statement.", answer: "The pass statement is a null operation; it is used as a placeholder." },
      { question: "What are Python decorators?", answer: "Decorators are functions that modify the behavior of another function." },
      { question: "Difference between list and tuple?", answer: "Lists are mutable, tuples are immutable." },
      { question: "What is Python's GIL?", answer: "GIL stands for Global Interpreter Lock; it allows only one thread to execute Python bytecode at a time." },
      { question: "Explain Python's lambda function.", answer: "Lambda functions are anonymous, single-expression functions." },
      { question: "What are Python modules?", answer: "Modules are files containing Python definitions and statements." },
    ],
    HTML: [
      { question: "What is HTML?", answer: "HTML is a markup language used to structure web pages." },
      { question: "Difference between <div> and <span>?", answer: "<div> is a block-level element; <span> is inline." },
      { question: "What are semantic tags?", answer: "Semantic tags provide meaning to the content, like <header>, <footer>, <article>." },
      { question: "What is the purpose of the <head> tag?", answer: "<head> contains meta-information about the document." },
      { question: "What are HTML forms?", answer: "Forms are used to collect user input." },
    ],
    CSS: [
      { question: "What is CSS?", answer: "CSS is used for styling HTML elements." },
      { question: "Difference between relative, absolute, fixed, and sticky positioning?", answer: "Relative is relative to normal position, absolute is relative to parent, fixed is relative to viewport, sticky is relative until a threshold." },
      { question: "What is the difference between inline, internal, and external CSS?", answer: "Inline is within element, internal is within <style>, external is in a separate file." },
      { question: "What are pseudo-classes?", answer: "Pseudo-classes style elements based on state, e.g., :hover, :focus." },
      { question: "What are pseudo-elements?", answer: "Pseudo-elements style part of elements, e.g., ::before, ::after." },
    ],
    Bootstrap: [
      { question: "What is Bootstrap?", answer: "Bootstrap is a CSS framework for responsive web design." },
      { question: "What are Bootstrap's breakpoints?", answer: "Breakpoints define responsive design thresholds for xs, sm, md, lg, xl screens." },
      { question: "Explain Bootstrap's grid system.", answer: "Grid system uses rows and columns to create layouts." },
      { question: "What are Bootstrap components?", answer: "Pre-designed UI elements like buttons, navbars, cards." },
      { question: "Difference between container and container-fluid?", answer: "container has fixed width, container-fluid spans full width." },
    ],
    JavaScript: [
      { question: "What is JavaScript?", answer: "JavaScript is a programming language used for web development to create dynamic behavior." },
      { question: "Difference between var, let, and const?", answer: "var is function-scoped, let and const are block-scoped; const cannot be reassigned." },
      { question: "What are JavaScript closures?", answer: "Closures are functions that have access to variables in their outer scope even after outer function executes." },
      { question: "Explain hoisting in JavaScript.", answer: "Hoisting moves variable and function declarations to the top of their scope." },
      { question: "What are JavaScript promises?", answer: "Promises handle asynchronous operations and have states: pending, resolved, rejected." },
    ],
    Java: [
      { question: "What is Java?", answer: "Java is a high-level, object-oriented programming language that runs on JVM." },
      { question: "Difference between JDK, JRE, and JVM?", answer: "JVM runs Java bytecode, JRE is JVM + libraries, JDK is JRE + development tools." },
      { question: "What is the difference between abstract class and interface?", answer: "Abstract class can have implemented methods; interface has only abstract methods (before Java 8) and no state." },
      { question: "Explain method overloading and overriding.", answer: "Overloading: same method name, different parameters; Overriding: subclass provides new implementation." },
      { question: "What are Java exceptions?", answer: "Exceptions are events that disrupt normal flow; checked and unchecked exist." },
    ],
    Django: [
      { question: "What is Django?", answer: "Django is a high-level Python web framework for rapid development." },
      { question: "What is the MTV architecture in Django?", answer: "Model-Template-View, where View handles business logic, Template handles UI, Model handles data." },
      { question: "Explain Django ORM.", answer: "Django ORM allows interacting with the database using Python objects instead of SQL." },
      { question: "What are Django models?", answer: "Models define database schema as Python classes." },
      { question: "What is a Django view?", answer: "View processes requests and returns responses." },
    ],
    React: [
      { question: "What is React?", answer: "React is a JavaScript library for building user interfaces, developed by Facebook." },
      { question: "What are components in React?", answer: "Components are reusable UI pieces that define how a section of the interface should appear." },
      { question: "Difference between functional and class components?", answer: "Functional components are stateless and use hooks; class components use lifecycle methods and state." },
      { question: "What are React hooks?", answer: "Hooks allow functional components to use state and lifecycle features." },
      { question: "What is JSX?", answer: "JSX is a syntax extension that allows writing HTML-like code inside JavaScript." },
    ],
    C: [
      { question: "What is C language?", answer: "C is a general-purpose, procedural programming language developed by Dennis Ritchie in 1972." },
      { question: "What are variables in C?", answer: "Variables are data storage locations identified by names and types." },
      { question: "Difference between call by value and call by reference?", answer: "Call by value passes a copy of data; call by reference passes an address of data." },
      { question: "What are pointers?", answer: "Pointers are variables that store memory addresses of other variables." },
      { question: "What is the difference between malloc() and calloc()?", answer: "malloc allocates uninitialized memory; calloc allocates zero-initialized memory." },
    ],
    "C++": [
      { question: "What is C++?", answer: "C++ is an object-oriented programming language developed as an extension of C by Bjarne Stroustrup." },
      { question: "What are classes and objects?", answer: "Classes are blueprints for creating objects; objects are instances of classes." },
      { question: "Explain inheritance in C++.", answer: "Inheritance allows one class to acquire properties and behaviors of another." },
      { question: "What is polymorphism?", answer: "Polymorphism means one interface with multiple implementations, achieved via function overloading or overriding." },
      { question: "What are constructors and destructors?", answer: "Constructors initialize objects; destructors clean up resources before objects are destroyed." },
    ],
  };

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
      // Hero section animation
      if (heroRef.current) {
        gsap.fromTo(heroRef.current.children,
          { y: 50, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 1,
            stagger: 0.2,
            ease: "power3.out"
          }
        );
      }

      // Topics list animation
      if (topicListRef.current) {
        gsap.fromTo(topicListRef.current.querySelectorAll('.topic-item'),
          { x: -30, opacity: 0 },
          {
            x: 0,
            opacity: 1,
            duration: 0.6,
            stagger: 0.05,
            ease: "power2.out",
            delay: 0.3
          }
        );
      }

      // Initial content animation
      if (contentRef.current && selectedTopic) {
        gsap.fromTo(contentRef.current,
          { y: 30, opacity: 0 },
          {
            y: 0,
            opacity: 1,
            duration: 0.8,
            ease: "power2.out",
            delay: 0.5
          }
        );
      }
    }, mainRef);

    return () => {
      lenis.destroy();
      gsap.ticker.remove((time) => {
        lenis.raf(time * 1000);
      });
      ctx.revert();
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, []);

  // Content animation when topic changes
  useEffect(() => {
    if (contentRef.current && selectedTopic) {
      gsap.fromTo(contentRef.current,
        { y: 20, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          ease: "power2.out"
        }
      );

      // Animate questions
      gsap.fromTo(contentRef.current.querySelectorAll('.qa-box'),
        { x: -20, opacity: 0 },
        {
          x: 0,
          opacity: 1,
          duration: 0.4,
          stagger: 0.1,
          delay: 0.2
        }
      );
    }
  }, [selectedTopic]);

  // Question toggle animation
  const animateQuestionToggle = (index: number, isOpening: boolean) => {
    const questionElement = document.querySelector(`.qa-box:nth-child(${index + 1})`);
    if (questionElement) {
      if (isOpening) {
        gsap.to(questionElement, {
          scale: 1.02,
          duration: 0.2,
          ease: "power2.out"
        });
        gsap.to(questionElement.querySelector('.qa-answer'), {
          height: "auto",
          opacity: 1,
          duration: 0.3,
          ease: "power2.out"
        });
      } else {
        gsap.to(questionElement, {
          scale: 1,
          duration: 0.2,
          ease: "power2.out"
        });
        gsap.to(questionElement.querySelector('.qa-answer'), {
          height: 0,
          opacity: 0,
          duration: 0.3,
          ease: "power2.out"
        });
      }
    }
  };

  // Filter topics based on search query
  const filteredTopics = useMemo(() => {
    if (!searchQuery.trim()) return topics;

    const query = searchQuery.toLowerCase().trim();
    return topics.filter(topic =>
      topic.title.toLowerCase().includes(query) ||
      topic.description.toLowerCase().includes(query) ||
      topic.key.toLowerCase().includes(query)
    );
  }, [searchQuery, topics]);

  // Filter questions based on search query
  const filteredQuestions = useMemo(() => {
    if (!selectedTopic || !interview_questions[selectedTopic]) return [];

    if (!searchQuery.trim()) return interview_questions[selectedTopic];

    const query = searchQuery.toLowerCase().trim();
    return interview_questions[selectedTopic].filter(item =>
      item.question.toLowerCase().includes(query) ||
      item.answer.toLowerCase().includes(query)
    );
  }, [searchQuery, selectedTopic]);

  const handleTopicClick = (key: string) => {
    setSelectedTopic(key);
    setOpenQuestionIndex(null);

    // Animate the clicked topic item
    const clickedElement = document.querySelector(`[data-topic="${key}"]`);
    if (clickedElement) {
      gsap.to(clickedElement, {
        scale: 0.95,
        duration: 0.2,
        yoyo: true,
        repeat: 1
      });
    }
  };

  const toggleQuestion = (index: number) => {
    const isOpening = openQuestionIndex !== index;
    setOpenQuestionIndex(isOpening ? index : null);
    animateQuestionToggle(index, isOpening);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);

    // Animate search interaction
    if (e.target.value) {
      gsap.to('.search-wrapper', {
        scale: 1.02,
        duration: 0.2,
        ease: "power2.out"
      });
    } else {
      gsap.to('.search-wrapper', {
        scale: 1,
        duration: 0.2,
        ease: "power2.out"
      });
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    gsap.to('.search-wrapper', {
      scale: 1,
      duration: 0.2,
      ease: "power2.out"
    });
  };

  // Add card to refs array
  const addToRefs = (el: HTMLDivElement | null) => {
    if (el && !topicCardsRef.current.includes(el)) {
      topicCardsRef.current.push(el);
    }
  };

  return (
    <div className="prep-container" ref={mainRef}>
      <Navbar />

      <main className="prep-main">
        <section className="hero-section" ref={heroRef}>
          <h1 className="hero-title">
            Master Your <span className="hero-gradient">Technical Interview</span>
          </h1>
          <p className="hero-subtitle">Select a topic to explore curated interview questions & answers.</p>

          <div className="search-wrapper">
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search topics, questions, or companies..."
              className="search-input"
              value={searchQuery}
              onChange={handleSearchChange}
            />
            {searchQuery && (
              <button className="clear-search" onClick={clearSearch}>
                <FiX size={16} />
              </button>
            )}
          </div>
        </section>

        <section className="content-section">
          <div className="content-layout">
            {/* Topics List Sidebar */}
            <div className="topics-sidebar" ref={topicListRef}>
              <h3 className="sidebar-title">Interview Topics</h3>
              <div className="topics-list">
                {filteredTopics.length > 0 ? (
                  filteredTopics.map((topic, i) => (
                    <button
                      key={i}
                      data-topic={topic.key}
                      className={`topic-item ${selectedTopic === topic.key ? 'active' : ''}`}
                      onClick={() => handleTopicClick(topic.key)}
                    >
                      <div className="topic-item-icon">{topic.icon}</div>
                      <div className="topic-item-content">
                        <span className="topic-item-title">{topic.title}</span>
                        <span className="topic-item-desc">{topic.description}</span>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="no-results">
                    <p>No topics found matching "{searchQuery}"</p>
                  </div>
                )}
              </div>
            </div>

            {/* Questions Content */}
            <div className="questions-content" ref={contentRef}>
              {selectedTopic && (
                <>
                  <div className="content-header">
                    <h2>{selectedTopic} Interview Questions</h2>
                    <div className="questions-count">
                      {filteredQuestions.length} question{filteredQuestions.length !== 1 ? 's' : ''}
                    </div>
                  </div>

                  <div className="questions-list">
                    {filteredQuestions.length > 0 ? (
                      filteredQuestions.map((item, index) => (
                        <div key={index} className={`qa-box ${openQuestionIndex === index ? "open" : ""}`}>
                          <button className="qa-question" onClick={() => toggleQuestion(index)}>
                            <span className="question-text">{index + 1}. {item.question}</span>
                            {openQuestionIndex === index ? <FiChevronUp /> : <FiChevronDown />}
                          </button>
                          <div className="qa-answer">
                            <p>{item.answer}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="no-results">
                        <p>No questions found matching "{searchQuery}"</p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </section>
      </main>

      <Footer contact={{} as any} />
    </div>
  );
}