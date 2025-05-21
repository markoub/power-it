"use client"

import type { Slide } from "@/lib/types"
import SlideRenderer from "@/components/slides/SlideRenderer"

interface SlidePreviewProps {
  slide: Slide
  mini?: boolean
}

export default function SlidePreview({ slide, mini = false }: SlidePreviewProps) {
  return (
    <div className={`w-full h-full flex flex-col ${mini ? "" : "p-2"}`}>
      <SlideRenderer slide={slide} mini={mini} />
    </div>
  )
}
