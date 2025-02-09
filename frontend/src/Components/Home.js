import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Terminal, Database } from 'lucide-react';
import { Link } from 'react-router-dom';

const Home = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.3,
        delayChildren: 0.2
      }
    }
  };

  const textRevealVariants = {
    hidden: { y: 100, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12
      }
    }
  };

  const floatingAnimation = {
    y: [-10, 10],
    transition: {
      y: {
        duration: 2,
        repeat: Infinity,
        repeatType: "reverse",
        ease: "easeInOut"
      }
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative min-h-screen bg-[#0A0A0A] text-white overflow-hidden"
    >
      {/* Enhanced neon background effect */}
      <motion.div
        animate={{
          background: [
            "radial-gradient(circle at 0% 0%, rgba(0, 255, 255, 0.15) 0%, transparent 50%)",
            "radial-gradient(circle at 100% 100%, rgba(255, 0, 255, 0.15) 0%, transparent 50%)",
            "radial-gradient(circle at 0% 100%, rgba(0, 255, 255, 0.15) 0%, transparent 50%)",
          ],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          repeatType: "reverse",
        }}
        className="absolute inset-0 z-0"
      />

      {/* Neon grid lines */}
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(0,255,255,0.1)_1px,transparent_1px),linear-gradient(0deg,rgba(255,0,255,0.1)_1px,transparent_1px)] bg-[size:40px_40px]" />

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-6 py-20 relative z-10">
        {/* Hero Section */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center text-center max-w-3xl mx-auto"
        >
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ 
              type: "spring",
              stiffness: 260,
              damping: 20,
              duration: 1.5
            }}
            className="w-20 h-20 bg-gradient-to-r from-cyan-500 to-fuchsia-500 rounded-full mb-8 shadow-[0_0_30px_rgba(0,255,255,0.5)]"
          />
          
          <motion.h1
            variants={textRevealVariants}
            className="text-5xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-fuchsia-400 bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(0,255,255,0.5)]"
          >
            Shastra Result Processing
          </motion.h1>
          
          <motion.p
            variants={textRevealVariants}
            className="text-lg text-cyan-200 mb-8 text-shadow-neon"
          >
            Automated solution for processing and cleaning HackerRank leaderboard data for Shastra results. 
            Streamline your workflow with our Jupyter Notebook scripts.
          </motion.p>

          <Link to="/upload">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              animate={{
                boxShadow: [
                  "0 0 0 0 rgba(0, 255, 255, 0)",
                  "0 0 30px 5px rgba(0, 255, 255, 0.5)",
                  "0 0 0 0 rgba(0, 255, 255, 0)"
                ]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse"
              }}
              className="px-8 py-3 bg-gradient-to-r from-cyan-600 to-fuchsia-600 rounded-lg font-medium text-lg border border-cyan-400/50 text-white shadow-neon"
            >
              Get Started
            </motion.button>
          </Link>
        </motion.div>

        {/* Workflow Steps */}
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {[
            {
              icon: <Terminal className="group-hover:text-cyan-300 transition-colors duration-300" />,
              step: "1",
              title: "Scrape HackerRank",
              description: "Extract user IDs and marks from the HackerRank leaderboard automatically."
            },
            {
              icon: <FileText className="group-hover:text-fuchsia-300 transition-colors duration-300" />,
              step: "2",
              title: "Clean CSV",
              description: "Remove '@' symbols from HackerRank IDs in your uploaded CSV file."
            },
            {
              icon: <Database className="group-hover:text-cyan-300 transition-colors duration-300" />,
              step: "3",
              title: "Merge Results",
              description: "Combine marks from scraped data into the cleaned CSV file."
            }
          ].map((card, index) => (
            <WorkflowCard key={index} {...card} delay={index * 0.2} floatingAnimation={floatingAnimation} />
          ))}
        </motion.div>
      </div>
    </motion.div>
  );
};

const WorkflowCard = ({ icon, step, title, description, delay, floatingAnimation }) => (
  <motion.div
    initial={{ opacity: 0, y: 50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5 }}
    whileHover={{ 
      scale: 1.05,
      transition: { duration: 0.2 }
    }}
    className="relative p-8 bg-black/40 rounded-xl border border-cyan-500/30 hover:border-fuchsia-500/30 transition-all group backdrop-blur-xl shadow-[0_0_20px_rgba(0,255,255,0.2)]"
  >
    <motion.div
      animate={floatingAnimation}
      className="w-12 h-12 bg-gradient-to-br from-cyan-600/20 to-fuchsia-600/20 rounded-lg flex items-center justify-center mb-4 border border-cyan-500/30 group-hover:border-fuchsia-500/30 transition-colors"
    >
      {icon}
    </motion.div>
    <motion.div className="text-sm text-fuchsia-400 mb-2 font-medium">
      Step {step}
    </motion.div>
    <motion.h3 className="text-xl font-semibold mb-2 text-cyan-100">
      {title}
    </motion.h3>
    <motion.p className="text-cyan-300">
      {description}
    </motion.p>
  </motion.div>
);

export default Home;