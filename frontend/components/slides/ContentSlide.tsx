"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

export default function ContentSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: slide.content || ''
  };

  // Calculate text size based on content length (convert to string for length calculation)
  const contentForLength = Array.isArray(safeSlide.content) 
    ? safeSlide.content.join(' ') 
    : safeSlide.content;
  const contentLength = contentForLength.length;
  const isLongContent = contentLength > 800;
  const isVeryLongContent = contentLength > 1500;

  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : isVeryLongContent
      ? "text-2xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
      : isLongContent
        ? "text-3xl font-bold mb-3 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
        : "text-3xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  // Handle empty content
  const isEmpty = Array.isArray(safeSlide.content) 
    ? safeSlide.content.length === 0 || safeSlide.content.every(item => !item?.trim())
    : !safeSlide.content?.trim();

  if (isEmpty) {
    return (
      <div className={`w-full h-full flex flex-col ${mini ? "p-1" : "p-8"}`}>
        <h3 className={titleClass}>{safeSlide.title}</h3>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-400 italic">
            {mini ? "Empty slide" : "This slide is empty. Add some content in the editor."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "p-1" : "p-8"}`}>
      <h3 className={titleClass}>{safeSlide.title}</h3>
      
      <div className={`${mini ? "" : "flex-1 overflow-y-auto pr-2"}`}>
        <MarkdownRenderer 
          content={safeSlide.content}
          mini={mini}
          animated={!mini}
          className={
            mini ? "line-clamp-3" : 
            isVeryLongContent ? "prose-sm" : 
            isLongContent ? "prose-base" : "prose-lg"
          }
        />
      </div>
    </div>
  )
} 