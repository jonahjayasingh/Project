"use client";
import { useState, useEffect } from "react";
import "./AddGallery.css";

interface AddGalleryProps {
  onClose: () => void;
  gallery?: any; // when provided → edit mode
}

export default function AddGallery({ onClose, gallery }: AddGalleryProps) {
  const [formData, setFormData] = useState({
    title: "",
    image: null as File | null,
  });

  // Prefill when editing
  useEffect(() => {
    if (gallery) {
      setFormData({
        title: gallery.title || "",
        image: null,
      });
    }
  }, [gallery]);

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
    data.append("title", formData.title);

    // only send image if selected (for edit)
    if (formData.image) {
      data.append("image", formData.image);
    }

    // send id inside FormData when editing
    if (gallery?.id) {
      data.append("id", String(gallery.id));
    }

    // decide method
    const method = gallery ? "PUT" : "POST";
    const url = "/api/dashboard/gallery";

    try {
      const res = await fetch(url, {
        method,
        body: data,
      });

      if (!res.ok) {
        const error = await res.json();
        alert("Error: " + (error.error || "Something went wrong"));
        return;
      }

      alert(gallery ? "Gallery updated successfully!" : "Gallery added successfully!");
      onClose();
    } catch (err) {
      console.error(err);
      alert("Network error: failed to submit gallery");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="addcourse-form">
      <h2>{gallery ? "Edit Gallery" : "Add Gallery"}</h2>

      <div>
        <label>Title</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          placeholder="Enter the Title"
          required
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Image {gallery && "(Upload only if updating)"}</label>
        <input
          type="file"
          name="image"
          accept=".png,.jpg,.jpeg"
          onChange={handleChange}
        />
      </div>

      <div className="button-row">
        <input type="submit" value={gallery ? "Update Gallery" : "Add Gallery"} />
        <button type="button" className="close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </form>
  );
}
