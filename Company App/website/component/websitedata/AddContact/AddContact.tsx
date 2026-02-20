"use client";

import { useState, useEffect } from "react";

interface AddContactProps {
  onClose: () => void;
  contact?: any; // when provided → edit mode
}

export default function AddContact({ onClose, contact }: AddContactProps) {
  const [formData, setFormData] = useState({
    phone1: "",
    phone2: "",
    email: "",
    map: "",
    address: "",
    instagram_link: "",
    facebook_link: "",
    x_link: "",
    linkedin_link: "",
    youtube_link: "",
  });

  // Pre-fill when editing
  useEffect(() => {
    if (contact) {
      setFormData({
        phone1: contact.phone1 || "",
        phone2: contact.phone2 || "",
        email: contact.email || "",
        map: contact.map || "",
        address: contact.address || "",
        instagram_link: contact.instagram_link || "",
        facebook_link: contact.facebook_link || "",
        x_link: contact.x_link || "",
        linkedin_link: contact.linkedin_link || "",
        youtube_link: contact.youtube_link || "",
      });
    }
  }, [contact]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };


  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const data = new FormData();
    Object.entries(formData).forEach(([key, value]) => data.append(key, value));
    if (contact) data.append("id",contact.id)
      console.log(contact)
    // switch add / edit automatically
    const url =  "/api/dashboard/contact";
    const method = contact ? "PUT" : "POST";

    try {
      const res = await fetch(url, { method, body: data });

      if (!res.ok) {
        const error = await res.json();
        alert("Error: " + (error.error || "Something went wrong"));
        return;
      }

      alert(contact ? "Contact updated successfully!" : "Contact added successfully!");
      onClose();
    } catch (err) {
      alert("Network error!");
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="addcourse-form">
      <h2>{contact ? "Edit Contact" : "Add Contact"}</h2>

      <div>
        <label>Phone 1</label>
        <input
          type="text"
          name="phone1"
          value={formData.phone1}
          placeholder="Enter Phone"
          required
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Phone 2</label>
        <input
          type="text"
          name="phone2"
          value={formData.phone2}
          placeholder="Enter Second Phone"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Email</label>
        <input
          type="text"
          name="email"
          value={formData.email}
          placeholder="Enter Email"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Address</label>
        <textarea
          name="address"
          value={formData.address}
          placeholder="Enter Address"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Map (Embed Code)</label>
        <input
          type="text"
          name="map"
          value={formData.map}
          placeholder="Enter Map iFrame Code"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Instagram Link</label>
        <input
          type="text"
          name="instagram_link"
          value={formData.instagram_link}
          placeholder="Enter Instagram Link"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Facebook Link</label>
        <input
          type="text"
          name="facebook_link"
          value={formData.facebook_link}
          placeholder="Enter Facebook Link"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>X Link</label>
        <input
          type="text"
          name="x_link"
          value={formData.x_link}
          placeholder="Enter X (Twitter) Link"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>LinkedIn Link</label>
        <input
          type="text"
          name="linkedin_link"
          value={formData.linkedin_link}
          placeholder="Enter LinkedIn Link"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>YouTube Link</label>
        <input
          type="text"
          name="youtube_link"
          value={formData.youtube_link}
          placeholder="Enter YouTube Link"
          onChange={handleChange}
        />
      </div>

      <div className="button-row">
        <input type="submit" value={contact ? "Update" : "Submit"} />
        <button type="button" className="close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </form>
  );
}
