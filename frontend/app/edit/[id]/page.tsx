"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import type { Presentation } from "@/lib/types";
import Link from "next/link";
import { PatternBackground } from "@/components/ui-elements";
import WorkflowSteps from "@/components/workflow-steps";
import ResearchStep from "@/components/steps/research-step";
import SlidesStep from "@/components/steps/slides-step";
import IllustrationStep from "@/components/steps/illustration-step";
import CompiledStep from "@/components/steps/compiled-step";
import PptxStep from "@/components/steps/pptx-step";
import { api } from "@/lib/api";
import ClientWrapper from "@/components/client-wrapper";
import { use } from "react";
import React from "react";

// Import custom hooks
import { usePresentationPolling } from "@/hooks/usePresentationPolling";
import { useStepNavigation } from "@/hooks/useStepNavigation";
import { useSlideManagement } from "@/hooks/useSlideManagement";
import { usePresentationActions } from "@/hooks/usePresentationActions";

// Import custom components
import { PresentationHeader } from "@/components/presentation/PresentationHeader";
import { WizardIntegration } from "@/components/wizard/WizardIntegration";

// Move constants outside component to prevent re-creation on every render
const STEPS = ["Research", "Slides", "Illustration", "Compiled", "PPTX"];
const STEP_API_NAMES = ["research", "slides", "images", "compiled", "pptx"];

export default function EditPage({ params }: { params: Promise<{ id: string }> }) {
  // Properly unwrap params to get the id
  const unwrappedParams = React.use(params);
  
  // Development flag for verbose logging - set to false to reduce console spam
  const VERBOSE_LOGGING = process.env.NODE_ENV === 'development' && false;
  
  const router = useRouter();
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wizardContext, setWizardContext] = useState<"all" | "single">("all");

  // Initialize custom hooks
  const {
    currentStep,
    setCurrentStep,
    hasManuallyNavigated,
    setHasManuallyNavigated,
    handleStepChange,
    updateCurrentStep,
    resetNavigation,
    isStepCompleted,
    isStepPending,
    isStepProcessing,
    isStepFailed,
    determineCurrentStep,
    getStepStatuses
  } = useStepNavigation({
    steps: STEPS,
    stepApiNames: STEP_API_NAMES,
    presentation,
    verboseLogging: VERBOSE_LOGGING
  });

  const {
    currentSlide,
    setCurrentSlide,
    isSaving,
    savePresentation,
    addNewSlide,
    updateSlide,
    deleteSlide,
    initializeSlides
  } = useSlideManagement({
    presentation,
    setPresentation,
    verboseLogging: VERBOSE_LOGGING
  });

  const {
    isProcessingStep,
    isExporting,
    handleExport,
    runPresentationStep,
    continueToNextStep,
    rerunStep
  } = usePresentationActions({
    presentation,
    verboseLogging: VERBOSE_LOGGING
  });

  const {
    refreshPresentation,
    stopPolling,
    startPolling
  } = usePresentationPolling({
    presentationId: unwrappedParams.id,
    onPresentationUpdate: (updatedPresentation) => {
      setPresentation(updatedPresentation);
      
      // Only update current step automatically if user hasn't manually navigated
      if (!hasManuallyNavigated) {
        updateCurrentStep(updatedPresentation);
      }
    },
    onStepComplete: (stepName) => {
      // Force update current step when a step completes
      updateCurrentStep(presentation!, true);
    },
    verboseLogging: VERBOSE_LOGGING
  });

  // Helper for structured logging
  const logInfo = (message: string, data?: any) => {
    if (VERBOSE_LOGGING) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  };

  const logError = (message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  };

  // Initial presentation load
  useEffect(() => {
    const fetchInitialPresentation = async () => {
      setIsLoading(true);
      try {
        // Stop polling during initial load to prevent conflicts
        stopPolling();
        
        const fetchedPresentation = await api.getPresentation(unwrappedParams.id);
        if (fetchedPresentation) {
          setPresentation(fetchedPresentation);

          // Determine the current step based on completion status
          updateCurrentStep(fetchedPresentation, true);
          
          // Initialize slides
          initializeSlides(fetchedPresentation.slides);
          
          setError(null);
          
          // Start polling after successful initial load
          startPolling();
        } else {
          setError("Presentation not found");
          setTimeout(() => router.push("/"), 3000);
        }
      } catch (err) {
        logError("Error fetching presentation:", err);
        setError("Failed to load presentation");
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialPresentation();
    
    // Cleanup: stop polling when component unmounts
    return () => {
      stopPolling();
    };
  }, [unwrappedParams.id]); // Only depend on ID change

  const handleWizardContextChange = (context: "all" | "single") => {
    setWizardContext(context);
  };

  // Get step status arrays from the hook
  const { completedSteps, pendingSteps, processingSteps, failedSteps } = getStepStatuses();

  // Continue to next step function
  const handleContinueToNextStep = async () => {
    await continueToNextStep(STEP_API_NAMES, isStepCompleted, (stepIndex, stepName) => {
      // Update local state when step starts
      const updatedSteps = presentation?.steps?.map(s => 
        s.step === stepName ? { ...s, status: "processing" as const } : s
      ) || [];
      if (presentation) {
        setPresentation({ ...presentation, steps: updatedSteps });
      }
      setCurrentStep(stepIndex);
      resetNavigation();
      
      // Force immediate refresh to get latest status
      setTimeout(async () => {
        await refreshPresentation();
      }, 500);
    });
  };

  // Determine if continue button should be shown
  const shouldShowContinueButton = () => {
    if (!presentation || !presentation.steps) return false;

    // Find if there are any incomplete steps
    for (let i = 0; i < STEP_API_NAMES.length; i++) {
      if (!isStepCompleted(i)) {
        // If the step before this one is completed, we show the continue button
        return i > 0 && isStepCompleted(i - 1);
      }
    }

    return false; // All steps completed or no steps found
  };

  // Handle rerunning a step
  const handleRerunStep = async (stepIndex: number) => {
    await rerunStep(stepIndex, STEP_API_NAMES, STEPS, (stepIndex, stepName) => {
      // Update local state when step starts
      const updatedSteps = presentation?.steps?.map(s => 
        s.step === stepName ? { ...s, status: "processing" as const } : s
      ) || [];
      if (presentation) {
        setPresentation({ ...presentation, steps: updatedSteps });
      }
      setCurrentStep(stepIndex);
      resetNavigation();
      
      // Force immediate refresh to get latest status
      setTimeout(async () => {
        await refreshPresentation();
      }, 500);
    });
  };

  // Expose debugging info to window for tests
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).currentStep = currentStep;
      (window as any).completedSteps = completedSteps;
      (window as any).presentation = presentation;
    }
  }, [currentStep, completedSteps, presentation]);

  return (
    <ClientWrapper
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="h-10 w-10 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
            <p className="text-gray-600 dark:text-gray-300">Loading presentation...</p>
          </div>
        </div>
      }
    >
      {isLoading ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-10 w-10 animate-spin text-primary-500" />
            <p className="text-gray-600 dark:text-gray-300">Loading presentation...</p>
          </div>
        </div>
      ) : error ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center p-8 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-700 max-w-md">
            <h2 className="text-xl font-semibold text-red-600 mb-4">{error}</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">Redirecting to home page...</p>
            <Link href="/">
              <Button className="bg-primary hover:bg-primary-600 text-white">
                Go to Home
              </Button>
            </Link>
          </div>
        </div>
      ) : !presentation ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center p-8 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-700 max-w-md">
            <h2 className="text-xl font-semibold text-red-600 mb-4">
              Presentation not found
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Unable to load the requested presentation.
            </p>
            <Link href="/">
              <Button className="bg-primary hover:bg-primary-600 text-white">
                Go to Home
              </Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="min-h-screen relative">
          <PatternBackground pattern="grid" />

          <div className="container mx-auto p-4">
            <PresentationHeader
              presentationName={presentation.name}
              isSaving={isSaving}
              isExporting={isExporting}
              onSave={savePresentation}
              onExport={handleExport}
            />

            <WorkflowSteps
              steps={STEPS}
              currentStep={currentStep}
              onChange={handleStepChange}
              onContinue={
                shouldShowContinueButton()
                  ? handleContinueToNextStep
                  : undefined
              }
              isProcessing={isProcessingStep}
              completedSteps={completedSteps}
              pendingSteps={pendingSteps}
              processSteps={processingSteps}
              failedSteps={failedSteps}
              presentationId={presentation.id}
              onRerunStep={handleRerunStep}
            />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
              {/* Wizard Sidebar */}
              <div className="lg:col-span-1">
                <WizardIntegration
                  presentation={presentation}
                  currentSlide={currentSlide}
                  setPresentation={setPresentation}
                  setCurrentSlide={setCurrentSlide}
                  savePresentation={savePresentation}
                  currentStep={currentStep}
                  steps={STEPS}
                  onContextChange={handleWizardContextChange}
                />
              </div>

              {/* Main Content Area */}
              <div className="lg:col-span-3">
                <div className="bg-card/90 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-border">
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
                      onContextChange={handleWizardContextChange}
                      refreshPresentation={refreshPresentation}
                    />
                  )}
                  {currentStep === 2 && (
                    <IllustrationStep
                      presentation={presentation}
                      currentSlide={currentSlide}
                      setCurrentSlide={setCurrentSlide}
                      updateSlide={updateSlide}
                      onContextChange={handleWizardContextChange}
                      refreshPresentation={refreshPresentation}
                    />
                  )}
                  {currentStep === 3 && (
                    <CompiledStep
                      presentation={presentation}
                      currentSlide={currentSlide}
                      setCurrentSlide={setCurrentSlide}
                      onContextChange={handleWizardContextChange}
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
              </div>
            </div>
          </div>
        </div>
      )}
    </ClientWrapper>
  );
}