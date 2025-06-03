import React from 'react'
import { ImageIcon } from 'lucide-react'

type AspectRatio = 'square' | 'landscape' | 'portrait'

interface ImagePlaceholderProps {
  aspectRatio?: AspectRatio
  text?: string
  className?: string
}

const aspectRatioClasses: Record<AspectRatio, string> = {
  square: 'aspect-square',
  landscape: 'aspect-video',
  portrait: 'aspect-[3/4]'
}

const aspectRatioSizes: Record<AspectRatio, { width: number; height: number }> = {
  square: { width: 400, height: 400 },
  landscape: { width: 600, height: 338 },
  portrait: { width: 300, height: 400 }
}

export function ImagePlaceholder({ 
  aspectRatio = 'landscape', 
  text = 'Image placeholder',
  className = '' 
}: ImagePlaceholderProps) {
  const size = aspectRatioSizes[aspectRatio]
  
  return (
    <div 
      className={`
        relative overflow-hidden rounded-lg
        bg-gradient-to-br from-gray-100 to-gray-200
        flex flex-col items-center justify-center
        ${aspectRatioClasses[aspectRatio]}
        ${className}
      `}
    >
      <div className="absolute inset-0 opacity-5">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>
      
      <div className="relative z-10 flex flex-col items-center gap-3 text-gray-400">
        <div className="rounded-full bg-white/80 p-4 shadow-sm">
          <ImageIcon size={32} className="text-gray-500" />
        </div>
        <div className="text-center px-4">
          <p className="text-sm font-medium text-gray-600">{text}</p>
          <p className="text-xs text-gray-500 mt-1">
            {size.width} × {size.height}px
          </p>
        </div>
      </div>
      
      <div className="absolute bottom-2 right-2 text-xs text-gray-400 bg-white/70 px-2 py-1 rounded">
        {aspectRatio}
      </div>
    </div>
  )
}

export function getAspectRatioFromDimensions(width?: number, height?: number): AspectRatio {
  if (!width || !height) return 'landscape'
  
  const ratio = width / height
  
  if (Math.abs(ratio - 1) < 0.1) return 'square'
  if (ratio > 1.3) return 'landscape'
  return 'portrait'
}