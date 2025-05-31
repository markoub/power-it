"use client";

import { useState } from "react";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2, Sparkles, Loader2, Edit3, Eye, FileText, Grid3X3, ArrowLeft, Settings } from "lucide-react";
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
  const contentForDetection = Array.isArray(slide.content) 
    ? slide.content.join(' ').toLowerCase() 
    : (typeof slide.content === 'string' ? slide.content.toLowerCase() : '');
  
  if (title.includes("welcome") || title.includes("introduction") || title.match(/^\s*presentation|overview/i)) {
    return "Welcome";
  }
  
  if (title.includes("table of contents") || title.includes("agenda") || title.includes("overview")) {
    return "TableOfContents";
  }
  
  if (title.match(/^\s*section|part|chapter/i) || (title.length < 20 && contentForDetection.length < 20)) {
    return "Section";
  }
  
  if (slide.imageUrl) {
    if (contentForDetection.length < 100) {
      return "ImageFull";
    }
    
    if (contentForDetection.match(/image\s*1.*image\s*2.*image\s*3/i) || 
        contentForDetection.match(/figure\s*1.*figure\s*2.*figure\s*3/i)) {
      return "3Images";
    }
    
    if (contentForDetection.match(/logo|brand|company|partner/i)) {
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

interface SlidesCustomization {
  target_slides: number;
  target_audience: string;
  content_density: string;
  presentation_duration: number;
  custom_prompt: string;
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
  const [viewMode, setViewMode] = useState<"preview" | "edit">("preview");
  const [isGenerating, setIsGenerating] = useState(false);
  const [slideView, setSlideView] = useState<"overview" | "single">("overview");
  const [showCustomization, setShowCustomization] = useState(false);
  const [customization, setCustomization] = useState<SlidesCustomization>({
    target_slides: 10,
    target_audience: "general",
    content_density: "medium",
    presentation_duration: 15,
    custom_prompt: "",
  });

  useEffect(() => {
    // Update slide view based on current slide selection
    if (currentSlide) {
      setSlideView("single");
      onContextChange("single");
    } else {
      setSlideView("overview");
      onContextChange("all");
    }
  }, [currentSlide, onContextChange]);

  // Function to generate slides with AI
  const handleGenerateSlides = async () => {
    try {
      setIsGenerating(true);

      const presentationId = typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id;
      
      // Prepare customization parameters, filtering out empty custom_prompt
      const params: any = { ...customization };
      if (!params.custom_prompt.trim()) {
        delete params.custom_prompt;
      }
      
      const result = await api.runPresentationStep(presentationId, "slides", params);

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

  const handleSlideClick = (slide: Slide) => {
    setCurrentSlide(slide);
    setSlideView("single");
  };

  const handleBackToOverview = () => {
    setCurrentSlide(null);
    setSlideView("overview");
  };

  const noSlides = presentation.slides.length === 0;
  
  // Check if slides step is currently processing
  const slidesStep = presentation.steps?.find(step => step.step === 'slides');
  const isProcessing = slidesStep?.status === 'processing';

  // Show processing state if slides are being generated
  if (isProcessing) {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold mb-4 gradient-text">Generating Slides</h2>
          <p className="text-gray-600 mb-6">
            Your slides are being generated using AI based on your research content.
          </p>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="flex items-center justify-center gap-3 text-primary-600 mb-4">
              <Loader2 size={32} className="animate-spin" />
              <h3 className="text-xl font-semibold">Generating Slides...</h3>
            </div>
            <p className="text-gray-600 mb-4">
              This process may take a minute or two. Please wait while we create your slides.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
              The AI is analyzing your research content and creating structured slides with appropriate titles and content.
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

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

            <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
              <Dialog open={showCustomization} onOpenChange={setShowCustomization}>
                <DialogTrigger asChild>
                  <Button
                    variant="outline"
                    className="flex items-center gap-2"
                    data-testid="customize-slides-button"
                  >
                    <Settings size={18} />
                    Customize
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[500px]">
                  <DialogHeader>
                    <DialogTitle>Customize Slides Generation</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-6 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="target_slides">Number of Slides (approximate)</Label>
                      <Input
                        id="target_slides"
                        type="number"
                        min="3"
                        max="30"
                        value={customization.target_slides}
                        onChange={(e) => setCustomization(prev => ({ ...prev, target_slides: parseInt(e.target.value) || 10 }))}
                        placeholder="10"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="target_audience">Target Audience</Label>
                      <Select 
                        value={customization.target_audience} 
                        onValueChange={(value) => setCustomization(prev => ({ ...prev, target_audience: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select audience" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="general">General Audience</SelectItem>
                          <SelectItem value="executives">Executives</SelectItem>
                          <SelectItem value="technical">Technical Team</SelectItem>
                          <SelectItem value="students">Students</SelectItem>
                          <SelectItem value="sales">Sales Team</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="content_density">Content Density</Label>
                      <Select 
                        value={customization.content_density} 
                        onValueChange={(value) => setCustomization(prev => ({ ...prev, content_density: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select density" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low (Minimal text, visual focus)</SelectItem>
                          <SelectItem value="medium">Medium (Balanced content)</SelectItem>
                          <SelectItem value="high">High (Detailed information)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="presentation_duration">Presentation Duration (minutes)</Label>
                      <Input
                        id="presentation_duration"
                        type="number"
                        min="5"
                        max="120"
                        value={customization.presentation_duration}
                        onChange={(e) => setCustomization(prev => ({ ...prev, presentation_duration: parseInt(e.target.value) || 15 }))}
                        placeholder="15"
                      />
                      <p className="text-xs text-gray-500">Affects the length of speaker notes</p>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="custom_prompt">Additional Instructions (optional)</Label>
                      <Textarea
                        id="custom_prompt"
                        value={customization.custom_prompt}
                        onChange={(e) => setCustomization(prev => ({ ...prev, custom_prompt: e.target.value }))}
                        placeholder="e.g., Focus on ROI metrics, Include case studies, Emphasize technical challenges..."
                        rows={3}
                        className="resize-none"
                      />
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

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
          </div>
        </motion.div>
      </div>
    );
  }

  // Overview Mode - Show all slides as thumbnails
  if (slideView === "overview") {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold gradient-text">Slides Overview</h2>
              <p className="text-gray-600">
                Click on any slide to edit it. You have {presentation.slides.length} slides in your presentation.
              </p>
            </div>
            <Button
              onClick={addNewSlide}
              className="bg-primary hover:bg-primary-600 text-white flex items-center gap-2"
              data-testid="add-slide-button"
            >
              <Plus size={16} />
              Add Slide
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <AnimatePresence>
              {presentation.slides.map((slide, index) => {
                const slideType = detectSlideType(slide);
                const typeInfo = getSlideTypeInfo(slideType);
                const Icon = typeInfo.icon;
                
                return (
                  <motion.div
                    key={slide.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.2, delay: index * 0.02 }}
                  >
                    <Card
                      data-testid={`slide-thumbnail-${index}`}
                      className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105 group"
                      onClick={() => handleSlideClick(slide)}
                    >
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex items-center gap-2 min-w-0 flex-1">
                            <Icon size={14} className="text-gray-500 flex-shrink-0" />
                            <span className="font-medium truncate text-sm">
                              {slide.title || `Slide ${index + 1}`}
                            </span>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 rounded-full hover:bg-red-50 hover:text-red-500 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteSlide(slide.id);
                            }}
                          >
                            <Trash2 size={12} />
                          </Button>
                        </div>
                        
                        <Badge 
                          className={`text-xs px-2 py-0.5 mb-3 ${typeInfo.color}`}
                          variant="outline"
                        >
                          {typeInfo.label}
                        </Badge>
                        
                        <div 
                          className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-lg overflow-hidden"
                          style={{ aspectRatio: '16/9' }}
                        >
                          <div className="h-full w-full bg-white rounded-sm">
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
        </motion.div>
      </div>
    );
  }

  // Single Slide Mode - Show selected slide with horizontal thumbnails below
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header with back button */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="outline"
            onClick={handleBackToOverview}
            className="flex items-center gap-2"
            data-testid="back-to-overview-button"
          >
            <ArrowLeft size={16} />
            Back to Overview
          </Button>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold gradient-text">
              {currentSlide?.title || "Untitled Slide"}
            </h2>
            <Badge 
              className={`${getSlideTypeInfo(detectSlideType(currentSlide!)).color}`}
              variant="outline"
            >
              {getSlideTypeInfo(detectSlideType(currentSlide!)).label}
            </Badge>
          </div>
        </div>

        {/* Main slide content */}
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100">
          {/* Mode toggle */}
          <div className="p-4 border-b border-gray-100">
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
                        <SlideRenderer slide={currentSlide!} mini={false} />
                      </div>
                    </div>
                  </div>
                  {currentSlide?.notes && (
                    <div className="p-4">
                      <Accordion type="single" collapsible>
                        <AccordionItem value="notes">
                          <AccordionTrigger>Speaker Notes</AccordionTrigger>
                          <AccordionContent>
                            <p className="whitespace-pre-line">{currentSlide.notes}</p>
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
                    </div>
                  )}
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
                      value={currentSlide?.title || ""}
                      onChange={(e) =>
                        updateSlide({
                          ...currentSlide!,
                          title: e.target.value,
                          fields: {
                            ...currentSlide!.fields,
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
                      Slide Content (Markdown supported)
                    </label>
                    <Textarea
                      value={
                        Array.isArray(currentSlide?.content)
                          ? currentSlide.content.join('\n')
                          : (typeof currentSlide?.content === "string" ? currentSlide.content : "")
                      }
                      onChange={(e) => {
                        const newContent = e.target.value;
                        updateSlide({
                          ...currentSlide!,
                          content: newContent, // Keep as string for user editing
                          fields: {
                            ...currentSlide!.fields,
                            content: newContent,
                          },
                        })
                      }}
                      placeholder="Enter slide content using Markdown:

# Heading
## Subheading
- Bullet point
**Bold text**
*Italic text*

Or let each line become a bullet point automatically!"
                      rows={12}
                      className="resize-none border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500">
                      You can use Markdown formatting (headings, lists, bold, italic, etc.) or just type lines of text that will automatically become bullet points.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">
                      Speaker Notes
                    </label>
                    <Textarea
                      value={currentSlide?.notes || ""}
                      onChange={(e) =>
                        updateSlide({
                          ...currentSlide!,
                          notes: e.target.value,
                          fields: {
                            ...currentSlide!.fields,
                            notes: e.target.value,
                          },
                        })
                      }
                      placeholder="Enter short script for presenter"
                      rows={4}
                      className="resize-none border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all font-mono text-sm"
                    />
                  </div>

                  {/* Live Preview in Edit Mode */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Live Preview</h4>
                    <div 
                      className="bg-white rounded-md shadow-sm border overflow-hidden"
                      style={{ aspectRatio: '16/9' }}
                    >
                      <SlideRenderer slide={currentSlide!} mini={false} />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Horizontal slide thumbnails */}
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">All Slides ({presentation.slides.length})</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={addNewSlide}
              className="flex items-center gap-1 border-dashed"
              data-testid="add-slide-horizontal-button"
            >
              <Plus size={14} />
              Add
            </Button>
          </div>
          
          <div className="flex gap-3 overflow-x-auto pb-2">
            <AnimatePresence>
              {presentation.slides.map((slide, index) => {
                const slideType = detectSlideType(slide);
                const typeInfo = getSlideTypeInfo(slideType);
                const Icon = typeInfo.icon;
                const isSelected = currentSlide?.id === slide.id;
                
                return (
                  <motion.div
                    key={slide.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2, delay: index * 0.02 }}
                    className="flex-shrink-0"
                  >
                    <Card
                      data-testid={`slide-thumbnail-horizontal-${index}`}
                      className={`cursor-pointer transition-all duration-200 w-48 ${
                        isSelected
                          ? "ring-2 ring-primary-500 bg-primary-50 border-primary-200"
                          : "hover:bg-gray-50 hover:border-gray-200"
                      }`}
                      onClick={() => handleSlideClick(slide)}
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
                        
                        <div 
                          className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-md overflow-hidden"
                          style={{ aspectRatio: '16/9', height: '80px' }}
                        >
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
      </motion.div>
    </div>
  );
}
