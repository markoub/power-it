"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

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
        className="text-center max-w-4xl"
      >
        <h2 className={titleClass}>{safeSlide.title}</h2>
        
        {safeSlide.content.trim() && (
          <motion.div
            initial={mini ? {} : { opacity: 0 }}
            animate={mini ? {} : { opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-4"
          >
            <MarkdownRenderer 
              content={safeSlide.content}
              mini={mini}
              animated={!mini}
              className={`text-center ${mini ? "prose-xs" : "prose-xl"} prose-headings:text-center prose-p:text-center`}
            />
          </motion.div>
        )}
      </motion.div>
    </div>
  )
} 