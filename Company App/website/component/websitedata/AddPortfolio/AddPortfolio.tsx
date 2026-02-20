"use client";
import { useState } from "react";
import "./AddCourse.css";

interface AddCourseProps {
  onClose: () => void;
}

export default function AddCourse({ onClose }: AddCourseProps) {
  const [formData, setFormData] = useState({
    course_name: "",
    description: "",
    duration: "",
    Price: "",
    course_difficulty: "Beginner",
    image: null as File | null,
  });

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

    if (formData.image) {
      data.append("image", formData.image);
    } else {
      alert("Image is required");
      return;
    }

    try {
      const res = await fetch("/api/dashboard/courses", {
        method: "POST",
        body: data,
      });

      if (!res.ok) {
        const error = await res.json();
        alert("Error: " + (error.error || "Something went wrong"));
        return;
      }

      alert("Course added successfully!");
      onClose();
    } catch (err) {
      console.error(err);
      alert("Network error: failed to submit course");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="addcourse-form">
      <h2>Add Course</h2>

      <div>
        <label>Course Name</label>
        <input
          type="text"
          name="course_name"
          placeholder="Enter the Course Name"
          required
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Description</label>
        <textarea
          name="description"
          placeholder="Enter the Course Description"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Duration</label>
        <input
          type="text"
          name="duration"
          placeholder="Enter duration e.g. 1 month"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Price</label>
        <input
          type="number"
          name="Price"
          placeholder="Enter the amount"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Difficulty</label>
        <select name="course_difficulty" onChange={handleChange}>
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>
      </div>

      <div>
        <label>Image</label>
        <input
          type="file"
          name="image"
          accept=".png,.jpg,.jpeg"
          required
          onChange={handleChange}
        />
      </div>

      <div className="button-row">
        <input type="submit" value="Submit" />
        <button type="button" className="close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </form>
  );
}
