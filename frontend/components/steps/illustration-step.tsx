"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Loader2, RefreshCw, Wand2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Presentation, Slide } from "@/lib/types"

interface IllustrationStepProps {
  presentation: Presentation
  currentSlide: Slide | null
  setCurrentSlide: (slide: Slide | null) => void
  updateSlide: (slide: Slide) => void
  onContextChange: (context: "all" | "single") => void
}

export default function IllustrationStep({
  presentation,
  currentSlide,
  setCurrentSlide,
  updateSlide,
  onContextChange,
}: IllustrationStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatingSlideId, setGeneratingSlideId] = useState<string | null>(null)

  useEffect(() => {
    // Set context to "single" when a slide is selected
    if (currentSlide) {
      onContextChange("single")
    } else {
      onContextChange("all")
    }
  }, [currentSlide, onContextChange])

  const generateImagePrompt = (slide: Slide) => {
    // In a real app, this might use AI to generate a better prompt
    return `Illustration for presentation slide about: ${slide.title}. ${slide.content.substring(0, 100)}`
  }

  const generateImage = async (slide: Slide) => {
    setIsGenerating(true)
    setGeneratingSlideId(slide.id)

    try {
      // Simulate API call to generate image
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Generate a prompt if one doesn't exist
      const imagePrompt = slide.imagePrompt || generateImagePrompt(slide)

      // In a real app, this would call an API to generate an image
      // For now, we'll use a placeholder
      const imageUrl = `/placeholder.svg?height=400&width=600&query=${encodeURIComponent(imagePrompt)}`

      // Update the slide with the image URL and prompt
      updateSlide({
        ...slide,
        imagePrompt,
        imageUrl,
      })
    } catch (error) {
      console.error("Error generating image:", error)
    } finally {
      setIsGenerating(false)
      setGeneratingSlideId(null)
    }
  }

  const generateAllImages = async () => {
    setIsGenerating(true)

    try {
      // Process slides one by one
      for (const slide of presentation.slides) {
        setGeneratingSlideId(slide.id)

        // Simulate API call to generate image
        await new Promise((resolve) => setTimeout(resolve, 800))

        // Generate a prompt if one doesn't exist
        const imagePrompt = slide.imagePrompt || generateImagePrompt(slide)

        // In a real app, this would call an API to generate an image
        // For now, we'll use a placeholder
        const imageUrl = `/placeholder.svg?height=400&width=600&query=${encodeURIComponent(imagePrompt)}`

        // Update the slide with the image URL and prompt
        updateSlide({
          ...slide,
          imagePrompt,
          imageUrl,
        })
      }
    } catch (error) {
      console.error("Error generating images:", error)
    } finally {
      setIsGenerating(false)
      setGeneratingSlideId(null)
    }
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold gradient-text">Illustrations</h2>
          <Button
            onClick={generateAllImages}
            className="bg-primary hover:bg-primary-600 text-white"
            disabled={isGenerating}
          >
            {isGenerating ? (
              <span className="flex items-center gap-2">
                <Loader2 size={16} className="animate-spin" />
                Generating...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Wand2 size={16} />
                Generate All Images
              </span>
            )}
          </Button>
        </div>
        <p className="text-gray-600 mb-6">Generate or customize illustrations for each slide in your presentation.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {presentation.slides.map((slide, index) => (
              <motion.div
                key={slide.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <Card
                  className={`overflow-hidden slide-card ${
                    currentSlide?.id === slide.id ? "ring-2 ring-primary-500" : ""
                  }`}
                  onClick={() => setCurrentSlide(slide)}
                >
                  <CardContent className="p-4">
                    <h3 className="font-semibold mb-2 truncate">{slide.title || `Slide ${index + 1}`}</h3>

                    <div className="aspect-video bg-gray-100 rounded-lg mb-3 overflow-hidden relative">
                      {slide.imageUrl ? (
                        <img
                          src={slide.imageUrl || "/placeholder.svg"}
                          alt={slide.title}
                          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          No image generated
                        </div>
                      )}

                      {isGenerating && generatingSlideId === slide.id && (
                        <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                          <div className="text-white text-center">
                            <Loader2 size={24} className="animate-spin mx-auto mb-2" />
                            <p className="text-sm">Generating...</p>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-medium text-gray-500">Image Prompt</label>
                      <div className="flex gap-2">
                        <Input
                          value={slide.imagePrompt || ""}
                          onChange={(e) => updateSlide({ ...slide, imagePrompt: e.target.value })}
                          placeholder="Enter image prompt"
                          className="text-sm"
                        />
                        <Button
                          size="icon"
                          variant="outline"
                          onClick={() => generateImage(slide)}
                          disabled={isGenerating}
                          className="flex-shrink-0"
                        >
                          <RefreshCw size={16} className={isGenerating ? "animate-spin" : ""} />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {presentation.slides.length === 0 && (
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <p className="text-gray-500">No slides to illustrate. Please create slides first.</p>
          </div>
        )}
      </motion.div>
    </div>
  )
}
