"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

export default function WelcomeSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: slide.content || ''
  };

  const titleClass = mini
    ? "text-xl font-bold mb-1"
    : "text-4xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  // Handle empty content
  const isEmpty = Array.isArray(safeSlide.content) 
    ? safeSlide.content.length === 0 || safeSlide.content.every(item => !item?.trim())
    : !safeSlide.content?.trim();

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
      
      {!isEmpty && (
        <motion.div
          initial={mini ? {} : { opacity: 0, y: -10 }}
          animate={mini ? {} : { opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-4xl"
        >
          <MarkdownRenderer 
            content={safeSlide.content}
            mini={mini}
            animated={!mini}
            className={`text-center ${mini ? "prose-xs" : "prose-xl"} prose-headings:text-center prose-p:text-center`}
          />
        </motion.div>
      )}
    </div>
  )
} 