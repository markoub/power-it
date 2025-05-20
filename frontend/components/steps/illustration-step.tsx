"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Loader2, RefreshCw, Wand2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Presentation, Slide } from "@/lib/types"
import { api } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"

// Define API_URL to match the one used in the api.ts file
const API_URL = 'http://localhost:8000';

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
      // Generate a prompt if one doesn't exist
      const imagePrompt = slide.imagePrompt || generateImagePrompt(slide)

      // Update the slide with the prompt first
      updateSlide({
        ...slide,
        imagePrompt,
      })

      // Notify the user that image generation is starting
      toast({
        title: "Image generation requested",
        description: "The image for this slide is being generated..."
      });

      // Make API call to the backend to generate the image
      // This will work in both online and offline mode since the backend handles offline mode properly
      try {
        const response = await fetch(`${API_URL}/images`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            prompt: imagePrompt,
            size: "1024x1024"
          }),
          mode: 'cors',
        });
        
        if (!response.ok) {
          throw new Error(`Failed to generate image: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Format the image URL using the same helper function pattern from api.ts
        let imageUrl = data.image_url || '';
        if (imageUrl && !imageUrl.startsWith('http')) {
          imageUrl = `${API_URL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;
        }
        
        // Update the slide with the real image URL from the API
        updateSlide({
          ...slide,
          imagePrompt,
          imageUrl,
        });
      } catch (error) {
        console.error("API error generating image:", error);
        
        // If API call fails, still provide a fallback placeholder
        // This ensures the UI doesn't break if the backend is unreachable
        const fallbackImageUrl = `/placeholder.svg?height=400&width=600&query=${encodeURIComponent(imagePrompt)}`;
        
        updateSlide({
          ...slide,
          imagePrompt,
          imageUrl: fallbackImageUrl,
        });
        
        toast({
          title: "Using placeholder image",
          description: "Could not connect to image generation API. Using a placeholder instead.",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error("Error generating image:", error)
      toast({
        title: "Error",
        description: "Failed to generate image. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false)
      setGeneratingSlideId(null)
    }
  }

  const generateAllImages = async () => {
    setIsGenerating(true);

    try {
      // Call the API to run the images step
      const result = await api.runPresentationStep(String(presentation.id), "images");
      
      if (result) {
        toast({
          title: "Image generation started",
          description: "Images for all slides are being generated. This may take a minute..."
        });
        
        // Poll until the images are ready
        let imagesReady = false;
        let attempts = 0;
        const maxAttempts = 20; // Limit polling attempts
        
        while (!imagesReady && attempts < maxAttempts) {
          attempts++;
          
          // Wait 3 seconds between polls
          await new Promise(resolve => setTimeout(resolve, 3000));
          
          // Fetch the updated presentation
          const updatedPresentation = await api.getPresentation(String(presentation.id));
          
          if (updatedPresentation) {
            // Check if images step is completed
            const imagesStep = updatedPresentation.steps?.find(
              step => step.step === "images" && step.status === "completed"
            );
            
            if (imagesStep) {
              imagesReady = true;
              
              // Refresh the page to show the new images
              window.location.reload();
            }
          }
        }
        
        if (!imagesReady) {
          toast({
            title: "Taking longer than expected",
            description: "Image generation is still in progress. Please refresh the page in a minute.",
            variant: "destructive"
          });
        }
      }
    } catch (error) {
      console.error("Error generating images:", error);
      toast({
        title: "Error generating images",
        description: "Failed to generate images. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
      setGeneratingSlideId(null);
    }
  }

  // Check if there are no slides or if slides have no images yet
  const noSlides = presentation.slides.length === 0;
  const hasNoImages = presentation.slides.every(slide => !slide.imageUrl || slide.imageUrl === '');

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold gradient-text">Illustrations</h2>
          {!noSlides && (
            <Button
              onClick={generateAllImages}
              className="bg-primary hover:bg-primary-600 text-white"
              disabled={isGenerating}
              data-testid="run-images-button"
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
          )}
        </div>
        <p className="text-gray-600 mb-6">Generate or customize illustrations for each slide in your presentation.</p>

        {noSlides ? (
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <h3 className="text-lg font-medium text-gray-500 mb-2">No slides available</h3>
            <p className="text-gray-400 mb-6">Generate slides first before adding illustrations.</p>
          </div>
        ) : hasNoImages && !isGenerating ? (
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <h3 className="text-lg font-medium text-gray-700 mb-2">Ready to Generate Images</h3>
            <p className="text-gray-500 mb-6">
              Your slides are ready for illustrations. Click the button below to generate images for all slides.
            </p>
            <Button
              onClick={generateAllImages}
              className="bg-primary hover:bg-primary-600 text-white px-6"
              size="lg"
              data-testid="run-images-button"
            >
              <Wand2 size={16} className="mr-2" />
              Generate Images
            </Button>
          </div>
        ) : (
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
                          <>
                            <img
                              src={String(slide.imageUrl)}
                              alt={String(slide.title)}
                              className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                              onError={(e) => {
                                console.error(`Failed to load image for slide "${slide.title}":`, slide.imageUrl);
                                // Replace with a placeholder and show error info
                                e.currentTarget.onerror = null;
                                e.currentTarget.src = "/placeholder.svg";
                                
                                // Add error overlay
                                const target = e.currentTarget as HTMLImageElement;
                                target.style.opacity = "0.5";
                                
                                // Add an error indicator
                                const parent = target.parentElement;
                                if (parent) {
                                  const errorDiv = document.createElement('div');
                                  errorDiv.className = "absolute inset-0 flex items-center justify-center text-red-500 text-sm font-bold";
                                  errorDiv.textContent = "Image failed to load";
                                  parent.appendChild(errorDiv);
                                }
                              }}
                            />
                            <div className="absolute inset-0 opacity-0 hover:opacity-100 bg-black/70 transition-opacity duration-300 flex items-center justify-center text-white text-xs p-2 text-center overflow-auto">
                              <div>
                                <p className="font-bold mb-1">Image URL:</p>
                                <p className="break-all">{slide.imageUrl}</p>
                              </div>
                            </div>
                          </>
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
                            onClick={(e) => {
                              e.stopPropagation();
                              generateImage(slide);
                            }}
                            disabled={isGenerating}
                            className="flex-shrink-0"
                            data-testid="generate-image-button"
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
        )}
      </motion.div>
    </div>
  )
}
