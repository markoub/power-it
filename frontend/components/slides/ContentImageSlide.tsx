"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

export default function ContentImageSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: slide.content || '',
    imageUrl: typeof slide.imageUrl === 'string' ? slide.imageUrl : '',
    imagePrompt: typeof slide.imagePrompt === 'string' ? slide.imagePrompt : ''
  };

  // Calculate text size based on content length (convert to string for length calculation)
  const contentForLength = Array.isArray(safeSlide.content) 
    ? safeSlide.content.join(' ') 
    : safeSlide.content;
  const contentLength = contentForLength.length;
  const isLongContent = contentLength > 500;
  
  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : isLongContent 
      ? "text-2xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
      : "text-3xl font-bold mb-3 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  // Handle empty content
  const isEmpty = Array.isArray(safeSlide.content) 
    ? safeSlide.content.length === 0 || safeSlide.content.every(item => !item?.trim())
    : !safeSlide.content?.trim();

  return (
    <div className={`w-full h-full flex ${mini ? "flex-col p-1" : "p-6"}`}>
      <div className={mini ? "w-full mb-1" : "w-1/2 pr-4 flex flex-col h-full"}>
        <h3 className={titleClass}>{safeSlide.title}</h3>
        
        <div className={`${mini ? "" : "flex-1 overflow-y-auto pr-2"}`}>
          {!isEmpty ? (
            <MarkdownRenderer 
              content={safeSlide.content}
              mini={mini}
              animated={!mini}
              className={
                mini ? "line-clamp-3" : 
                isLongContent ? "prose-base" : "prose-lg"
              }
            />
          ) : (
            <p className="text-gray-400 italic">
              {mini ? "Empty content" : "This slide has no content. Add some content in the editor."}
            </p>
          )}
        </div>
      </div>
      
      <div className={mini ? "w-full h-20" : "w-1/2 pl-4 flex items-center justify-center"}>
        {safeSlide.imageUrl ? (
          <img
            src={safeSlide.imageUrl}
            alt={safeSlide.title}
            className="max-w-full max-h-full object-contain rounded-lg shadow-md"
          />
        ) : (
          <div className={`w-full ${mini ? "h-16" : "h-full"} bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 ${mini ? "text-[8px]" : ""}`}>
            {safeSlide.imagePrompt || "No image available"}
          </div>
        )}
      </div>
    </div>
  )
} 