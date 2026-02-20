"use client";
import { useState, useEffect } from "react";
import "./AddTestimonial.css";

interface AddTestimonialProps {
    onClose: () => void;
    testimonial?: any; // provided when editing
}

export default function AddTestimonial({ onClose, testimonial }: AddTestimonialProps) {
    const [formData, setFormData] = useState({
        name: "",
        job_title: "",
        company: "",
        image: null as File | null,
    });

    // Prefill when editing
    useEffect(() => {
        if (testimonial) {
            console.log(testimonial)
            setFormData((prev) => ({
                ...prev,
                name: testimonial.name || "",
                job_title: testimonial.job_title || "",
                company: testimonial.company || "",
                image: null, // don't preload a file
            }));
        }
    }, [testimonial]);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, files } = e.target as HTMLInputElement;
        setFormData((prev) => ({
            ...prev,
            [name]: files ? files[0] : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        const data = new FormData();
        data.append("name", formData.name);
        data.append("job_title", formData.job_title);
        data.append("company_name", formData.company);

        // Only require image if creating new
        if (formData.image) {
            data.append("image", formData.image);
        } else if (!testimonial) {
            alert("Image is required");
            return;
        }

        // add ID when editing
        if (testimonial) data.append("id", testimonial.id);

        try {
            const res = await fetch("/api/dashboard/testimonials", {
                method: testimonial ? "PUT" : "POST",
                body: data,
            });

            if (!res.ok) {
                const error = await res.json();
                alert("Error: " + (error.error || "Something went wrong"));
                return;
            }

            alert(testimonial ? "Testimonial updated successfully!" : "Testimonial added successfully!");
            onClose();
        } catch (err) {
            console.error(err);
            alert("Network error: failed to submit testimonial");
        }
    };

    return (
        <form onSubmit={handleSubmit} className="addcourse-form">
            <h2>{testimonial ? "Edit Testimonial" : "Add Testimonial"}</h2>

            <div>
                <label>Name</label>
                <input
                    type="text"
                    name="name"
                    placeholder="Enter Name"
                    value={formData.name}
                    required
                    onChange={handleChange}
                />
            </div>

            <div>
                <label>Job Title</label>
                <input
                    type="text"
                    name="job_title"
                    placeholder="Enter Job Title"
                    value={formData.job_title}
                    onChange={handleChange}
                />
            </div>

            <div>
                <label>Company</label>
                <input
                    type="text"
                    name="company"
                    placeholder="Enter Company Name"
                    value={formData.company}
                    onChange={handleChange}
                />
            </div>

            <div>
                <label>Image {testimonial ? "(upload to change)" : ""}</label>
                <input
                    type="file"
                    name="image"
                    accept=".png,.jpg,.jpeg"
                    onChange={handleChange}
                    required={!testimonial}
                />
            </div>

            <div className="button-row">
                <input type="submit" value={testimonial ? "Update Testimonial" : "Submit"} />
                <button type="button" className="close-btn" onClick={onClose}>
                    Close
                </button>
            </div>
        </form>
    );
}
