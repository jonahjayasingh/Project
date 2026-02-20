"use client";
import { useState, useEffect } from "react";
import "./AddCourse.css";

interface AddCourseProps {
  onClose: () => void;
  course?: any; // provided when editing
}

export default function AddCourse({ onClose, course }: AddCourseProps) {
  const [formData, setFormData] = useState({
    course_name: "",
    description: "",
    duration: "",
    Price: "",
    course_difficulty: "Beginner",
    image: null as File | null,
  });

  // Prefill data when editing
  useEffect(() => {
    if (course) {
      setFormData((prev) => ({
        ...prev,
        course_name: course.course_name || "",
        description: course.description || "",
        duration: course.duration || "",
        Price: course.Price || "",
        course_difficulty: course.course_difficulty || "Beginner",
        image: null, // we never prefill File with url
      }));
    }
  }, [course]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
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
    data.append("course_name", formData.course_name);
    data.append("description", formData.description);
    data.append("duration", formData.duration);
    data.append("Price", formData.Price);
    data.append("course_difficulty", formData.course_difficulty);

    // Only require image if it's a new course, not when editing
    if (formData.image) {
      data.append("image", formData.image);
    } else if (!course) {
      alert("Image is required");
      return;
    }
    if (course) data.append("id",course.id)
    try {
      const res = await fetch("/api/dashboard/courses", {
        method: course ? "PUT" : "POST", // switch based on edit mode
        body: data,
      });

      if (!res.ok) {
        const error = await res.json();
        alert("Error: " + (error.error || "Something went wrong"));
        return;
      }

      alert(course ? "Course updated successfully!" : "Course added successfully!");
      onClose();
    } catch (err) {
      console.error(err);
      alert("Network error: failed to submit course");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="addcourse-form">
      <h2>{course ? "Edit Course" : "Add Course"}</h2>

      <div>
        <label>Course Name</label>
        <input
          type="text"
          name="course_name"
          placeholder="Enter the Course Name"
          value={formData.course_name}
          required
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Description</label>
        <textarea
          name="description"
          placeholder="Enter the Course Description"
          value={formData.description}
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Duration</label>
        <input
          type="text"
          name="duration"
          placeholder="Enter duration e.g. 1 month"
          value={formData.duration}
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Price</label>
        <input
          type="number"
          name="Price"
          placeholder="Enter the amount"
          value={formData.Price}
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Difficulty</label>
        <select
          name="course_difficulty"
          value={formData.course_difficulty}
          onChange={handleChange}
        >
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>
      </div>

      <div>
        <label>Image {course ? "(upload to change)" : ""}</label>
        <input
          type="file"
          name="image"
          accept=".png,.jpg,.jpeg"
          onChange={handleChange}
          required={!course} // only required when creating
        />
      </div>

      <div className="button-row">
        <input type="submit" value={course ? "Update Course" : "Submit"} />
        <button type="button" className="close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </form>
  );
}
