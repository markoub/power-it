"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"

export default function TableOfContentsSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : ''
  };

  const titleClass = mini
    ? "text-sm font-bold mb-2"
    : "text-3xl font-bold mb-6 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const sectionClass = mini
    ? "text-xs mb-1"
    : "text-xl mb-3"

  // Parse content to get sections
  const sections = safeSlide.content
    .split("\n")
    .filter(line => line.trim() !== "")
    .map(line => line.trim());

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "p-2" : "p-8"}`}>
      <motion.h2
        initial={mini ? {} : { opacity: 0, y: -10 }}
        animate={mini ? {} : { opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className={titleClass}
      >
        {safeSlide.title || "Table of Contents"}
      </motion.h2>

      <motion.div
        initial={mini ? {} : { opacity: 0 }}
        animate={mini ? {} : { opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex-1"
      >
        <ol className="list-decimal pl-6 space-y-2">
          {sections.map((section, index) => (
            <motion.li
              key={index}
              initial={mini ? {} : { opacity: 0, x: -10 }}
              animate={mini ? {} : { opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.1 * index + 0.3 }}
              className={sectionClass}
            >
              {section}
            </motion.li>
          ))}
        </ol>
        
        {sections.length === 0 && (
          <p className="text-gray-400 italic">
            {mini ? "No sections" : "No sections defined. Please add sections in the editor."}
          </p>
        )}
      </motion.div>
    </div>
  )
} 