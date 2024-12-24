// src/components/SlideConfig.jsx

import React from 'react';
import Select from 'react-select';
import '../styles/SlideConfig.css';

// Define supported layouts
const layoutOptions = [
  { value: 'title', label: 'Title Slide' },
  { value: 'bullet_points', label: 'Bullet Points' },
  { value: 'two_column', label: 'Two-Column Layout' },
  { value: 'content_with_image', label: 'Content with Image' },
];

const SlideConfig = ({ index, register, errors }) => {
  const handleChange = (selectedOption, setValue) => {
    setValue(`layouts.${index}.value`, selectedOption.value, {
      shouldValidate: true,
      shouldDirty: true,
    });
  };

  return (
    <div className="slide-config">
      <label className="slide-config-label">
        Slide {index + 1} Layout
      </label>
      <Select
        options={layoutOptions}
        defaultValue={layoutOptions[1]} // Default to 'Bullet Points'
        onChange={(selectedOption) =>
          register(`layouts.${index}.value`).onChange({
            target: { name: `layouts.${index}.value`, value: selectedOption.value },
          })
        }
        classNamePrefix="react-select"
      />
      {errors && errors.value && (
        <p className="error-message">{errors.value.message}</p>
      )}
    </div>
  );
};

export default SlideConfig;
