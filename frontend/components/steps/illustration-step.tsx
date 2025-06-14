"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent, DialogTitle, DialogDescription, DialogHeader, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Loader2, RefreshCw, Wand2, ImageIcon } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Presentation, Slide } from "@/lib/types"
import { api } from "@/lib/api"
import { toast } from "@/hooks/use-toast"
import { ImagePlaceholder, getAspectRatioFromDimensions } from "@/components/ui/image-placeholder"

// Define API_URL to match the one used in the api.ts file
const API_URL = 'http://localhost:8000';

interface IllustrationStepProps {
  presentation: Presentation
  currentSlide: Slide | null
  setCurrentSlide: (slide: Slide | null) => void
  updateSlide: (slide: Slide) => void
  onContextChange: (context: "all" | "single") => void
  refreshPresentation?: () => Promise<Presentation | null>
}

export default function IllustrationStep({
  presentation,
  currentSlide,
  setCurrentSlide,
  updateSlide,
  onContextChange,
  refreshPresentation,
}: IllustrationStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatingSlideId, setGeneratingSlideId] = useState<string | null>(null)
  const [imageProvider, setImageProvider] = useState<"openai" | "gemini">("openai")

  useEffect(() => {
    // Set context to "single" when a slide is selected
    if (currentSlide) {
      onContextChange("single")
    } else {
      onContextChange("all")
    }
  }, [currentSlide, onContextChange])

  const generatePromptForSlide = (slide: Slide) => {
    const contentForPrompt = Array.isArray(slide.content) 
      ? slide.content.join(' ') 
      : (typeof slide.content === 'string' ? slide.content : '');
    
    return `Illustration for presentation slide about: ${slide.title}. ${contentForPrompt.substring(0, 100)}`
  }

  const generateImage = async (slide: Slide) => {
    setIsGenerating(true)
    setGeneratingSlideId(slide.id)

    try {
      // Generate a prompt if one doesn't exist
      const imagePrompt = slide.imagePrompt || generatePromptForSlide(slide)

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
            size: "1024x1024",
            provider: imageProvider
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
      // Call the API to run the images step with the selected provider
      const result = await api.runPresentationStep(String(presentation.id), "images", {
        image_provider: imageProvider
      });

      if (result) {
        toast({
          title: "Image generation started",
          description: "Images for all slides are being generated. This may take a minute..."
        });
        // Poll until images step is completed, updating slides as results appear
        let imagesReady = false;
        let attempts = 0;
        const maxAttempts = 20;

        const applyImageResults = (images: any[]) => {
          images.forEach((image: any) => {
            let url = image.image_url || '';
            if (url && !url.startsWith('http')) {
              url = `${API_URL}${url.startsWith('/') ? '' : '/'}${url}`;
            }

            if (typeof image.slide_index === 'number' && presentation.slides[image.slide_index]) {
              const slide = presentation.slides[image.slide_index];
              if (!slide.imageUrl) {
                updateSlide({ ...slide, imageUrl: url, imagePrompt: image.prompt || slide.imagePrompt });
              }
            }
          });
        };

        while (!imagesReady && attempts < maxAttempts) {
          attempts++;
          // Use shorter polling interval in offline/test mode for faster tests
          const pollInterval = process.env.NEXT_PUBLIC_POWERIT_OFFLINE === '1' || 
                              process.env.NODE_ENV === 'test' ? 500 : 3000;
          await new Promise(resolve => setTimeout(resolve, pollInterval));

          const updatedPresentation = await api.getPresentation(String(presentation.id));
          if (updatedPresentation) {
            const imagesStep = updatedPresentation.steps?.find(step => step.step === "images");
            if (imagesStep && imagesStep.result && Array.isArray(imagesStep.result.images)) {
              applyImageResults(imagesStep.result.images);
              if (imagesStep.status === "completed") {
                imagesReady = true;
                
                // Refresh main presentation data to update step status
                if (refreshPresentation) {
                  await refreshPresentation();
                }
              }
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
  const hasNoImages = presentation.slides.every(
    (slide) => !slide.imageUrl || slide.imageUrl === ""
  );
  
  // Check if images step is currently processing
  const imagesStep = presentation.steps?.find(step => step.step === 'images');
  const isStepProcessing = imagesStep?.status === 'processing';

  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedImageSlide, setSelectedImageSlide] = useState<Slide | null>(null);

  const regenerateImage = async (slide: Slide) => {
    const index = presentation.slides.findIndex((s) => s.id === slide.id);
    if (index === -1) return;
    setIsGenerating(true);
    setGeneratingSlideId(slide.id);
    const prompt = slide.imagePrompt || generatePromptForSlide(slide);

    try {
      const data = await api.regenerateImage(presentation.id, index, prompt, imageProvider);
      let imageUrl = data.image_url || "";
      if (imageUrl && !imageUrl.startsWith("http")) {
        imageUrl = `${API_URL}${imageUrl.startsWith("/") ? "" : "/"}${imageUrl}`;
      }
      updateSlide({ ...slide, imagePrompt: prompt, imageUrl });
    } catch (error) {
      console.error("Error regenerating image:", error);
      toast({
        title: "Error",
        description: "Failed to regenerate image.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
      setGeneratingSlideId(null);
    }
  };

  // Show processing state if images are being generated
  if (isStepProcessing) {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold mb-4 gradient-text">Generating Images</h2>
          <p className="text-muted-foreground mb-6">
            AI is creating custom illustrations for your slides based on their content.
          </p>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="flex items-center justify-center gap-3 text-primary-600 mb-4">
              <Loader2 size={32} className="animate-spin" />
              <h3 className="text-xl font-semibold">Generating Images...</h3>
            </div>
            <p className="text-muted-foreground mb-4">
              This process may take a few minutes as we create unique illustrations for each slide.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
              The AI is analyzing slide content and generating appropriate visual elements to enhance your presentation.
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold gradient-text">Illustrations</h2>
            <div className="flex items-center gap-4 mt-2">
              <Label htmlFor="provider-select" className="text-sm font-medium text-gray-700">
                Image Provider:
              </Label>
              <Select value={imageProvider} onValueChange={(value: "openai" | "gemini") => setImageProvider(value)}>
                <SelectTrigger id="provider-select" className="w-[180px]">
                  <SelectValue placeholder="Select provider" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openai">
                    <div className="flex items-center gap-2">
                      <ImageIcon size={14} />
                      OpenAI (GPT Image 1)
                    </div>
                  </SelectItem>
                  <SelectItem value="gemini">
                    <div className="flex items-center gap-2">
                      <ImageIcon size={14} />
                      Google Gemini (Imagen 3)
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {!noSlides && (
            <Button
              onClick={generateAllImages}
              className="bg-primary hover:bg-primary-600 text-white"
              disabled={isGenerating}
              data-testid="run-images-button-header"
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
        <p className="text-muted-foreground mb-6">Generate or customize illustrations for each slide in your presentation.</p>

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
              data-testid="run-images-button-center"
            >
              <Wand2 size={16} className="mr-2" />
              Generate Images
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {presentation.slides
                .filter((s) => s.imageUrl)
                .map((slide, index) => (
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
                      onClick={() => {
                        setCurrentSlide(slide);
                        setDialogOpen(true);
                      }}
                    >
                      <CardContent className="p-4">
                        <h3 className="font-semibold mb-2 truncate">{slide.title || `Slide ${index + 1}`}</h3>

                        <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden relative">
                          {slide.imageUrl ? (
                            <img 
                              src={String(slide.imageUrl)} 
                              alt={String(slide.title)} 
                              className="w-full h-full object-cover" 
                              onError={(e) => {
                                // If image fails to load, replace with placeholder
                                const target = e.target as HTMLImageElement;
                                target.style.display = 'none';
                                const placeholder = target.nextElementSibling as HTMLElement;
                                if (placeholder) placeholder.style.display = 'flex';
                              }}
                            />
                          ) : null}
                          <div 
                            className="w-full h-full items-center justify-center" 
                            style={{ display: slide.imageUrl ? 'none' : 'flex' }}
                          >
                            <ImagePlaceholder 
                              aspectRatio="landscape" 
                              text={slide.imagePrompt || "No image generated"}
                              className="w-full h-full"
                            />
                          </div>
                          {isGenerating && generatingSlideId === slide.id && (
                            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                              <div className="text-white text-center">
                                <Loader2 size={24} className="animate-spin mx-auto mb-2" />
                                <p className="text-sm">Generating...</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
            </AnimatePresence>
          </div>
        )}
      </motion.div>
      <Dialog
        open={dialogOpen}
        onOpenChange={(o) => {
          if (!o) {
            setDialogOpen(false);
            setCurrentSlide(null);
          }
        }}
      >
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>
              {currentSlide?.title || "Image Preview"}
            </DialogTitle>
            <DialogDescription>
              You can customize the prompt and regenerate this image
            </DialogDescription>
          </DialogHeader>
          
          {currentSlide && (
            <div className="space-y-4">
              <div className="max-h-[500px] overflow-auto flex justify-center">
                {currentSlide.imageUrl ? (
                  <>
                    <img 
                      src={String(currentSlide.imageUrl)} 
                      alt={currentSlide.title || "Slide image"} 
                      className="rounded object-contain max-h-[450px] max-w-full" 
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const placeholder = target.nextElementSibling as HTMLElement;
                        if (placeholder) placeholder.style.display = 'block';
                      }}
                    />
                    <div style={{ display: 'none' }} className="max-h-[450px] max-w-full">
                      <ImagePlaceholder 
                        aspectRatio="landscape" 
                        text={currentSlide.imagePrompt || "Image failed to load"}
                        className="h-[450px]"
                      />
                    </div>
                  </>
                ) : (
                  <ImagePlaceholder 
                    aspectRatio="landscape" 
                    text={currentSlide.imagePrompt || "No image generated"}
                    className="h-[450px]"
                  />
                )}
              </div>
              
              <div className="space-y-2">
                <label htmlFor="imagePrompt" className="text-sm font-medium text-gray-700">
                  Image prompt
                </label>
                <Textarea
                  id="imagePrompt"
                  value={currentSlide.imagePrompt || ""}
                  onChange={(e) => updateSlide({ ...currentSlide, imagePrompt: e.target.value })}
                  placeholder="Enter a detailed description of the image you want to generate..."
                  className="min-h-[120px] resize-y"
                />
              </div>
              
              <DialogFooter>
                <Button
                  onClick={() => regenerateImage(currentSlide)}
                  disabled={isGenerating}
                  className="bg-primary text-white"
                >
                  {isGenerating ? (
                    <span className="flex items-center gap-2">
                      <Loader2 size={16} className="animate-spin" />
                      Regenerating...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <RefreshCw size={16} />
                      Regenerate
                    </span>
                  )}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
