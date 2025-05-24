"use client";

import { useState } from "react";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2, Sparkles, Loader2, Edit3, Eye, FileText } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { Presentation, Slide } from "@/lib/types";
import SlideRenderer from "@/components/slides/SlideRenderer";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/use-toast";

interface SlidesStepProps {
  presentation: Presentation;
  currentSlide: Slide | null;
  setCurrentSlide: (slide: Slide | null) => void;
  updateSlide: (slide: Slide) => void;
  addNewSlide: () => void;
  deleteSlide: (slideId: string) => void;
  onContextChange: (context: "all" | "single") => void;
  refreshPresentation?: () => Promise<Presentation | null>;
}

// Slide type detection logic (matching SlideRenderer)
const detectSlideType = (slide: Slide): string => {
  const title = typeof slide.title === 'string' ? slide.title.toLowerCase() : '';
  const content = typeof slide.content === 'string' ? slide.content.toLowerCase() : '';
  
  if (title.includes("welcome") || title.includes("introduction") || title.match(/^\s*presentation|overview/i)) {
    return "Welcome";
  }
  
  if (title.includes("table of contents") || title.includes("agenda") || title.includes("overview")) {
    return "TableOfContents";
  }
  
  if (title.match(/^\s*section|part|chapter/i) || (title.length < 20 && content.length < 20)) {
    return "Section";
  }
  
  if (slide.imageUrl) {
    if (content.length < 100) {
      return "ImageFull";
    }
    
    if (content.match(/image\s*1.*image\s*2.*image\s*3/i) || 
        content.match(/figure\s*1.*figure\s*2.*figure\s*3/i)) {
      return "3Images";
    }
    
    if (content.match(/logo|brand|company|partner/i)) {
      return "ContentWithLogos";
    }
    
    return "ContentImage";
  }
  
  return "Content";
};

// Get slide type color and icon
const getSlideTypeInfo = (slideType: string) => {
  const typeMap: Record<string, { color: string; icon: any; label: string }> = {
    "Welcome": { color: "bg-purple-100 text-purple-700 border-purple-200", icon: Sparkles, label: "Welcome" },
    "TableOfContents": { color: "bg-blue-100 text-blue-700 border-blue-200", icon: FileText, label: "Table of Contents" },
    "Section": { color: "bg-green-100 text-green-700 border-green-200", icon: FileText, label: "Section" },
    "ContentImage": { color: "bg-orange-100 text-orange-700 border-orange-200", icon: FileText, label: "Content + Image" },
    "Content": { color: "bg-gray-100 text-gray-700 border-gray-200", icon: FileText, label: "Content" },
    "ImageFull": { color: "bg-pink-100 text-pink-700 border-pink-200", icon: FileText, label: "Full Image" },
    "3Images": { color: "bg-indigo-100 text-indigo-700 border-indigo-200", icon: FileText, label: "Three Images" },
    "ContentWithLogos": { color: "bg-yellow-100 text-yellow-700 border-yellow-200", icon: FileText, label: "Content + Logos" },
  };
  
  return typeMap[slideType] || typeMap["Content"];
};

export default function SlidesStep({
  presentation,
  currentSlide,
  setCurrentSlide,
  updateSlide,
  addNewSlide,
  deleteSlide,
  onContextChange,
  refreshPresentation,
}: SlidesStepProps) {
  const [viewMode, setViewMode] = useState<"preview" | "edit">("preview");
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    // Set context to "single" when a slide is selected
    if (currentSlide) {
      onContextChange("single");
    } else {
      onContextChange("all");
    }
  }, [currentSlide, onContextChange]);

  // Function to generate slides with AI
  const handleGenerateSlides = async () => {
    try {
      setIsGenerating(true);

      const presentationId = typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id;
      const result = await api.runPresentationStep(presentationId, "slides");

      if (result) {
        toast({
          title: "Slides generation started",
          description: "Your slides are being generated. This may take a minute...",
        });

        let slidesReady = false;
        let attempts = 0;
        const maxAttempts = 20;

        while (!slidesReady && attempts < maxAttempts) {
          attempts++;
          await new Promise((resolve) => setTimeout(resolve, 3000));

          const updatedPresentation = await api.getPresentation(presentationId);

          if (updatedPresentation) {
            const slidesStep = updatedPresentation.steps?.find(
              (step) => step.step === "slides" && step.status === "completed",
            );

            if (slidesStep) {
              slidesReady = true;

              if (refreshPresentation) {
                await refreshPresentation();
              } else {
                window.location.reload();
              }
            }
          }
        }

        if (!slidesReady) {
          toast({
            title: "Taking longer than expected",
            description: "Slides generation is still in progress. Please refresh the page in a minute.",
            variant: "destructive",
          });
        }
      }
    } catch (error) {
      console.error("Error generating slides:", error);
      toast({
        title: "Error generating slides",
        description: "Failed to generate slides. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const noSlides = presentation.slides.length === 0;

  if (noSlides) {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold mb-4 gradient-text">Slides</h2>
          <p className="text-gray-600 mb-6">
            Create and edit your presentation slides. Add titles and content for each slide.
          </p>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <h3 className="text-xl font-semibold mb-6">Generate Slides</h3>
            <p className="text-gray-600 mb-8">
              Your presentation needs slides. You can generate them automatically using AI based on your research.
            </p>

            <Button
              onClick={handleGenerateSlides}
              className="bg-primary hover:bg-primary-600 text-white px-6 py-2"
              disabled={isGenerating}
              data-testid="run-slides-button"
            >
              {isGenerating ? (
                <span className="flex items-center gap-2">
                  <Loader2 size={18} className="animate-spin" />
                  Generating Slides...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Sparkles size={18} />
                  Generate Slides
                </span>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-2xl font-bold mb-4 gradient-text">Slides</h2>
        <p className="text-gray-600 mb-6">
          Create and edit your presentation slides. Preview is optimized for readability and content flow.
        </p>

        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
          {/* Slide Navigation Sidebar */}
          <div className="xl:col-span-1 space-y-4">
            <div className="bg-white/90 backdrop-blur-sm p-4 rounded-xl shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Slides ({presentation.slides.length})</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={addNewSlide}
                  className="flex items-center gap-1 border-dashed"
                  data-testid="add-slide-button"
                >
                  <Plus size={14} />
                  Add
                </Button>
              </div>
              
              <div className="space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto pr-2">
                <AnimatePresence>
                  {presentation.slides.map((slide, index) => {
                    const slideType = detectSlideType(slide);
                    const typeInfo = getSlideTypeInfo(slideType);
                    const Icon = typeInfo.icon;
                    
                    return (
                      <motion.div
                        key={slide.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ duration: 0.2, delay: index * 0.02 }}
                      >
                        <Card
                          data-testid={`slide-thumbnail-${index}`}
                          className={`cursor-pointer transition-all duration-200 ${
                            currentSlide?.id === slide.id
                              ? "ring-2 ring-primary-500 bg-primary-50 border-primary-200"
                              : "hover:bg-gray-50 hover:border-gray-200"
                          }`}
                          onClick={() => setCurrentSlide(slide)}
                        >
                          <CardContent className="p-3">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center gap-2 min-w-0 flex-1">
                                <Icon size={12} className="text-gray-500 flex-shrink-0" />
                                <span className="font-medium truncate text-sm">
                                  {slide.title || `Slide ${index + 1}`}
                                </span>
                              </div>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6 rounded-full hover:bg-red-50 hover:text-red-500 flex-shrink-0"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  deleteSlide(slide.id);
                                }}
                              >
                                <Trash2 size={12} />
                              </Button>
                            </div>
                            
                            <Badge 
                              className={`text-xs px-2 py-0.5 mb-2 ${typeInfo.color}`}
                              variant="outline"
                            >
                              {typeInfo.label}
                            </Badge>
                            
                            <div className="h-12 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-md overflow-hidden p-1">
                              <div className="h-full w-full bg-white rounded-sm flex items-center justify-center">
                                <SlideRenderer slide={slide} mini />
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Main Preview/Edit Area */}
          <div className="xl:col-span-4">
            {currentSlide ? (
              <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100">
                {/* Header with slide info and mode toggle */}
                <div className="p-4 border-b border-gray-100">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {currentSlide.title || "Untitled Slide"}
                      </h3>
                      <Badge 
                        className={`${getSlideTypeInfo(detectSlideType(currentSlide)).color}`}
                        variant="outline"
                      >
                        {getSlideTypeInfo(detectSlideType(currentSlide)).label}
                      </Badge>
                    </div>
                    
                    <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as "preview" | "edit")}>
                      <TabsList className="bg-gray-100 p-1 rounded-lg">
                        <TabsTrigger 
                          value="preview" 
                          className="data-[state=active]:bg-white data-[state=active]:text-primary-600 rounded-md transition-all flex items-center gap-2"
                        >
                          <Eye size={16} />
                          Preview
                        </TabsTrigger>
                        <TabsTrigger 
                          value="edit" 
                          className="data-[state=active]:bg-white data-[state=active]:text-primary-600 rounded-md transition-all flex items-center gap-2"
                        >
                          <Edit3 size={16} />
                          Edit
                        </TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>
                </div>

                {/* Content Area */}
                <div className="p-6">
                  <AnimatePresence mode="wait">
                    {viewMode === "preview" ? (
                      <motion.div
                        key="preview"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                        className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-xl shadow-inner"
                      >
                        <div className="w-full flex items-center justify-center p-8">
                          <div 
                            className="w-full bg-white rounded-lg shadow-md overflow-hidden"
                            style={{ 
                              aspectRatio: '16/9',
                              minHeight: '400px',
                              maxHeight: '600px'
                            }}
                          >
                            <div className="w-full h-full overflow-y-auto">
                              <SlideRenderer slide={currentSlide} mini={false} />
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ) : (
                      <motion.div
                        key="edit"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                        className="space-y-6"
                      >
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-700">
                            Slide Title
                          </label>
                          <Input
                            value={currentSlide.title}
                            onChange={(e) =>
                              updateSlide({
                                ...currentSlide,
                                title: e.target.value,
                                fields: {
                                  ...currentSlide.fields,
                                  title: e.target.value,
                                },
                              })
                            }
                            placeholder="Enter slide title"
                            className="text-xl font-semibold border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                            data-testid="slide-title-input"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-gray-700">
                            Slide Content
                          </label>
                          <Textarea
                            value={
                              typeof currentSlide.content === "string"
                                ? currentSlide.content
                                : ""
                            }
                            onChange={(e) =>
                              updateSlide({
                                ...currentSlide,
                                content: e.target.value,
                                fields: {
                                  ...currentSlide.fields,
                                  content: e.target.value,
                                },
                              })
                            }
                            placeholder="Enter slide content"
                            rows={12}
                            className="resize-none border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                          />
                        </div>

                        {/* Live Preview in Edit Mode */}
                        <div className="bg-gray-50 rounded-lg p-4">
                          <h4 className="text-sm font-medium text-gray-700 mb-3">Live Preview</h4>
                          <div 
                            className="bg-white rounded-md shadow-sm border overflow-hidden"
                            style={{ aspectRatio: '16/9' }}
                          >
                            <SlideRenderer slide={currentSlide} mini={false} />
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-96 bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100 p-8">
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="text-center"
                >
                  <div className="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="h-8 w-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a slide to preview</h3>
                  <p className="text-gray-500 mb-6">Choose a slide from the sidebar to see its content and make edits</p>
                  <Button
                    onClick={addNewSlide}
                    className="bg-primary hover:bg-primary-600 text-white transition-all duration-300 shadow-md hover:shadow-primary-500/25"
                    data-testid="add-first-slide-button"
                  >
                    <Plus size={16} className="mr-2" />
                    Add Your First Slide
                  </Button>
                </motion.div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
