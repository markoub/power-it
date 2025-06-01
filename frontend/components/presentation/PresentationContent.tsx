import React from 'react';
import { Presentation, Slide } from '@/lib/types';
import ResearchStep from '@/components/steps/research-step';
import SlidesStep from '@/components/steps/slides-step';
import IllustrationStep from '@/components/steps/illustration-step';
import CompiledStep from '@/components/steps/compiled-step';
import PptxStep from '@/components/steps/pptx-step';

interface PresentationContentProps {
  presentation: Presentation;
  currentStep: number;
  currentSlide: Slide | null;
  setPresentation: (presentation: Presentation) => void;
  setCurrentSlide: (slide: Slide | null) => void;
  setCurrentStep: (step: number) => void;
  updateSlide: (slideId: string, updates: Partial<Slide>) => Promise<void>;
  addNewSlide: (afterSlideId?: string) => Promise<void>;
  deleteSlide: (slideId: string) => Promise<void>;
  savePresentation: () => Promise<void>;
  refreshPresentation: () => Promise<any>;
  onWizardContextChange: (context: "all" | "single") => void;
}

export function PresentationContent({
  presentation,
  currentStep,
  currentSlide,
  setPresentation,
  setCurrentSlide,
  setCurrentStep,
  updateSlide,
  addNewSlide,
  deleteSlide,
  savePresentation,
  refreshPresentation,
  onWizardContextChange
}: PresentationContentProps) {
  return (
    <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
      {currentStep === 0 && (
        <ResearchStep
          presentation={presentation}
          setPresentation={setPresentation}
          savePresentation={savePresentation}
          mode={presentation.researchMethod === 'manual' ? 'manual' : 'edit'}
          onEditResearch={() => setCurrentStep(0)}
          refreshPresentation={refreshPresentation}
        />
      )}
      {currentStep === 1 && (
        <SlidesStep
          presentation={presentation}
          currentSlide={currentSlide}
          setCurrentSlide={setCurrentSlide}
          updateSlide={updateSlide}
          addNewSlide={addNewSlide}
          deleteSlide={deleteSlide}
          onContextChange={onWizardContextChange}
          refreshPresentation={refreshPresentation}
        />
      )}
      {currentStep === 2 && (
        <IllustrationStep
          presentation={presentation}
          currentSlide={currentSlide}
          setCurrentSlide={setCurrentSlide}
          updateSlide={updateSlide}
          onContextChange={onWizardContextChange}
          refreshPresentation={refreshPresentation}
        />
      )}
      {currentStep === 3 && (
        <CompiledStep
          presentation={presentation}
          currentSlide={currentSlide}
          setCurrentSlide={setCurrentSlide}
          onContextChange={onWizardContextChange}
          refreshPresentation={refreshPresentation}
        />
      )}
      {currentStep === 4 && (
        <PptxStep 
          presentation={presentation} 
          refreshPresentation={refreshPresentation}
        />
      )}
    </div>
  );
}