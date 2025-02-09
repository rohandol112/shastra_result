// src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Components/layout/Layout';
import Home from './Components/Home';
import FileUploadPage from './Components/forms/Fileupload';
import Docs from './Components/Docs';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<FileUploadPage />} />
          <Route path="/docs" element={<Docs />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;