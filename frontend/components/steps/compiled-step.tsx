"use client"

import { useState } from "react"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Presentation, Slide } from "@/lib/types"

interface CompiledStepProps {
  presentation: Presentation
  currentSlide: Slide | null
  setCurrentSlide: (slide: Slide | null) => void
  onContextChange: (context: "all" | "single") => void
}

export default function CompiledStep({
  presentation,
  currentSlide,
  setCurrentSlide,
  onContextChange,
}: CompiledStepProps) {
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    // Set context to "all" by default for the compiled view
    onContextChange("all")

    // If there's a current slide, find its index
    if (currentSlide) {
      const index = presentation.slides.findIndex((slide) => slide.id === currentSlide.id)
      if (index !== -1) {
        setCurrentIndex(index)
      }
    }
  }, [currentSlide, onContextChange, presentation.slides])

  const goToNextSlide = () => {
    if (currentIndex < presentation.slides.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setCurrentSlide(presentation.slides[currentIndex + 1])
    }
  }

  const goToPreviousSlide = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      setCurrentSlide(presentation.slides[currentIndex - 1])
    }
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h2 className="text-2xl font-bold mb-4 gradient-text">Compiled Presentation</h2>
        <p className="text-gray-600 mb-6">Preview your complete presentation with slides and illustrations combined.</p>

        {presentation.slides.length > 0 ? (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl shadow-lg p-8 aspect-[16/9] relative">
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentIndex}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="w-full h-full flex"
                >
                  <div className="w-1/2 pr-4 flex flex-col">
                    <h3 className="text-3xl font-bold mb-6 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                      {presentation.slides[currentIndex].title || `Slide ${currentIndex + 1}`}
                    </h3>
                    <div className="text-lg flex-1 overflow-auto">
                      {presentation.slides[currentIndex].content.split("\n").map((paragraph, index) => (
                        <motion.p
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="mb-3"
                        >
                          {paragraph}
                        </motion.p>
                      ))}
                    </div>
                  </div>
                  <div className="w-1/2 pl-4 flex items-center justify-center">
                    {presentation.slides[currentIndex].imageUrl ? (
                      <img
                        src={presentation.slides[currentIndex].imageUrl || "/placeholder.svg"}
                        alt={presentation.slides[currentIndex].title}
                        className="max-w-full max-h-full object-contain rounded-lg shadow-md"
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
                        No image available
                      </div>
                    )}
                  </div>
                </motion.div>
              </AnimatePresence>

              {/* Navigation buttons */}
              <div className="absolute bottom-4 left-0 right-0 flex justify-center items-center gap-4">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={goToPreviousSlide}
                  disabled={currentIndex === 0}
                  className="bg-white/80 backdrop-blur-sm hover:bg-white"
                >
                  <ChevronLeft size={18} />
                </Button>
                <span className="text-sm font-medium">
                  {currentIndex + 1} / {presentation.slides.length}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={goToNextSlide}
                  disabled={currentIndex === presentation.slides.length - 1}
                  className="bg-white/80 backdrop-blur-sm hover:bg-white"
                >
                  <ChevronRight size={18} />
                </Button>
              </div>
            </div>

            <div className="overflow-x-auto pb-4">
              <div className="flex gap-4">
                {presentation.slides.map((slide, index) => (
                  <Card
                    key={slide.id}
                    className={`flex-shrink-0 w-40 cursor-pointer transition-all ${
                      index === currentIndex ? "ring-2 ring-primary-500 scale-105" : "opacity-70 hover:opacity-100"
                    }`}
                    onClick={() => {
                      setCurrentIndex(index)
                      setCurrentSlide(slide)
                    }}
                  >
                    <CardContent className="p-2">
                      <div className="aspect-video bg-gray-100 rounded mb-2 overflow-hidden">
                        {slide.imageUrl ? (
                          <img
                            src={slide.imageUrl || "/placeholder.svg"}
                            alt={slide.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-xs text-gray-400">
                            No image
                          </div>
                        )}
                      </div>
                      <p className="text-xs font-medium truncate">{slide.title || `Slide ${index + 1}`}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <p className="text-gray-500">No slides to preview. Please create slides first.</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}
