"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

export default function ContentWithLogosSlide({ slide, mini = false }: SlideProps) {
  // Ensure we always have valid content
  const safeSlide = {
    ...slide,
    title: typeof slide.title === 'string' ? slide.title : '',
    content: slide.content || '',
    imageUrl: typeof slide.imageUrl === 'string' ? slide.imageUrl : '',
    imagePrompt: typeof slide.imagePrompt === 'string' ? slide.imagePrompt : ''
  };

  const titleClass = mini
    ? "text-xs font-semibold mb-1"
    : "text-3xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  // Handle empty content
  const isEmpty = Array.isArray(safeSlide.content) 
    ? safeSlide.content.length === 0 || safeSlide.content.every(item => !item?.trim())
    : !safeSlide.content?.trim();

  // In a real implementation, we would get logo URLs from proper slide properties
  // For this demo, we'll use the main imageUrl as the first logo
  // And provide placeholders for the others
  const logos = {
    logo1: safeSlide.imageUrl || "",
    logo2: "",
    logo3: "",
  };

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "p-1" : "p-6"}`}>
      <h3 className={titleClass}>{safeSlide.title}</h3>
      
      <div className="flex flex-1">
        <div className={`${mini ? "w-3/4" : "w-2/3"}`}>
          {!isEmpty ? (
            <MarkdownRenderer 
              content={safeSlide.content}
              mini={mini}
              animated={!mini}
              className={mini ? "line-clamp-3" : "prose-lg"}
            />
          ) : (
            <p className="text-gray-400 italic">
              {mini ? "Empty slide" : "This slide is empty. Add some content in the editor."}
            </p>
          )}
        </div>
        
        <div className={`${mini ? "w-1/4 pl-1" : "w-1/3 pl-6"} flex flex-col justify-center space-y-${mini ? "1" : "4"}`}>
          {/* Logo 1 */}
          {logos.logo1 ? (
            <div className={`bg-white rounded-lg shadow-sm ${mini ? "p-0.5" : "p-2"} flex items-center justify-center`}>
              <img 
                src={logos.logo1} 
                alt="Logo 1" 
                className="max-w-full max-h-full object-contain" 
              />
            </div>
          ) : (
            <div className={`bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 ${mini ? "h-5 text-[6px]" : "h-16 text-sm"}`}>
              Logo 1
            </div>
          )}
          
          {/* Logo 2 */}
          {logos.logo2 ? (
            <div className={`bg-white rounded-lg shadow-sm ${mini ? "p-0.5" : "p-2"} flex items-center justify-center`}>
              <img 
                src={logos.logo2} 
                alt="Logo 2" 
                className="max-w-full max-h-full object-contain" 
              />
            </div>
          ) : (
            <div className={`bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 ${mini ? "h-5 text-[6px]" : "h-16 text-sm"}`}>
              Logo 2
            </div>
          )}
          
          {/* Logo 3 */}
          {logos.logo3 ? (
            <div className={`bg-white rounded-lg shadow-sm ${mini ? "p-0.5" : "p-2"} flex items-center justify-center`}>
              <img 
                src={logos.logo3} 
                alt="Logo 3" 
                className="max-w-full max-h-full object-contain" 
              />
            </div>
          ) : (
            <div className={`bg-gray-100 rounded-lg flex items-center justify-center text-gray-400 ${mini ? "h-5 text-[6px]" : "h-16 text-sm"}`}>
              Logo 3
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 