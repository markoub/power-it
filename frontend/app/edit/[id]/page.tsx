"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Download, Save, Loader2 } from "lucide-react";
import type { Presentation, Slide } from "@/lib/types";
import Link from "next/link";
import { PatternBackground } from "@/components/ui-elements";
import { toast } from "@/components/ui/use-toast";
import { ToastAction } from "@/components/ui/toast";
import WorkflowSteps from "@/components/workflow-steps";
import ResearchStep from "@/components/steps/research-step";
import SlidesStep from "@/components/steps/slides-step";
import IllustrationStep from "@/components/steps/illustration-step";
import CompiledStep from "@/components/steps/compiled-step";
import PptxStep from "@/components/steps/pptx-step";
import Wizard from "@/components/wizard/wizard";
import { api } from "@/lib/api";
import { v4 as uuidv4 } from "uuid";
import ClientWrapper from "@/components/client-wrapper";
import { use } from "react";
import React from "react";

export default function EditPage({ params }: { params: { id: string } }) {
  // Properly unwrap params to get the id
  const unwrappedParams = React.use(params);
  
  // Development flag for verbose logging - set to false to reduce console spam
  const VERBOSE_LOGGING = process.env.NODE_ENV === 'development' && false;
  
  const router = useRouter();
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [currentSlide, setCurrentSlide] = useState<Slide | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wizardContext, setWizardContext] = useState<"all" | "single">("all");
  const [isProcessingStep, setIsProcessingStep] = useState(false);

  const steps = ["Research", "Slides", "Illustration", "Compiled", "PPTX"];
  const stepApiNames = ["research", "slides", "images", "compiled", "pptx"];

  // Helper for structured logging
  const logInfo = (message: string, data?: any) => {
    if (VERBOSE_LOGGING) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  };

  const logError = (message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  };

  useEffect(() => {
    // Load presentation from API
    fetchPresentation();
  }, [unwrappedParams.id]);

  // Add periodic polling to keep presentation data up to date
  useEffect(() => {
    if (!presentation) return;

    // Use adaptive polling - faster when things are processing, slower when stable
    const getCurrentPollingInterval = () => {
      if (!presentation.steps) return 5000; // Default 5 seconds if no steps
      
      const hasRunningSteps = presentation.steps.some(step => step.status === "running");
      const hasPendingSteps = presentation.steps.some(step => step.status === "pending");
      
      if (hasRunningSteps) return 2000; // 2 seconds when processing
      if (hasPendingSteps) return 3000; // 3 seconds when pending
      return 10000; // 10 seconds when everything is stable
    };

    let pollInterval: NodeJS.Timeout;
    let consecutiveUnchangedPolls = 0;
    const MAX_UNCHANGED_POLLS = 3;

    const startPolling = () => {
      const intervalMs = getCurrentPollingInterval();
      
      pollInterval = setInterval(async () => {
        try {
          const updatedPresentation = await api.getPresentation(unwrappedParams.id);
          if (updatedPresentation) {
            // Only update if there are actual changes to steps
            const hasStepChanges = updatedPresentation.steps?.some((newStep, index) => {
              const currentStep = presentation.steps?.[index];
              return !currentStep || 
                     currentStep.status !== newStep.status || 
                     JSON.stringify(currentStep.result) !== JSON.stringify(newStep.result);
            });

            if (hasStepChanges) {
              logInfo('🔄 Presentation data updated from polling');
              setPresentation(updatedPresentation);
              
              // Update current step if needed
              const newCurrentStep = determineCurrentStep(updatedPresentation);
              if (newCurrentStep !== currentStep) {
                setCurrentStep(newCurrentStep);
              }
              
              // Reset consecutive unchanged counter
              consecutiveUnchangedPolls = 0;
              
              // Restart polling with new interval based on updated state
              clearInterval(pollInterval);
              startPolling();
            } else {
              consecutiveUnchangedPolls++;
              
              // If we've had several polls with no changes and nothing is running,
              // slow down polling significantly
              if (consecutiveUnchangedPolls >= MAX_UNCHANGED_POLLS) {
                const hasActiveProcessing = updatedPresentation.steps?.some(
                  step => step.status === "running" || step.status === "pending"
                );
                if (!hasActiveProcessing) {
                  clearInterval(pollInterval);
                  // Switch to very slow polling for completed presentations
                  pollInterval = setInterval(async () => {
                    // Just check once every 30 seconds for completed presentations
                    try {
                      const check = await api.getPresentation(unwrappedParams.id);
                      if (check && JSON.stringify(check) !== JSON.stringify(updatedPresentation)) {
                        setPresentation(check);
                        consecutiveUnchangedPolls = 0;
                        clearInterval(pollInterval);
                        startPolling(); // Resume normal polling if something changed
                      }
                                         } catch (error) {
                       logError('Error in slow polling:', error);
                     }
                  }, 30000);
                }
              }
            }
          }
        } catch (error) {
          logError('Error polling presentation updates:', error);
        }
      }, intervalMs);
    };

    startPolling();

    return () => clearInterval(pollInterval);
  }, [presentation, currentStep, unwrappedParams.id]);

  // Manual refresh function that components can call
  const refreshPresentation = async () => {
    try {
      const updatedPresentation = await api.getPresentation(unwrappedParams.id);
      if (updatedPresentation) {
        logInfo('🔄 Presentation data manually refreshed');
        setPresentation(updatedPresentation);
        
        // Update current step
        const newCurrentStep = determineCurrentStep(updatedPresentation);
        setCurrentStep(newCurrentStep);
        
        return updatedPresentation;
      }
    } catch (error) {
      logError('Error manually refreshing presentation:', error);
    }
    return null;
  };

  // Get the highest step that is completed + 1 (if not the last step)
  const determineCurrentStep = (presentationData: any) => {
    if (!presentationData.steps || !Array.isArray(presentationData.steps)) {
      return 0; // Default to first step if no steps data
    }

    let highestCompletedStep = -1;
    for (let i = 0; i < stepApiNames.length; i++) {
      const stepName = stepApiNames[i];
      const step = presentationData.steps.find((s: any) => s.step === stepName);

      if (step && step.status === "completed") {
        highestCompletedStep = i;
      } else {
        // Found first incomplete step
        break;
      }
    }

    // If nothing is completed, start with step 0
    if (highestCompletedStep === -1) return 0;

    // Show the last completed step so users can see their results
    // Only advance to next step when user manually navigates
    return highestCompletedStep;
  };

  const fetchPresentation = async () => {
    setIsLoading(true);
    try {
      const fetchedPresentation = await api.getPresentation(unwrappedParams.id);
      if (fetchedPresentation) {
        setPresentation(fetchedPresentation);

        // Determine the current step based on completion status
        const newCurrentStep = determineCurrentStep(fetchedPresentation);
        setCurrentStep(newCurrentStep);

        if (
          fetchedPresentation.slides &&
          fetchedPresentation.slides.length > 0
        ) {
          setCurrentSlide(fetchedPresentation.slides[0]);
        }
        setError(null);
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

  const savePresentation = async () => {
    if (!presentation) return;

    setIsSaving(true);
    try {
      const updatedPresentation = await api.updatePresentation(
        presentation.id,
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
  };

  const addNewSlide = () => {
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
  };

  const updateSlide = (updatedSlide: Slide) => {
    if (!presentation) return;

    const updatedSlides = presentation.slides.map((slide) =>
      slide.id === updatedSlide.id ? updatedSlide : slide,
    );

    setPresentation({
      ...presentation,
      slides: updatedSlides,
    });
    setCurrentSlide(updatedSlide);
  };

  const deleteSlide = (slideId: string) => {
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
  };

  const handleExport = async () => {
    if (!presentation) return;

    toast({
      title: "PPTX Generation Started",
      description: "Your presentation is being generated on the server...",
    });

    try {
      // Assuming your backend endpoint for PPTX generation is '/api/generate-pptx-backend'
      // This needs to be an endpoint on your Python backend, not a Next.js API route.
      // Adjust the URL as per your actual backend API structure.
      const response = await fetch(
        "http://localhost:8000/api/v1/presentations/generate-pptx",
        {
          // Example backend URL
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(presentation),
        },
      );

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          // If parsing JSON fails, use text
          errorData = { message: (await response.text()) || "Unknown error" };
        }
        throw new Error(
          `Failed to generate PPTX: ${response.status} ${response.statusText} - ${errorData?.detail || errorData?.message || "Server error"}`,
        );
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      // Use presentation name for filename, default to 'presentation.pptx'
      const fileName = presentation.name
        ? `${presentation.name.replace(/[^a-z0-9_-\s\.]/gi, "_")}.pptx`
        : "presentation.pptx";
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: "Presentation Exported",
        description: "Your PPTX file has been downloaded successfully.",
        action: <ToastAction altText="OK">OK</ToastAction>,
      });
    } catch (error) {
      logError("Error during PPTX export:", error);
      toast({
        title: "Export Error",
        description:
          error instanceof Error
            ? error.message
            : "Failed to export PPTX. See console for details.",
        variant: "destructive",
        action: <ToastAction altText="OK">OK</ToastAction>,
      });
    }
  };

  const handleWizardContextChange = (context: "all" | "single") => {
    setWizardContext(context);
  };

  const applyWizardChanges = async (changes: any) => {
    if (!presentation) return;

    if (changes.slide && wizardContext === "single" && currentSlide) {
      // Apply changes to current slide
      const updatedSlide = { ...currentSlide, ...changes.slide };
      updateSlide(updatedSlide);
    } else if (changes.slides && wizardContext === "all") {
      // Apply changes to all slides
      setPresentation({
        ...presentation,
        slides: changes.slides,
      });
    } else if (changes.presentation) {
      // Apply presentation-level changes (add/remove slides, etc.)
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

    await savePresentation();

    toast({
      title: "Changes applied",
      description: changes.presentation 
        ? "The presentation has been modified successfully."
        : "The suggested changes have been applied to your presentation.",
      action: <ToastAction altText="OK">OK</ToastAction>,
    });
  };

  // Check if a step is completed based on backend data
  const isStepCompleted = (stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    // Debug logging to understand what's happening
    if (stepIndex === 0 && VERBOSE_LOGGING) { // Research step
      logInfo(`🔍 Checking step completion for ${stepName} (index ${stepIndex}):`, {
        availableSteps: presentation.steps.map(s => ({ step: s.step, status: s.status })),
        foundStep: step ? { step: step.step, status: step.status } : null,
        isCompleted: step?.status === "completed"
      });
    }

    return step?.status === "completed";
  };

  // Check if a step is pending/processing
  const isStepPending = (stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "pending";
  };

  // Check if a step is processing
  const isStepProcessing = (stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "running";
  };

  // Memoize the completed steps array to ensure React detects changes
  const completedSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const completed = stepApiNames.map((name, index) => isStepCompleted(index));
    logInfo('🔄 Completed steps array updated:', completed.map((isCompleted, index) => ({
      step: stepApiNames[index],
      completed: isCompleted
    })));
    
    return completed;
  }, [presentation?.steps, stepApiNames]);

  // Memoize the pending steps array
  const pendingSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const pending = stepApiNames.map((name, index) => isStepPending(index));
    logInfo('🔄 Pending steps array updated:', pending.map((isPending, index) => ({
      step: stepApiNames[index],
      pending: isPending
    })));
    
    return pending;
  }, [presentation?.steps, stepApiNames]);

  // Memoize the processing steps array
  const processSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const processing = stepApiNames.map((name, index) => isStepProcessing(index));
    logInfo('🔄 Processing steps array updated:', processing.map((isProcessing, index) => ({
      step: stepApiNames[index],
      processing: isProcessing
    })));
    
    return processing;
  }, [presentation?.steps, stepApiNames]);

  // Continue to next step function
  const handleContinueToNextStep = async () => {
    if (!presentation) return;

    try {
      setIsProcessingStep(true);

      // Get the API step name for the next uncompleted step
      let nextStepIndex = -1;
      for (let i = 0; i < stepApiNames.length; i++) {
        if (!isStepCompleted(i)) {
          nextStepIndex = i;
          break;
        }
      }

      if (nextStepIndex === -1) {
        console.log("All steps are already completed");
        setIsProcessingStep(false);
        return;
      }

      const nextStepName = stepApiNames[nextStepIndex];

      // Call the API to run the next step
      const result = await api.runPresentationStep(
        presentation.id,
        nextStepName,
      );

      if (result) {
        toast({
          title: "Step initiated",
          description: `Starting ${steps[nextStepIndex]} generation process...`,
        });

        // Wait a bit for the step to be processed
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Refresh the presentation to get updated step status
        await fetchPresentation();

        // Don't automatically move to the next step - let user see the results
        // The determineCurrentStep function will now keep them on the completed step
      } else {
        throw new Error("Failed to start the next step");
      }
    } catch (error) {
      logError("Error continuing to next step:", error);
      toast({
        title: "Error",
        description: "Failed to continue to the next step. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessingStep(false);
    }
  };

  // Determine if continue button should be shown
  const shouldShowContinueButton = () => {
    if (!presentation || !presentation.steps) return false;

    // Find if there are any incomplete steps
    for (let i = 0; i < stepApiNames.length; i++) {
      if (!isStepCompleted(i)) {
        // If the step before this one is completed, we show the continue button
        return i > 0 && isStepCompleted(i - 1);
      }
    }

    return false; // All steps completed or no steps found
  };

  // Handle direct step navigation
  const handleStepChange = (stepIndex: number) => {
    logInfo(`🔄 Step change requested: ${stepIndex}, current: ${currentStep}`);
    logInfo(`🔍 Step completion status:`, {
      completedSteps: completedSteps,
      isStepCompleted: (index: number) => isStepCompleted(index),
      targetStepCompleted: isStepCompleted(stepIndex),
      previousStepCompleted: stepIndex > 0 ? isStepCompleted(stepIndex - 1) : false
    });
    
    // We can always navigate to current step
    if (stepIndex === currentStep) return;

    // Allow navigation to completed steps
    if (isStepCompleted(stepIndex)) {
      logInfo(`✅ Navigating to completed step ${stepIndex}`);
      setCurrentStep(stepIndex);
      return;
    }

    // Allow navigation to the first uncompleted step (next step after completed ones)
    if (stepIndex > 0 && isStepCompleted(stepIndex - 1)) {
      logInfo(`✅ Navigating to next step ${stepIndex} after completed step ${stepIndex - 1}`);
      setCurrentStep(stepIndex);
      return;
    }

    // Otherwise, show error message
    logInfo(`❌ Step ${stepIndex} navigation blocked`);
    toast({
      title: "Step unavailable",
      description: "You need to complete previous steps first.",
      variant: "destructive",
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
            <header className="flex justify-between items-center mb-6 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
              <div className="flex items-center gap-4">
                <Link href="/">
                  <Button
                    variant="outline"
                    size="icon"
                    className="rounded-full hover:bg-primary-50 hover:text-primary-600 transition-colors"
                  >
                    <ArrowLeft size={18} />
                  </Button>
                </Link>
                <h1 className="text-2xl font-bold gradient-text">
                  {presentation.name}
                </h1>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={savePresentation}
                  className="flex items-center gap-1 hover:bg-primary-50 hover:text-primary-600 transition-colors"
                  disabled={isSaving}
                  data-testid="save-button"
                >
                  {isSaving ? (
                    <span className="flex items-center gap-1">
                      <div className="h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                      Saving...
                    </span>
                  ) : (
                    <>
                      <Save size={18} />
                      Save
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleExport}
                  className="bg-primary hover:bg-primary-600 text-white flex items-center gap-1 transition-all duration-300 shadow-md hover:shadow-primary-500/25"
                  data-testid="export-pptx-button"
                >
                  <Download size={18} />
                  Export PPTX
                </Button>
              </div>
            </header>

            <WorkflowSteps
              steps={steps}
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
              processSteps={processSteps}
            />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
              {/* Wizard Sidebar */}
              <div className="lg:col-span-1">
                <Wizard
                  presentation={presentation}
                  currentSlide={currentSlide}
                  context={wizardContext}
                  step={steps[currentStep]}
                  onApplyChanges={applyWizardChanges}
                />
              </div>

              {/* Main Content Area */}
              <div className="lg:col-span-3">
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
