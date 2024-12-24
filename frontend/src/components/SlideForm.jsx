// src/components/SlideForm.jsx

import React, { useState, useRef, useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import Select from 'react-select';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import SlideConfig from './SlideConfig';
import axios from 'axios';
import '../styles/SlideForm.css';
import { Link } from 'react-router-dom';


// Define supported layouts
const layoutOptions = [
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

const SlideForm = () => {
    const [downloadUrl, setDownloadUrl] = useState('');
    const [presentationId, setPresentationId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const downloadRef = useRef(null);


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
        if (downloadUrl && downloadRef.current) {
            downloadRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [downloadUrl]);

    React.useEffect(() => {
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


    const onSubmit = async (data) => {
        setLoading(true);
        setError(null);
        setDownloadUrl('');
        setPresentationId('');

        try {
            const payload = {
                topic: data.topic,
                num_slides: data.num_slides,
                theme: data.theme,
                layouts: data.layouts.map((layout) => layout.value),
            };

            // Replace with your backend API URL
            const response = await axios.post(
                'http://localhost:5000/api/v1/presentations',
                payload
            );

            setPresentationId(response.data.id);
            setDownloadUrl(`http://localhost:5000${response.data.download_url}`);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.error || 'An error occurred while generating slides.'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="slide-form-container">
            <h1 className="slide-form-title">Slide Generator</h1>
            <form onSubmit={handleSubmit(onSubmit)} className="slide-form">
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
                        disabled={loading}
                        className="submit-button"
                    >
                        {loading ? 'Generating...' : 'Generate Slides'}
                    </button>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="error-container">
                        <p className="error-text">{error}</p>
                    </div>
                )}

                {/* Download Link */}
                {downloadUrl && (
                    <div className="download-container" ref={downloadRef}>
                        <p className="success-text">Presentation Created Successfully!</p>
                        <a
                            href={downloadUrl}
                            download
                            className="download-button"
                        >
                            Download Presentation
                        </a>
                        {/* Link to Presentation Details */}
                        <Link to={`/presentations/${presentationId}`} className="details-link">
                            View Presentation Details
                        </Link>
                    </div>
                )}

            </form>
        </div>
    );
};

export default SlideForm;
