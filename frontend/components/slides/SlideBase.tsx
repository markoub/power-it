"use client"

import { motion } from "framer-motion"
import type { Slide as SlideType } from "@/lib/types"

export interface SlideProps {
  slide: SlideType;
  mini?: boolean;
}

export default function SlideBase({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : ''
  };
  
  return (
    <div className={`w-full h-full flex flex-col ${mini ? "" : "p-6"}`}>
      <p className="text-gray-400 italic">
        {mini ? "Base slide" : "This is a base slide component that should be extended."}
      </p>
    </div>
  )
} 