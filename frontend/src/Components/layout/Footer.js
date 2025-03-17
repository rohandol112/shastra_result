// src/Components/layout/Footer.js
import React from 'react';
import { motion } from 'framer-motion';
import { Github, Mail, Globe, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="w-full bg-[#0A0A0A] border-t border-orange-600/20 py-8">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Branding */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-orange-500 rounded-lg" />
              <span className="text-xl font-bold text-white">शस्त्र</span>
            </div>
            <p className="text-gray-400 text-sm">
              TCET's Shastra Coding Club - Result Processing Tool
            </p>
          </div>

          {/* Quick Links */}
          <div className="flex flex-col gap-4">
            <h3 className="text-white font-semibold">Quick Links</h3>
            <div className="flex flex-col gap-2">
              <FooterLink href="/docs">Documentation</FooterLink>
              <FooterLink href="/about">About</FooterLink>
              <FooterLink href="/contact">Contact</FooterLink>
            </div>
          </div>

          {/* Connect */}
          <div className="flex flex-col gap-4">
            <h3 className="text-white font-semibold">Connect</h3>
            <div className="flex gap-4">
              <motion.a
                href="https://github.com/yourusername"
                target="_blank"
                rel="noopener noreferrer"
                whileHover={{ scale: 1.1 }}
                className="text-gray-400 hover:text-white"
              >
                <Github className="w-5 h-5" />
              </motion.a>
              <motion.a
                href="mailto:contact@example.com"
                whileHover={{ scale: 1.1 }}
                className="text-gray-400 hover:text-white"
              >
                <Mail className="w-5 h-5" />
              </motion.a>
              <motion.a
                href="https://yourwebsite.com"
                target="_blank"
                rel="noopener noreferrer"
                whileHover={{ scale: 1.1 }}
                className="text-gray-400 hover:text-white"
              >
                <Globe className="w-5 h-5" />
              </motion.a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800">
          <p className="text-center text-gray-400 text-sm">
            © {new Date().getFullYear()} TCET's Shastra Coding Club. All rights reserved.
          </p>
          <p className="text-center text-gray-400 text-sm flex items-center justify-center">
            Made with <Heart className="w-4 h-4 text-red-500 mx-1" /> by Documentation Team 2024-25
          </p>
        </div>
      </div>
    </footer>
  );
};

const FooterLink = ({ href, children }) => (
  <motion.a
    href={href}
    className="text-gray-400 hover:text-white text-sm"
    whileHover={{ x: 5 }}
  >
    {children}
  </motion.a>
);

export default Footer;