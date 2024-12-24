// src/components/PresentationDetails.jsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../styles/PresentationDetails.css';
import { useParams, Link } from 'react-router-dom';

const PresentationDetails = () => {
  const { id } = useParams();
  const [presentation, setPresentation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPresentation = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/v1/presentations/${id}`);
        setPresentation(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Error fetching presentation details.');
      } finally {
        setLoading(false);
      }
    };

    fetchPresentation();
  }, [id]);

  if (loading) {
    return <div className="details-container"><p>Loading...</p></div>;
  }

  if (error) {
    return <div className="details-container"><p className="error-text">{error}</p></div>;
  }

  return (
    <div className="details-container">
      <h2 className="details-title">Presentation Details</h2>
      <p><strong>ID:</strong> {presentation.id}</p>
      <p><strong>Topic:</strong> {presentation.topic}</p>
      <p><strong>Number of Slides:</strong> {presentation.num_slides}</p>
      <p><strong>Theme:</strong> {presentation.theme}</p>
      <p><strong>Status:</strong> {presentation.status}</p>
      <p><strong>Download URL:</strong> <a href={`http://localhost:5000${presentation.download_url}`} target="_blank" rel="noopener noreferrer">Download PPTX</a></p>
      <Link to={`/presentations/${id}/modify`} className="modify-button">Modify Presentation</Link>
    </div>
  );
};

export default PresentationDetails;
