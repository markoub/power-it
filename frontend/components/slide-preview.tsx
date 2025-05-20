"use client"

import type { Slide } from "@/lib/types"
import { motion } from "framer-motion"

interface SlidePreviewProps {
  slide: Slide
  mini?: boolean
}

export default function SlidePreview({ slide, mini = false }: SlidePreviewProps) {
  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : "text-3xl font-bold mb-6 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const contentClass = mini ? "text-[8px] line-clamp-3" : "text-lg"

  const paragraphs = slide.content.split("\n").filter((p) => p.trim() !== "")

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "" : "p-6"}`}>
      <h3 className={titleClass}>{slide.title}</h3>
      <div className={contentClass}>
        {paragraphs.map((paragraph, index) => (
          <motion.p
            key={index}
            initial={mini ? {} : { opacity: 0, y: 10 }}
            animate={mini ? {} : { opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className={mini ? "line-clamp-1" : "mb-3"}
          >
            {paragraph}
          </motion.p>
        ))}
        {paragraphs.length === 0 && (
          <p className="text-gray-400 italic">
            {mini ? "Empty slide" : "This slide is empty. Add some content in the editor."}
          </p>
        )}
      </div>
    </div>
  )
}
