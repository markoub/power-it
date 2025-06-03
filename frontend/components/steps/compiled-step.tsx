"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Image, FileText, Play, Pause, Volume2, Video } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { Presentation, Slide } from "@/lib/types";
import SlidePreview from "@/components/slide-preview"; // Unified on SlidePreview as the rendering component
import { api } from "@/lib/api";
import { SimpleAvatar } from "@/components/SimpleAvatar";

interface CompiledStepProps {
  presentation: Presentation;
  currentSlide: Slide | null;
  setCurrentSlide: (slide: Slide | null) => void;
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
    "Welcome": { color: "bg-purple-100 text-purple-700 border-purple-200", icon: FileText, label: "Welcome" },
    "TableOfContents": { color: "bg-blue-100 text-blue-700 border-blue-200", icon: FileText, label: "Table of Contents" },
    "Section": { color: "bg-green-100 text-green-700 border-green-200", icon: FileText, label: "Section" },
    "ContentImage": { color: "bg-orange-100 text-orange-700 border-orange-200", icon: Image, label: "Content + Image" },
    "Content": { color: "bg-gray-100 text-gray-700 border-gray-200", icon: FileText, label: "Content" },
    "ImageFull": { color: "bg-pink-100 text-pink-700 border-pink-200", icon: Image, label: "Full Image" },
    "3Images": { color: "bg-indigo-100 text-indigo-700 border-indigo-200", icon: Image, label: "Three Images" },
    "ContentWithLogos": { color: "bg-yellow-100 text-yellow-700 border-yellow-200", icon: Image, label: "Content + Logos" },
  };
  
  return typeMap[slideType] || typeMap["Content"];
};

export default function CompiledStep({
  presentation,
  currentSlide,
  setCurrentSlide,
  onContextChange,
  refreshPresentation,
}: CompiledStepProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasAudio, setHasAudio] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [autoAdvance, setAutoAdvance] = useState(true);
  const [showAvatar, setShowAvatar] = useState(false);
  const [isAvatarPlaying, setIsAvatarPlaying] = useState(false);
  
  // Check if compiled step is currently processing
  const compiledStep = presentation.steps?.find(step => step.step === 'compiled');
  const isProcessing = compiledStep?.status === 'processing';

  useEffect(() => {
    onContextChange("all");
    if (currentSlide) {
      const index = presentation.slides.findIndex(
        (slide) => slide.id === currentSlide.id
      );
      if (index !== -1) setCurrentIndex(index);
    }
  }, [currentSlide, onContextChange, presentation.slides]);

  // Check if current slide has speaker notes
  useEffect(() => {
    const currentSlideData = presentation.slides[currentIndex];
    const hasNotes = currentSlideData?.speakerNotes || 
                    currentSlideData?.notes || 
                    (currentSlideData as any)?.fields?.notes;
    setHasAudio(!!hasNotes);
    
    // Stop any playing audio when slide changes
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
    }
    
    // Stop avatar when slide changes
    setIsAvatarPlaying(false);
  }, [currentIndex, presentation.slides]);

  const loadAndPlayAudio = async () => {
    if (!presentation.id) return;
    
    setIsLoading(true);
    setIsPlaying(false);
    
    try {
      // Stop existing audio
      if (audioRef.current) {
        audioRef.current.pause();
      }
      
      // Fetch audio stream
      const response = await api.streamSlideAudio(
        presentation.id,
        currentIndex,
        { rate: "+0%", pitch: "+0Hz", volume: "+0%" }
      );
      
      if (!response.ok) {
        console.error('Failed to load audio');
        setIsLoading(false);
        return;
      }
      
      // Create audio URL from response
      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      
      // Create and play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      // Set up event listeners
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        
        // Auto-advance to next slide if enabled
        if (autoAdvance && currentIndex < presentation.slides.length - 1) {
          goToNextSlide();
        }
      };
      
      audio.onplay = () => {
        setIsPlaying(true);
        setIsLoading(false);
      };
      
      audio.onerror = () => {
        console.error('Audio playback error');
        setIsPlaying(false);
        setIsLoading(false);
      };
      
      // Play audio
      await audio.play();
    } catch (error) {
      console.error('Error loading audio:', error);
      setIsLoading(false);
    }
  };

  const togglePlayPause = () => {
    if (!audioRef.current) {
      loadAndPlayAudio();
    } else if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const goToNextSlide = () => {
    if (currentIndex < presentation.slides.length - 1) {
      const nextIndex = currentIndex + 1;
      setCurrentIndex(nextIndex);
      setCurrentSlide(presentation.slides[nextIndex]);
    }
  };

  const goToPreviousSlide = () => {
    if (currentIndex > 0) {
      const prevIndex = currentIndex - 1;
      setCurrentIndex(prevIndex);
      setCurrentSlide(presentation.slides[prevIndex]);
    }
  };

  // Show processing state if compilation is in progress
  if (isProcessing) {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold mb-4 gradient-text">Compiling Presentation</h2>
          <p className="text-muted-foreground mb-6">
            Combining slides and illustrations into a complete presentation.
          </p>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="flex items-center justify-center gap-3 text-primary-600 mb-4">
              <div className="h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
              <h3 className="text-xl font-semibold">Compiling...</h3>
            </div>
            <p className="text-muted-foreground mb-4">
              Finalizing your presentation structure and preparing all elements.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
              This process ensures all slides and images are properly integrated and ready for export.
            </div>
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
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2 gradient-text">
              Compiled Presentation
            </h2>
            <p className="text-muted-foreground">
              Preview your complete presentation with slides and illustrations
              combined.
            </p>
          </div>
          
          {/* Auto-advance toggle */}
          <div className="flex items-center gap-2">
            <label htmlFor="auto-advance" className="text-sm font-medium">
              Auto-advance after audio
            </label>
            <input
              id="auto-advance"
              type="checkbox"
              checked={autoAdvance}
              onChange={(e) => setAutoAdvance(e.target.checked)}
              className="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500"
            />
          </div>
        </div>

        {presentation.slides.length > 0 ? (
          <div className="space-y-6">
            {/* Video and slide container */}
            <div className="flex gap-6">
              {/* Current slide preview with slide info */}
              <div className={`bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl shadow-lg p-8 aspect-[16/9] relative ${showAvatar ? 'flex-1' : 'w-full'}`}>
              {/* Slide type and image indicator */}
              <div className="absolute top-4 left-4 flex gap-2 z-10">
                <Badge 
                  className={`${getSlideTypeInfo(detectSlideType(presentation.slides[currentIndex])).color}`}
                  variant="outline"
                >
                  {getSlideTypeInfo(detectSlideType(presentation.slides[currentIndex])).label}
                </Badge>
                {presentation.slides[currentIndex].imageUrl && (
                  <Badge 
                    className="bg-emerald-100 text-emerald-700 border-emerald-200 flex items-center gap-1"
                    variant="outline"
                  >
                    <Image size={12} />
                    Image
                  </Badge>
                )}
              </div>

              <AnimatePresence mode="wait">
                <motion.div
                  key={currentIndex}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="w-full h-full"
                >
                  <SlidePreview slide={presentation.slides[currentIndex]} />
                </motion.div>
              </AnimatePresence>

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
                
                {hasAudio && (
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={togglePlayPause}
                    disabled={isLoading}
                    className="bg-white/80 backdrop-blur-sm hover:bg-white"
                    title={isPlaying ? "Pause speaker notes" : "Play speaker notes"}
                  >
                    {isLoading ? (
                      <div className="h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                    ) : isPlaying ? (
                      <Pause size={18} />
                    ) : (
                      <Play size={18} />
                    )}
                  </Button>
                )}
                
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
              
              {/* Audio indicator */}
              {hasAudio && (
                <div className="absolute top-4 right-4 z-10">
                  <Badge 
                    className="bg-blue-100 text-blue-700 border-blue-200 flex items-center gap-1"
                    variant="outline"
                  >
                    <Volume2 size={12} />
                    Speaker Notes
                  </Badge>
                </div>
              )}
            </div>
              
              {/* Simple Local Avatar */}
              {showAvatar && (
                <div className="flex-1 rounded-xl shadow-lg overflow-hidden aspect-[16/9] relative">
                  <SimpleAvatar
                    text={presentation.slides[currentIndex]?.speakerNotes || 
                          presentation.slides[currentIndex]?.notes || 
                          (presentation.slides[currentIndex] as any)?.fields?.notes || ''}
                    isPlaying={isAvatarPlaying}
                    onPlay={() => {
                      // Stop regular audio if playing
                      if (audioRef.current && !audioRef.current.paused) {
                        audioRef.current.pause();
                        setIsPlaying(false);
                      }
                    }}
                    onStop={() => setIsAvatarPlaying(false)}
                    onEnded={() => {
                      setIsAvatarPlaying(false);
                      // Auto-advance if enabled
                      if (autoAdvance && currentIndex < presentation.slides.length - 1) {
                        goToNextSlide();
                      }
                    }}
                  />
                  <button
                    className="absolute top-4 right-4 bg-white/80 p-2 rounded-full hover:bg-white transition-colors z-10"
                    onClick={() => {
                      setShowAvatar(false);
                      setIsAvatarPlaying(false);
                    }}
                    title="Close avatar"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
              )}
            </div>

            {/* Avatar controls */}
            <div className="flex items-center justify-between bg-white rounded-lg shadow-sm border border-gray-100 p-4">
              <div className="flex items-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setShowAvatar(!showAvatar);
                    if (!showAvatar) {
                      setIsAvatarPlaying(false);
                    }
                  }}
                  className="flex items-center gap-2"
                  disabled={!hasAudio}
                >
                  <Video size={16} />
                  {showAvatar ? 'Hide Avatar' : 'Show Avatar'}
                </Button>
                
                {showAvatar && hasAudio && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsAvatarPlaying(!isAvatarPlaying)}
                    className="flex items-center gap-2"
                  >
                    {isAvatarPlaying ? <Pause size={16} /> : <Play size={16} />}
                    {isAvatarPlaying ? 'Pause Avatar' : 'Play Avatar'}
                  </Button>
                )}
                
                {showAvatar && (
                  <div className="text-sm text-gray-500">
                    {hasAudio ? 'Simple avatar ready with speaker notes' : 'No speaker notes available'}
                  </div>
                )}
              </div>
              
              <div className="text-xs text-gray-400">
                {hasAudio ? 'Simple avatar will speak the speaker notes using browser TTS' : 'Add speaker notes to enable avatar'}
              </div>
            </div>

            {/* Slide thumbnails with type and image indicators */}
            <div className="overflow-x-auto pb-4">
              <div className="flex gap-4">
                {presentation.slides.map((slide, index) => {
                  const slideType = detectSlideType(slide);
                  const typeInfo = getSlideTypeInfo(slideType);
                  const Icon = typeInfo.icon;
                  
                  return (
                    <Card
                      key={slide.id}
                      data-testid={`compiled-thumbnail-${index}`}
                      className={`flex-shrink-0 w-40 cursor-pointer transition-all ${
                        index === currentIndex
                          ? "ring-2 ring-primary-500 scale-105"
                          : "opacity-70 hover:opacity-100"
                      }`}
                      onClick={() => {
                        setCurrentIndex(index);
                        setCurrentSlide(slide);
                      }}
                    >
                      <CardContent className="p-2">
                        <div className="aspect-video bg-white rounded mb-2 overflow-hidden border border-gray-100 shadow-sm">
                          <SlidePreview slide={slide} mini />
                        </div>
                        
                        {/* Slide title */}
                        <p className="text-xs font-medium truncate mb-2">
                          {slide.title || `Slide ${index + 1}`}
                        </p>

                        {/* Type and image indicators */}
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-1">
                            <Icon size={10} className="text-gray-500 flex-shrink-0" />
                            <Badge 
                              className={`text-[8px] px-1 py-0 ${typeInfo.color}`}
                              variant="outline"
                            >
                              {typeInfo.label}
                            </Badge>
                          </div>
                          {slide.imageUrl && (
                            <div className="flex items-center gap-1">
                              <Image size={10} className="text-emerald-600 flex-shrink-0" />
                              <span className="text-[8px] text-emerald-600 font-medium">
                                Has Image
                              </span>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <p className="text-gray-500">
              No slides to preview. Please create slides first.
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
}