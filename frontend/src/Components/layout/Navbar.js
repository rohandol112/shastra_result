// src/Components/layout/Navbar.js
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Github, Menu, X } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false); // State for mobile menu

  return (
    <motion.nav 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="w-full bg-[#0A0A0A] border-b border-orange-600/20 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto flex justify-between items-center h-16 px-6">
        {/* Logo Area */}
        <Link to="/" className="flex items-center gap-3">
          <img src="/Light.png" alt="Logo" className="w-12 h-12" />
          <span className="text-xl font-bold text-white">शस्त्र</span>
        </Link>

        {/* Hamburger Icon */}
        <div className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X className="w-6 h-6 text-white" /> : <Menu className="w-6 h-6 text-white" />}
        </div>

        {/* Center Navigation */}
        <div className={`md:flex items-center gap-4 ${isOpen ? 'flex flex-col absolute top-16 left-0 w-full bg-[#0A0A0A] border-b border-orange-600/20' : 'hidden'} md:block`}>
          <Link 
            to="/" 
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white transition duration-200 ${location.pathname === '/' ? 'bg-gradient-to-r from-blue-600 to-orange-500' : 'bg-transparent text-gray-400 hover:bg-gray-600'}`}
          >
            Home
          </Link>
          <Link 
            to="/upload" 
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white transition duration-200 ${location.pathname === '/upload' ? 'bg-gradient-to-r from-blue-600 to-orange-500' : 'bg-transparent text-gray-400 hover:bg-gray-600'}`}
          >
            Upload
          </Link>
          <Link 
            to="/docs" 
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white transition duration-200 ${location.pathname === '/docs' ? 'bg-gradient-to-r from-blue-600 to-orange-500' : 'bg-transparent text-gray-400 hover:bg-gray-600'}`}
          >
            Docs
          </Link>
        </div>

        {/* Right Side */}
        <div className="flex items-center gap-4">
          <motion.a
            href="https://github.com/rohandol112/shastra-results-process"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-blue-900/20 rounded-lg text-blue-400 hover:bg-blue-900/30 transition-colors"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Github className="w-4 h-4" />
            <span className="hidden md:inline">GitHub</span>
          </motion.a>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;