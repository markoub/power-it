"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

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
        {safeSlide.content.trim() ? (
          <MarkdownRenderer 
            content={safeSlide.content}
            mini={mini}
            animated={!mini}
            className={mini ? "prose-xs" : "prose-lg"}
          />
        ) : (
          <p className="text-gray-400 italic">
            {mini ? "No sections" : "No sections defined. Please add sections in the editor."}
          </p>
        )}
      </motion.div>
    </div>
  )
} 