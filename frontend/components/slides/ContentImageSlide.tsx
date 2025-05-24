"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"

export default function ContentImageSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid strings for title and content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: typeof slide.content === 'string' ? slide.content : '',
    imageUrl: typeof slide.imageUrl === 'string' ? slide.imageUrl : '',
    imagePrompt: typeof slide.imagePrompt === 'string' ? slide.imagePrompt : ''
  };

  // Calculate text size based on content length
  const contentLength = safeSlide.content.length;
  const isLongContent = contentLength > 500;
  
  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : isLongContent 
      ? "text-2xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
      : "text-3xl font-bold mb-3 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const subtitleClass = mini
    ? "text-[8px] font-medium mb-1"
    : isLongContent
      ? "text-lg font-medium mb-2 text-gray-700"
      : "text-xl font-medium mb-4 text-gray-700"

  const contentClass = mini 
    ? "text-[8px] line-clamp-3" 
    : isLongContent
      ? "text-base leading-relaxed"
      : "text-lg"

  // Parse content to potentially extract subtitle
  let subtitle = "";
  let mainContent = safeSlide.content;
  
  const contentLines = safeSlide.content.split("\n").filter(line => line.trim() !== "");
  if (contentLines.length > 0 && !safeSlide.title.includes(contentLines[0])) {
    // Use first line as subtitle if it doesn't appear to be part of the title
    subtitle = contentLines[0];
    mainContent = contentLines.slice(1).join("\n");
  }

  const contentParagraphs = mainContent.split("\n").filter(p => p.trim() !== "");

  return (
    <div className={`w-full h-full flex ${mini ? "flex-col p-1" : "p-6"}`}>
      <div className={mini ? "w-full mb-1" : "w-1/2 pr-4 flex flex-col h-full"}>
        <h3 className={titleClass}>{safeSlide.title}</h3>
        
        {subtitle && (
          <h4 className={subtitleClass}>{subtitle}</h4>
        )}
        
        <div className={`${contentClass} ${mini ? "" : "flex-1 overflow-y-auto pr-2"}`}>
          {contentParagraphs.map((paragraph, index) => (
            <motion.p
              key={index}
              initial={mini ? {} : { opacity: 0, y: 10 }}
              animate={mini ? {} : { opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={mini ? "line-clamp-1" : isLongContent ? "mb-2" : "mb-3"}
            >
              {paragraph}
            </motion.p>
          ))}
          
          {contentParagraphs.length === 0 && (
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