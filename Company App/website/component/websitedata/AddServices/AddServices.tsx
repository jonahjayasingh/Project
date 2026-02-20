"use client";
import { useState } from "react";
import "./AddServices.css";

interface AddServicesProps {
  onClose: () => void;
}

export default function AddServices({ onClose }: AddServicesProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    key_points: "",
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
    data.append("title", formData.title);
    data.append("description", formData.description);
    data.append("key_points", formData.key_points);

    try {
      const res = await fetch("/api/dashboard/services", {
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
      <h2>Add Service</h2>

      <div>
        <label>Service Name</label>
        <input
          type="text"
          name="title"
          placeholder="Enter the Service Name"
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
        <label>Key Points</label>
        <textarea
          name="key_points"
          placeholder="Enter the Key Points separated by commas"
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
