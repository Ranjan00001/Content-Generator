// src/App.jsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SlideForm from './components/SlideForm';
import PresentationDetails from './components/PresentationDetails';
import ModifyPresentation from './components/ModifyPresentation';
// import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<SlideForm />} />
          <Route path="/home" element={<SlideForm />} /> {/* New Route */}
          <Route path="/presentations/:id" element={<PresentationDetails />} />
          <Route path="/presentations/:id/modify" element={<ModifyPresentation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
