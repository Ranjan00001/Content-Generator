// src/components/ModifyPresentation.jsx

import React, { useEffect, useState, useRef } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import SlideConfig from './SlideConfig';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import '../styles/ModifyPresentation.css';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { Link } from 'react-router-dom';


// Define supported layouts
const supportedLayouts = [
  { value: 'title', label: 'Title Slide' },
  { value: 'bullet_points', label: 'Bullet Points' },
  { value: 'two_column', label: 'Two-Column Layout' },
  { value: 'content_with_image', label: 'Content with Image' },
];

// Validation schema using Yup
const schema = yup.object().shape({
  topic: yup.string().required('Topic is required'),
  num_slides: yup
    .number()
    .typeError('Number of slides must be a number')
    .required('Number of slides is required')
    .min(1, 'Minimum 1 slide')
    .max(20, 'Maximum 20 slides'),
  theme: yup.string().required('Theme is required'),
  layouts: yup.array().of(
    yup
      .object()
      .shape({
        value: yup
          .string()
          .oneOf(['title', 'bullet_points', 'two_column', 'content_with_image'])
          .required('Layout is required'),
      })
      .required()
  ),
});

const ModifyPresentation = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [presentation, setPresentation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState(null);

  const downloadRef = useRef(null); // Ref for the download container

  // Initialize React Hook Form
  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      topic: '',
      num_slides: 5,
      theme: 'default',
      layouts: [],
    },
  });

  const { fields, append, remove, replace } = useFieldArray({
    control,
    name: 'layouts',
  });

  const numSlides = watch('num_slides');

  useEffect(() => {
    const fetchPresentation = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/v1/presentations/${id}`);
        setPresentation(response.data);
        // Set form values based on fetched data
        setValue('topic', response.data.topic);
        setValue('num_slides', response.data.num_slides);
        setValue('theme', response.data.theme);
        setValue('layouts', response.data.layouts.map(layout => ({ value: layout })));
        // Replace field array
        replace(response.data.layouts.map(layout => ({ value: layout })));
      } catch (err) {
        setError(err.response?.data?.error || 'Error fetching presentation details.');
      } finally {
        setLoading(false);
      }
    };

    fetchPresentation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Dynamically manage layouts based on number of slides
  useEffect(() => {
    const currentLayouts = fields.length;
    const desiredLayouts = parseInt(numSlides, 10) || 5;

    if (currentLayouts < desiredLayouts) {
      for (let i = currentLayouts; i < desiredLayouts; i++) {
        append({ value: 'bullet_points' });
      }
    } else if (currentLayouts > desiredLayouts) { // Corrected variable name
      for (let i = currentLayouts; i > desiredLayouts; i--) {
        remove(i - 1);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [numSlides]);

  // Auto-scroll to download button when downloadUrl is set
  useEffect(() => {
    if (downloadRef.current) {
      downloadRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [downloadRef]);

  const onSubmit = async (data) => {
    setSubmitLoading(true);
    setError(null);

    try {
      const payload = {
        topic: data.topic,
        num_slides: data.num_slides,
        theme: data.theme,
        layouts: data.layouts.map((layout) => layout.value),
      };

      const response = await axios.post(
        `http://localhost:5000/api/v1/presentations/${id}/configure`,
        payload
      );

      // Assuming the backend updates the presentation and keeps the same ID
      setPresentation(response.data);
      setSubmitLoading(false);
      // Scroll to download button
      if (downloadRef.current) {
        downloadRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error || 'An error occurred while updating the presentation.'
      );
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return <div className="modify-container"><p>Loading...</p></div>;
  }

  if (error) {
    return <div className="modify-container"><p className="error-text">{error}</p></div>;
  }

  return (
    <div className="modify-container">
      <h2 className="modify-title">Modify Presentation</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="modify-form">
        {/* Topic Input */}
        <div className="form-group">
          <label htmlFor="topic">Topic/Subject</label>
          <input
            type="text"
            id="topic"
            {...register('topic')}
            className={`form-input ${errors.topic ? 'input-error' : ''}`}
          />
          {errors.topic && (
            <p className="error-message">{errors.topic.message}</p>
          )}
        </div>

        {/* Number of Slides */}
        <div className="form-group">
          <label htmlFor="num_slides">Number of Slides</label>
          <input
            type="number"
            id="num_slides"
            {...register('num_slides')}
            min="1"
            max="20"
            className={`form-input ${errors.num_slides ? 'input-error' : ''}`}
          />
          {errors.num_slides && (
            <p className="error-message">{errors.num_slides.message}</p>
          )}
        </div>

        {/* Theme Selection */}
        <div className="form-group">
          <label htmlFor="theme">Theme</label>
          <select
            id="theme"
            {...register('theme')}
            className={`form-select ${errors.theme ? 'input-error' : ''}`}
          >
            <option value="default">Default</option>
            <option value="dark">Dark</option>
            <option value="light">Light</option>
            {/* Add more themes as needed */}
          </select>
          {errors.theme && (
            <p className="error-message">{errors.theme.message}</p>
          )}
        </div>

        {/* Slide Layouts Configuration */}
        <div className="form-group">
          <h3 className="section-title">Slide Layouts Configuration</h3>
          {fields.map((field, index) => (
            <SlideConfig
              key={field.id}
              index={index}
              register={register}
              errors={errors.layouts && errors.layouts[index]}
            />
          ))}
        </div>

        {/* Submit Button */}
        <div className="form-group">
          <button
            type="submit"
            disabled={submitLoading}
            className="submit-button"
          >
            {submitLoading ? 'Updating...' : 'Update Presentation'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-container">
            <p className="error-text">{error}</p>
          </div>
        )}

        {/* Download and Details Link */}
        {presentation && (
          <div className="download-container" ref={downloadRef}>
            <p className="success-text">Presentation Updated Successfully!</p>
            <a
              href={`http://localhost:5000${presentation.download_url}`}
              download
              className="download-button"
            >
              Download Updated Presentation
            </a>
            {/* Link to Presentation Details */}
            <Link to={`/presentations/${presentation.id}`} className="details-link">
              View Presentation Details
            </Link>
          </div>
        )}
      </form>
    </div>
  );
};

export default ModifyPresentation;
