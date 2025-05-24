"use client";

import { useState } from "react";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Trash2, Sparkles, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { Presentation, Slide } from "@/lib/types";
import SlidePreview from "@/components/slide-preview";
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
  const [activeTab, setActiveTab] = useState("edit");
  const [isGenerating, setIsGenerating] = useState(false);
  const [numSlides, setNumSlides] = useState(10); // Default number of slides to generate

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

      // Call the API to run the slides step
      const presentationId = typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id;
      const result = await api.runPresentationStep(presentationId, "slides");

      if (result) {
        toast({
          title: "Slides generation started",
          description:
            "Your slides are being generated. This may take a minute...",
        });

        // Poll until the slides are ready
        let slidesReady = false;
        let attempts = 0;
        const maxAttempts = 20; // Limit polling attempts

        while (!slidesReady && attempts < maxAttempts) {
          attempts++;

          // Wait 3 seconds between polls
          await new Promise((resolve) => setTimeout(resolve, 3000));

          // Fetch the updated presentation
          const updatedPresentation = await api.getPresentation(
            presentationId
          );

          if (updatedPresentation) {
            // Check if slides step is completed
            const slidesStep = updatedPresentation.steps?.find(
              (step) => step.step === "slides" && step.status === "completed",
            );

            if (slidesStep) {
              slidesReady = true;

              // Refresh presentation data to update slides and step status
              if (refreshPresentation) {
                await refreshPresentation();
              } else {
                // Fallback to page reload if refresh function not available
                window.location.reload();
              }
            }
          }
        }

        if (!slidesReady) {
          toast({
            title: "Taking longer than expected",
            description:
              "Slides generation is still in progress. Please refresh the page in a minute.",
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

  // Check if there are no slides yet
  const noSlides = presentation.slides.length === 0;

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-2xl font-bold mb-4 gradient-text">Slides</h2>
        <p className="text-gray-600 mb-6">
          Create and edit your presentation slides. Add titles and content for
          each slide.
        </p>

        {noSlides ? (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <h3 className="text-xl font-semibold mb-6">Generate Slides</h3>
            <p className="text-gray-600 mb-8">
              Your presentation needs slides. You can generate them
              automatically using AI based on your research.
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
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Slide Thumbnails */}
            <div className="lg:col-span-1 space-y-4">
              <div className="bg-white/90 backdrop-blur-sm p-4 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  Slides
                </h3>
                <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
                  <AnimatePresence>
                    {presentation.slides.map((slide, index) => (
                      <motion.div
                        key={slide.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                      >
                        <Card
                          data-testid={`slide-thumbnail-${index}`}
                          className={`cursor-pointer slide-card ${
                            currentSlide?.id === slide.id
                              ? "ring-2 ring-primary-500 bg-primary-50"
                              : "hover:bg-gray-50"
                          }`}
                          onClick={() => setCurrentSlide(slide)}
                        >
                          <CardContent className="p-3">
                            <div className="flex justify-between items-center mb-2">
                              <span className="font-medium truncate text-sm">
                                {slide.title || `Slide ${index + 1}`}
                              </span>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6 rounded-full hover:bg-red-50 hover:text-red-500"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  deleteSlide(slide.id);
                                }}
                              >
                                <Trash2 size={14} />
                              </Button>
                            </div>
                            <div className="h-20 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-lg overflow-hidden p-2">
                              <SlidePreview slide={slide} mini />
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant="outline"
                      className="w-full flex items-center justify-center gap-1 border-dashed border-gray-300 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                      onClick={addNewSlide}
                      data-testid="add-slide-button"
                    >
                      <Plus size={16} />
                      Add Slide
                    </Button>
                  </motion.div>
                </div>
              </div>
            </div>

            {/* Slide Editor */}
            <div className="lg:col-span-3">
              {currentSlide ? (
                <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-gray-100">
                  <Tabs
                    value={activeTab}
                    onValueChange={setActiveTab}
                    className="w-full"
                  >
                    <TabsList className="mb-6 bg-gray-100 p-1 rounded-lg">
                      <TabsTrigger
                        value="edit"
                        className="data-[state=active]:bg-white data-[state=active]:text-primary-600 rounded-md transition-all"
                      >
                        Edit
                      </TabsTrigger>
                      <TabsTrigger
                        value="preview"
                        className="data-[state=active]:bg-white data-[state=active]:text-primary-600 rounded-md transition-all"
                      >
                        Preview
                      </TabsTrigger>
                    </TabsList>
                    <TabsContent
                      value="edit"
                      className="space-y-4 animate-fade-in"
                    >
                      <div className="space-y-2">
                        <label className="text-sm font-medium">
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
                        <label className="text-sm font-medium">
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
                          rows={10}
                          className="resize-none border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                        />
                      </div>
                    </TabsContent>
                    <TabsContent value="preview" className="animate-fade-in">
                      <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl shadow-lg p-8 aspect-[16/9] flex items-center justify-center">
                        <SlidePreview slide={currentSlide} />
                      </div>
                    </TabsContent>
                  </Tabs>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100 p-8">
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-center"
                  >
                    <svg
                      className="h-12 w-12 text-gray-300 mx-auto mb-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    <p className="text-gray-500 mb-4">No slides yet</p>
                    <Button
                      onClick={addNewSlide}
                      className="bg-primary hover:bg-primary-600 text-white transition-all duration-300 shadow-md hover:shadow-primary-500/25"
                      data-testid="add-first-slide-button"
                    >
                      Add Your First Slide
                    </Button>
                  </motion.div>
                </div>
              )}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
