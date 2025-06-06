import React, { useState, useCallback } from 'react';
import { Presentation, Slide } from '@/lib/types';
import { api } from '@/lib/api';
import { toast } from '@/hooks/use-toast';
import { ToastAction } from '@/components/ui/toast';
import Wizard from './wizard';

interface WizardIntegrationProps {
  presentation: Presentation | null;
  currentSlide: Slide | null;
  setPresentation: (presentation: Presentation) => void;
  setCurrentSlide: (slide: Slide | null) => void;
  savePresentation: () => Promise<void>;
  currentStep: number;
  steps: string[];
  onContextChange?: (context: "all" | "single") => void;
}

export function WizardIntegration({
  presentation,
  currentSlide,
  setPresentation,
  setCurrentSlide,
  savePresentation,
  currentStep,
  steps,
  onContextChange
}: WizardIntegrationProps) {
  // Determine wizard context based on current slide selection
  const wizardContext = currentSlide ? "single" : "all";

  const handleWizardContextChange = useCallback((context: "all" | "single") => {
    onContextChange?.(context);
  }, [onContextChange]);

  const applyWizardChanges = useCallback(async (changes: any) => {
    if (!presentation) return;

    let slidesModified = false;
    let updatedSlides = presentation.slides;

    if (changes.slide && wizardContext === "single" && currentSlide) {
      // Apply changes to current slide
      const updatedSlide = { ...currentSlide, ...changes.slide };
      updatedSlides = presentation.slides.map((slide) =>
        slide.id === updatedSlide.id ? updatedSlide : slide
      );

      setPresentation({
        ...presentation,
        slides: updatedSlides,
      });
      setCurrentSlide(updatedSlide);
      slidesModified = true;
    } else if (changes.slides && wizardContext === "all") {
      // Apply changes to all slides
      updatedSlides = changes.slides;
      setPresentation({
        ...presentation,
        slides: updatedSlides,
      });
      
      // Update current slide if it exists in the new slides
      if (currentSlide) {
        const updatedCurrentSlide = changes.slides.find((s: Slide) => s.id === currentSlide.id);
        if (updatedCurrentSlide) {
          setCurrentSlide(updatedCurrentSlide);
        }
      }
      slidesModified = true;
    } else if (changes.research) {
      // Apply research changes
      const updatedSteps = presentation.steps?.map(s =>
        s.step === "research" || s.step === "manual_research"
          ? { ...s, result: changes.research, status: "completed" as const }
          : s
      ) || [];

      setPresentation({ ...presentation, steps: updatedSteps });
      await api.saveModifiedResearch(String(presentation.id), changes.research);
      
      toast({
        title: "Research updated",
        description: "The research has been updated successfully.",
        action: <ToastAction altText="OK">OK</ToastAction>,
      });
      return;
    } else if (changes.presentation) {
      // Apply presentation-level changes (add/remove slides, etc.)
      if (changes.presentation.slides) {
        updatedSlides = changes.presentation.slides;
        slidesModified = true;
      }
      
      setPresentation({
        ...presentation,
        ...changes.presentation,
      });
      
      // If slides were modified and we had a current slide, try to maintain selection
      if (changes.presentation.slides && currentSlide) {
        const updatedSlide = changes.presentation.slides.find((slide: Slide) => slide.id === currentSlide.id);
        if (updatedSlide) {
          setCurrentSlide(updatedSlide);
        } else if (changes.presentation.slides.length > 0) {
          // If current slide was removed, select the first slide
          setCurrentSlide(changes.presentation.slides[0]);
        } else {
          setCurrentSlide(null);
        }
      }
    }

    // Save the changes to the backend
    if (slidesModified) {
      // Use the save_modified endpoint for slides changes
      const slidesData = { slides: updatedSlides };
      const success = await api.saveModifiedPresentation(String(presentation.id), slidesData);
      
      if (!success) {
        toast({
          title: "Error",
          description: "Failed to save changes to the backend. Please try again.",
          variant: "destructive",
          action: <ToastAction altText="Try again">Try again</ToastAction>,
        });
        return;
      }
    } else {
      // For non-slide changes, use the regular save
      await savePresentation();
    }

    toast({
      title: "Changes applied",
      description: changes.presentation 
        ? "The presentation has been modified successfully."
        : "The suggested changes have been applied to your presentation.",
      action: <ToastAction altText="OK">OK</ToastAction>,
    });
  }, [presentation, currentSlide, wizardContext, setPresentation, setCurrentSlide, savePresentation]);

  return (
    <Wizard
      presentation={presentation}
      currentSlide={currentSlide}
      context={wizardContext}
      step={steps[currentStep]}
      onApplyChanges={applyWizardChanges}
    />
  );
}

