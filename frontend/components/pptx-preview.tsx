"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { Presentation } from "@/lib/types";
import { api } from "@/lib/api";

interface PptxPreviewProps {
  presentation: Presentation;
  key?: string;
  onSlidesLoaded?: (count: number) => void;
}

export default function PptxPreview({ presentation, onSlidesLoaded }: PptxPreviewProps) {
  const [images, setImages] = useState<string[]>([]);
  const [current, setCurrent] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [showSlideDetails, setShowSlideDetails] = useState(false);

  useEffect(() => {
    async function fetchSlides() {
      setIsLoading(true);
      try {
        console.log(`Fetching PPTX slides for presentation ${presentation.id}...`);
        const slides = await api.getPptxSlides(presentation.id.toString());
        console.log(`Received ${slides.length} PPTX slides:`, slides);
        
        setImages(slides);
        setCurrent(0);
        
        // Notify parent about slide count
        if (onSlidesLoaded) {
          onSlidesLoaded(slides.length);
        }
      } catch (error) {
        console.error("Error fetching PPTX slides:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchSlides();
  }, [presentation.id, onSlidesLoaded]);

  const next = () => {
    if (current < images.length - 1) setCurrent(current + 1);
  };
  const prev = () => {
    if (current > 0) setCurrent(current - 1);
  };

  if (isLoading) {
    return (
      <div className="text-center py-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl border border-gray-100 dark:border-gray-700">
        <p className="text-gray-500 dark:text-gray-400">Loading PPTX preview...</p>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="text-center py-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-xl border border-gray-100 dark:border-gray-700">
        <p className="text-gray-500 dark:text-gray-400">PPTX not generated yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h2 className="text-2xl font-bold mb-4 gradient-text">PPTX Preview</h2>
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl shadow-lg p-8 aspect-[16/9] relative">
            <AnimatePresence mode="wait">
              <motion.img
                key={current}
                src={images[current]}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="w-full h-full object-contain"
                alt={`Slide ${current + 1}`}
                data-testid="pptx-preview-image"
              />
            </AnimatePresence>
            <div className="absolute bottom-4 left-0 right-0 flex justify-center items-center gap-4">
              <Button variant="outline" size="icon" onClick={prev} disabled={current === 0} className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm hover:bg-white dark:hover:bg-gray-800">
                <ChevronLeft size={18} />
              </Button>
              <span className="text-sm font-medium">
                {current + 1} / {images.length}
              </span>
              <Button variant="outline" size="icon" onClick={next} disabled={current === images.length - 1} className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm hover:bg-white dark:hover:bg-gray-800">
                <ChevronRight size={18} />
              </Button>
            </div>
          </div>
          
          {/* Slide Details Section - appears when thumbnail is clicked */}
          {showSlideDetails && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="slide-details bg-white rounded-xl shadow-lg p-6 border border-gray-200"
            >
              <h3 className="text-lg font-semibold mb-4">Slide {current + 1} Details</h3>
              <div className="aspect-video bg-gray-50 rounded-lg overflow-hidden">
                <img 
                  src={images[current]} 
                  alt={`Slide ${current + 1} detail view`}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="mt-4 flex justify-end">
                <Button 
                  variant="outline" 
                  onClick={() => setShowSlideDetails(false)}
                >
                  Close Details
                </Button>
              </div>
            </motion.div>
          )}
          
          <div className="overflow-x-auto pb-4">
            <div className="flex gap-4">
              {images.map((img, index) => (
                <Card
                  key={index}
                  data-testid={`pptx-thumb-${index}`}
                  className={`flex-shrink-0 w-40 cursor-pointer transition-all ${index === current ? "ring-2 ring-primary-500 scale-105" : "opacity-70 hover:opacity-100"}`}
                  onClick={() => {
                    setCurrent(index);
                    setShowSlideDetails(true);
                  }}
                >
                  <CardContent className="p-2">
                    <div className="aspect-video bg-gray-100 rounded mb-2 overflow-hidden">
                      <img src={img} className="w-full h-full object-contain" alt={`Slide ${index + 1}`} />
                    </div>
                    <p className="text-xs font-medium truncate">Slide {index + 1}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
