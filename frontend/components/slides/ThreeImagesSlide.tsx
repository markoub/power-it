"use client"

import { motion } from "framer-motion"
import { SlideProps } from "./SlideBase"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

export default function ThreeImagesSlide({ slide, mini = false }: SlideProps) {
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
    : "text-3xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"

  const subtitleClass = mini
    ? "text-[6px] text-center mt-1"
    : "text-sm font-medium text-center mt-2"

  // Parse content to get image subtitles and additional info
  // Format expected: [Image1 title]\n[Image2 title]\n[Image3 title]\n[Optional extra content]
  const contentLines = safeSlide.content.split("\n").filter(line => line.trim() !== "");
  
  const subtitles = {
    image1: contentLines.length > 0 ? contentLines[0] : "Image 1",
    image2: contentLines.length > 1 ? contentLines[1] : "Image 2",
    image3: contentLines.length > 2 ? contentLines[2] : "Image 3",
  };
  
  // Get additional content after the image subtitles for markdown rendering
  const additionalContent = contentLines.length > 3 ? contentLines.slice(3).join("\n") : "";
  
  // Assumption: The image URLs would be stored in some specific way
  // Since the current slide type doesn't account for multiple images directly,
  // we'll make a best-effort approach:
  // 1. Use the main imageUrl for the first image
  // 2. For demo purposes, we'll simulate the others
  
  // In a real implementation, these would come from actual data
  // For the component to be fully functional, the slide schema would need to be updated
  const images = {
    image1: safeSlide.imageUrl || "",
    // In a real implementation, these would be proper properties of the slide
    image2: "",
    image3: "",
  };
  
  // Placeholder text for missing images in mini view
  const miniPlaceholderClass = "text-[6px] text-gray-400";

  return (
    <div className={`w-full h-full flex flex-col ${mini ? "p-1" : "p-6"}`}>
      <h3 className={titleClass}>{safeSlide.title}</h3>
      
      <div className={`grid grid-cols-3 gap-${mini ? "1" : "4"} flex-1`}>
        {/* Image 1 */}
        <motion.div 
          initial={mini ? {} : { opacity: 0, y: 20 }}
          animate={mini ? {} : { opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col"
        >
          <div className={`relative rounded-lg overflow-hidden ${mini ? "h-12" : "flex-1"}`}>
            {images.image1 ? (
              <img 
                src={images.image1} 
                alt={subtitles.image1}
                className="w-full h-full object-cover" 
              />
            ) : (
              <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                {mini ? <span className={miniPlaceholderClass}>Image 1</span> : "Image not available"}
              </div>
            )}
          </div>
          <p className={subtitleClass}>{subtitles.image1}</p>
        </motion.div>
        
        {/* Image 2 */}
        <motion.div 
          initial={mini ? {} : { opacity: 0, y: 20 }}
          animate={mini ? {} : { opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="flex flex-col"
        >
          <div className={`relative rounded-lg overflow-hidden ${mini ? "h-12" : "flex-1"}`}>
            {images.image2 ? (
              <img 
                src={images.image2} 
                alt={subtitles.image2}
                className="w-full h-full object-cover" 
              />
            ) : (
              <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                {mini ? <span className={miniPlaceholderClass}>Image 2</span> : "Image not available"}
              </div>
            )}
          </div>
          <p className={subtitleClass}>{subtitles.image2}</p>
        </motion.div>
        
        {/* Image 3 */}
        <motion.div 
          initial={mini ? {} : { opacity: 0, y: 20 }}
          animate={mini ? {} : { opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="flex flex-col"
        >
          <div className={`relative rounded-lg overflow-hidden ${mini ? "h-12" : "flex-1"}`}>
            {images.image3 ? (
              <img 
                src={images.image3} 
                alt={subtitles.image3}
                className="w-full h-full object-cover" 
              />
            ) : (
              <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                {mini ? <span className={miniPlaceholderClass}>Image 3</span> : "Image not available"}
              </div>
            )}
          </div>
          <p className={subtitleClass}>{subtitles.image3}</p>
        </motion.div>
      </div>
      
      {/* Additional content if any */}
      {additionalContent && !mini && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.4 }}
          className="mt-4"
        >
          <MarkdownRenderer 
            content={additionalContent}
            mini={mini}
            animated={!mini}
            className="prose-sm"
          />
        </motion.div>
      )}
    </div>
  )
} 