"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"

export default function ContentSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : ''
  };

  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : "text-3xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const contentClass = mini ? "text-[8px] line-clamp-3" : "text-lg"

  const paragraphs = safeSlide.content.split("\n").filter((p) => p.trim() !== "")
  
  // Check if content has bullet points and render them appropriately
  const hasBulletPoints = paragraphs.some(p => p.trim().startsWith("•") || p.trim().startsWith("-") || p.trim().startsWith("*"));

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "p-1" : "p-8"}`}>
      <h3 className={titleClass}>{safeSlide.title}</h3>
      
      <div className={`${contentClass} ${mini ? "" : "flex-1"}`}>
        {hasBulletPoints ? (
          <ul className={`list-disc pl-5 ${mini ? "space-y-0" : "space-y-2"}`}>
            {paragraphs.map((paragraph, index) => {
              // Strip leading bullet characters for proper HTML list rendering
              const content = paragraph.trim().replace(/^[•\-*]\s*/, "");
              
              return (
                <motion.li
                  key={index}
                  initial={mini ? {} : { opacity: 0, x: 10 }}
                  animate={mini ? {} : { opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className={mini ? "line-clamp-1" : ""}
                >
                  {content}
                </motion.li>
              );
            })}
          </ul>
        ) : (
          paragraphs.map((paragraph, index) => (
            <motion.p
              key={index}
              initial={mini ? {} : { opacity: 0, y: 10 }}
              animate={mini ? {} : { opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={mini ? "line-clamp-1" : "mb-3"}
            >
              {paragraph}
            </motion.p>
          ))
        )}
        
        {paragraphs.length === 0 && (
          <p className="text-gray-400 italic">
            {mini ? "Empty slide" : "This slide is empty. Add some content in the editor."}
          </p>
        )}
      </div>
    </div>
  )
} 