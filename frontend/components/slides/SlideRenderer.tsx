"use client"

import { SlideProps } from "./SlideBase"
import WelcomeSlide from "./WelcomeSlide"
import TableOfContentsSlide from "./TableOfContentsSlide"
import SectionSlide from "./SectionSlide"
import ContentImageSlide from "./ContentImageSlide"
import ContentSlide from "./ContentSlide"
import ImageFullSlide from "./ImageFullSlide"
import ThreeImagesSlide from "./ThreeImagesSlide"
import ContentWithLogosSlide from "./ContentWithLogosSlide"

// Define slide type detection logic
const detectSlideType = (slide: SlideProps["slide"]): string => {
  const title = typeof slide.title === 'string' ? slide.title.toLowerCase() : '';
  const content = typeof slide.content === 'string' ? slide.content.toLowerCase() : '';
  
  // Check for specific slide types based on title and content patterns
  if (title.includes("welcome") || title.includes("introduction") || title.match(/^\s*presentation|overview/i)) {
    return "Welcome";
  }
  
  if (title.includes("table of contents") || title.includes("agenda") || title.includes("overview")) {
    return "TableOfContents";
  }
  
  if (title.match(/^\s*section|part|chapter/i) || (title.length < 20 && content.length < 20)) {
    return "Section";
  }
  
  // Check for image-based slides
  if (slide.imageUrl) {
    if (content.length < 100) {
      return "ImageFull";
    }
    
    // If content has references to multiple images (like Image 1, Image 2, etc.)
    if (content.match(/image\s*1.*image\s*2.*image\s*3/i) || 
        content.match(/figure\s*1.*figure\s*2.*figure\s*3/i)) {
      return "3Images";
    }
    
    if (content.match(/logo|brand|company|partner/i)) {
      return "ContentWithLogos";
    }
    
    return "ContentImage";
  }
  
  // Default to Content slide
  return "Content";
};

export default function SlideRenderer({ slide, mini = false }: SlideProps) {
  // Detect the slide type
  const slideType = detectSlideType(slide);
  
  // Render appropriate component based on slide type
  switch (slideType) {
    case "Welcome":
      return <WelcomeSlide slide={slide} mini={mini} />;
    case "TableOfContents":
      return <TableOfContentsSlide slide={slide} mini={mini} />;
    case "Section":
      return <SectionSlide slide={slide} mini={mini} />;
    case "ContentImage":
      return <ContentImageSlide slide={slide} mini={mini} />;
    case "ImageFull":
      return <ImageFullSlide slide={slide} mini={mini} />;
    case "3Images":
      return <ThreeImagesSlide slide={slide} mini={mini} />;
    case "ContentWithLogos":
      return <ContentWithLogosSlide slide={slide} mini={mini} />;
    case "Content":
    default:
      return <ContentSlide slide={slide} mini={mini} />;
  }
} 