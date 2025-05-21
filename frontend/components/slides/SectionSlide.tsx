"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"

export default function SectionSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : ''
  };

  const titleClass = mini
    ? "text-lg font-bold"
    : "text-5xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  return (
    <div className={`w-full h-full flex flex-col items-center justify-center ${mini ? "p-2" : "p-10"}`}>
      <motion.div
        initial={mini ? {} : { opacity: 0, scale: 0.9 }}
        animate={mini ? {} : { opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <h2 className={titleClass}>{safeSlide.title}</h2>
        
        {safeSlide.content && !mini && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-4 text-xl text-gray-600"
          >
            {safeSlide.content}
          </motion.p>
        )}
      </motion.div>
    </div>
  )
} 