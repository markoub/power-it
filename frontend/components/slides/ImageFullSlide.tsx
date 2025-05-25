"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

export default function ImageFullSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : '',
    imageUrl: typeof slide.imageUrl === 'string' ? slide.imageUrl : '',
    imagePrompt: typeof slide.imagePrompt === 'string' ? slide.imagePrompt : ''
  };

  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : "text-3xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const explanationClass = mini
    ? "mt-1"
    : "mt-3 bg-white/80 backdrop-blur-sm p-3 rounded-md shadow-sm"

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "p-1" : "p-4"}`}>
      <h3 className={titleClass}>{safeSlide.title}</h3>
      
      <div className={`relative flex-1 ${mini ? "mt-1" : "mt-2"} flex flex-col`}>
        <div className={`relative flex-1 rounded-lg overflow-hidden ${mini ? "" : "mb-3"}`}>
          {safeSlide.imageUrl ? (
            <img
              src={safeSlide.imageUrl}
              alt={safeSlide.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400">
              {mini ? "No image" : (safeSlide.imagePrompt || "No image available")}
            </div>
          )}
        </div>
        
        {safeSlide.content.trim() && (
          <motion.div
            initial={mini ? {} : { opacity: 0, y: 10 }}
            animate={mini ? {} : { opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className={explanationClass}
          >
            <MarkdownRenderer 
              content={safeSlide.content}
              mini={mini}
              animated={!mini}
              className={mini ? "line-clamp-2 prose-xs" : "prose-sm"}
            />
          </motion.div>
        )}
      </div>
    </div>
  )
} 