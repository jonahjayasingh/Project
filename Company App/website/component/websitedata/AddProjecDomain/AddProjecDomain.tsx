"use client";
import { useState } from "react";

interface AddProjectDomainProps {
  onClose: () => void;
}

export default function AddProjectDomain({ onClose }: AddProjectDomainProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
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
    data.append("name", formData.name);
    data.append("description", formData.description);
    data.append("image", formData.image as File);

   

    try {
      const res = await fetch("/api/dashboard/projectDomain", {
        method: "POST",
        body: data,
      });

      if (!res.ok) {
        const error = await res.json();
        alert("Error: " + (error.error || "Something went wrong"));
        return;
      }

      alert("Project Domain added successfully!");
      onClose();
    } catch (err) {
      console.error(err);
      alert("Network error: failed to submit project domain");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="addcourse-form">
      <h2>Add Project Domain</h2>

      <div>
        <label>Project Domain Name</label>
        <input
          type="text"
          name="name"
          placeholder="Enter the Project Domain Name"
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
