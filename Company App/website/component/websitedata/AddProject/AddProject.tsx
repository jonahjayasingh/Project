"use client";
import { useState ,useEffect} from "react";

interface AddProjectProps {
  onClose: () => void;
}

export default function AddProject({ onClose }: AddProjectProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    domainid: "",
  });

  const [domainOptions, setDomainOptions] = useState<any[]>([]);

  useEffect(() => {
    const fetchDomains = async () => {
      try {
        const res = await fetch("/api/dashboard/projectDomain");
        if (!res.ok) {
          const error = await res.json();
          alert("Error: " + (error.error || "Something went wrong"));
          return;
        }
        const domains = await res.json();
        setDomainOptions(domains.map((d: any) => ({ value: d.id.toString(), label: d.name })));
      } catch (err) {
        console.error(err);
        alert("Network error: failed to fetch project domains");
      }
    };
    fetchDomains();
  }, []);

  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data = new FormData();
    data.append("title", formData.title);
    data.append("description", formData.description);
    data.append("domainid", formData.domainid);

    const res = await fetch("/api/dashboard/project", { method: "POST", body: data });

    if (!res.ok) {
      const error = await res.json();
      alert("Error: " + (error.error || "Something went wrong"));
      return;
    }

    alert("Project added successfully!");
    onClose();
  };

  return (
    <form onSubmit={handleSubmit} className="addcourse-form">
      <h2>Add Project</h2>

      <div>
        <label>Title</label>
        <input
          type="text"
          name="title"
          placeholder="Enter the Project Title"
          required
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Description</label>
        <textarea
          name="description"
          placeholder="Enter the Project Description"
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Domain</label>
        <select
          name="domainid"
          required
          value={formData.domainid}
          onChange={handleChange}
        >
          <option value="" disabled>Select a domain</option>
          {domainOptions.map((domain: any) => (
            <option key={domain.value} value={domain.value}>
              {domain.label}
            </option>
          ))}
        </select>
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
