import { useState, useCallback } from 'react';
import { Slide, Presentation } from '@/lib/types';
import { v4 as uuidv4 } from 'uuid';
import { api } from '@/lib/api';
import { toast } from '@/hooks/use-toast';
import { ToastAction } from '@/components/ui/toast';

interface UseSlideManagementOptions {
  presentation: Presentation | null;
  setPresentation: (presentation: Presentation) => void;
  verboseLogging?: boolean;
}

export function useSlideManagement({
  presentation,
  setPresentation,
  verboseLogging = false
}: UseSlideManagementOptions) {
  const [currentSlide, setCurrentSlide] = useState<Slide | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Helper for structured logging
  const logInfo = useCallback((message: string, data?: any) => {
    if (verboseLogging) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  }, [verboseLogging]);

  const logError = useCallback((message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  }, []);

  // Save presentation
  const savePresentation = useCallback(async () => {
    if (!presentation) return;

    setIsSaving(true);
    try {
      const updatedPresentation = await api.updatePresentation(
        String(presentation.id),
        presentation,
      );

      if (updatedPresentation) {
        setPresentation(updatedPresentation);

        toast({
          title: "Changes saved",
          description: "Your presentation has been updated successfully.",
          action: <ToastAction altText="OK">OK</ToastAction>,
        });
      } else {
        throw new Error("Failed to update presentation");
      }
    } catch (error) {
      logError("Error saving presentation:", error);
      toast({
        title: "Error",
        description: "Failed to save changes. Please try again.",
        variant: "destructive",
        action: <ToastAction altText="Try again">Try again</ToastAction>,
      });
    } finally {
      setIsSaving(false);
    }
  }, [presentation, setPresentation, logError]);

  // Add new slide
  const addNewSlide = useCallback(() => {
    if (!presentation) return;

    const newSlide: Slide = {
      id: uuidv4(),
      type: "Content",
      fields: { title: "New Slide", content: "", notes: "" },
      title: "New Slide",
      content: "",
      notes: "",
      order: presentation.slides.length,
      imagePrompt: "",
      imageUrl: "",
    };

    const updatedPresentation = {
      ...presentation,
      slides: [...presentation.slides, newSlide],
    };

    setPresentation(updatedPresentation);
    setCurrentSlide(newSlide);
    savePresentation();
  }, [presentation, setPresentation, savePresentation]);

  // Update slide
  const updateSlide = useCallback((updatedSlide: Slide) => {
    if (!presentation) return;

    const updatedSlides = presentation.slides.map((slide) =>
      slide.id === updatedSlide.id ? updatedSlide : slide,
    );

    setPresentation({
      ...presentation,
      slides: updatedSlides,
    });
    setCurrentSlide(updatedSlide);
  }, [presentation, setPresentation]);

  // Delete slide
  const deleteSlide = useCallback((slideId: string) => {
    if (!presentation) return;

    const updatedSlides = presentation.slides
      .filter((slide) => slide.id !== slideId)
      .map((slide, index) => ({ ...slide, order: index }));

    const updatedPresentation = {
      ...presentation,
      slides: updatedSlides,
    };

    setPresentation(updatedPresentation);

    if (currentSlide?.id === slideId) {
      setCurrentSlide(updatedSlides.length > 0 ? updatedSlides[0] : null);
    }

    savePresentation();
  }, [presentation, currentSlide, setPresentation, savePresentation]);

  // Initialize slides
  const initializeSlides = useCallback((slides: Slide[]) => {
    if (slides && slides.length > 0 && !currentSlide) {
      setCurrentSlide(slides[0]);
    }
  }, [currentSlide]);

  // Reorder slides
  const reorderSlides = useCallback((fromIndex: number, toIndex: number) => {
    if (!presentation) return;

    const slides = [...presentation.slides];
    const [removed] = slides.splice(fromIndex, 1);
    slides.splice(toIndex, 0, removed);

    // Update order property
    const reorderedSlides = slides.map((slide, index) => ({
      ...slide,
      order: index
    }));

    setPresentation({
      ...presentation,
      slides: reorderedSlides
    });

    savePresentation();
  }, [presentation, setPresentation, savePresentation]);

  // Duplicate slide
  const duplicateSlide = useCallback((slideId: string) => {
    if (!presentation) return;

    const slideToDuplicate = presentation.slides.find(s => s.id === slideId);
    if (!slideToDuplicate) return;

    const newSlide: Slide = {
      ...slideToDuplicate,
      id: uuidv4(),
      title: `${slideToDuplicate.title} (Copy)`,
      order: slideToDuplicate.order + 1
    };

    // Insert after the original and update orders
    const updatedSlides = presentation.slides.flatMap((slide, index) => {
      if (slide.id === slideId) {
        return [slide, newSlide];
      }
      return slide;
    }).map((slide, index) => ({ ...slide, order: index }));

    setPresentation({
      ...presentation,
      slides: updatedSlides
    });

    setCurrentSlide(newSlide);
    savePresentation();
  }, [presentation, setPresentation, savePresentation]);

  // Update slide content
  const updateSlideContent = useCallback((slideId: string, updates: Partial<Slide>) => {
    if (!presentation) return;

    const updatedSlides = presentation.slides.map((slide) =>
      slide.id === slideId ? { ...slide, ...updates } : slide
    );

    setPresentation({
      ...presentation,
      slides: updatedSlides
    });
  }, [presentation, setPresentation]);

  return {
    currentSlide,
    setCurrentSlide,
    isSaving,
    savePresentation,
    addNewSlide,
    updateSlide,
    deleteSlide,
    initializeSlides,
    reorderSlides,
    duplicateSlide,
    updateSlideContent
  };
}