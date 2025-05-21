"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"

export default function WelcomeSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : '',
    author: typeof slide.author === 'string' ? slide.author : ''
  };

  const titleClass = mini
    ? "text-xl font-bold mb-1"
    : "text-4xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const subtitleClass = mini
    ? "text-sm font-medium mb-1"
    : "text-2xl font-medium mb-6 text-gray-700"

  const authorClass = mini
    ? "text-xs italic mt-1"
    : "text-lg italic mt-6 text-gray-600"

  // Parse content to extract subtitle and author if they're embedded in content
  let subtitle = "";
  let author = safeSlide.author || "";
  
  const contentLines = safeSlide.content.split("\n").filter(line => line.trim() !== "");
  if (contentLines.length > 0) {
    subtitle = contentLines[0];
    if (contentLines.length > 1) {
      author = contentLines[contentLines.length - 1].replace(/^By\s+|^Author:\s+/i, "");
    }
  }

  return (
    <div className={`w-full h-full flex flex-col items-center justify-center text-center ${mini ? "p-2" : "p-10"}`}>
      <motion.h1
        initial={mini ? {} : { opacity: 0, y: -20 }}
        animate={mini ? {} : { opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className={titleClass}
      >
        {safeSlide.title}
      </motion.h1>
      
      {subtitle && (
        <motion.h2
          initial={mini ? {} : { opacity: 0, y: -10 }}
          animate={mini ? {} : { opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className={subtitleClass}
        >
          {subtitle}
        </motion.h2>
      )}
      
      {author && (
        <motion.p
          initial={mini ? {} : { opacity: 0 }}
          animate={mini ? {} : { opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className={authorClass}
        >
          By {author}
        </motion.p>
      )}
    </div>
  )
} 