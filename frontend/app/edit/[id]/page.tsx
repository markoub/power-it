"use client";

import { useEffect, useState, useMemo, useCallback, useRef } from "react";
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
  const [currentSlide, setCurrentSlide] = useState<Slide | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wizardContext, setWizardContext] = useState<"all" | "single">("all");
  const [isProcessingStep, setIsProcessingStep] = useState(false);
  const [hasManuallyNavigated, setHasManuallyNavigated] = useState(false);
  
  // Refs to avoid stale closures in polling
  const presentationRef = useRef(presentation);
  const currentStepRef = useRef(currentStep);
  const hasManuallyNavigatedRef = useRef(hasManuallyNavigated);
  
  // Update refs when state changes
  useEffect(() => {
    presentationRef.current = presentation;
  }, [presentation]);
  
  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);
  
  useEffect(() => {
    hasManuallyNavigatedRef.current = hasManuallyNavigated;
  }, [hasManuallyNavigated]);

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

    let pollInterval: NodeJS.Timeout;
    let slowPollInterval: NodeJS.Timeout;
    let consecutiveUnchangedPolls = 0;
    const MAX_UNCHANGED_POLLS = 5;
    let lastPresentationHash = JSON.stringify(presentation.steps);

    const getCurrentPollingInterval = () => {
      const currentPresentation = presentationRef.current;
      if (!currentPresentation?.steps) return 10000; // Default 10 seconds if no steps
      
      const hasProcessingSteps = currentPresentation.steps.some(step => step.status === "processing");
      const hasPendingSteps = currentPresentation.steps.some(step => step.status === "pending");
      
      if (hasProcessingSteps) return 1000; // 1 second when processing for faster updates
      if (hasPendingSteps) return 2000; // 2 seconds when pending
      return 10000; // 10 seconds when everything is stable
    };

    const pollPresentation = async () => {
      try {
        const updatedPresentation = await api.getPresentation(unwrappedParams.id);
        if (updatedPresentation) {
          const newPresentationHash = JSON.stringify(updatedPresentation.steps);
          
          // Only update if there are actual changes to steps
          if (newPresentationHash !== lastPresentationHash) {
            logInfo('🔄 Presentation data updated from polling');
            setPresentation(updatedPresentation);
            lastPresentationHash = newPresentationHash;
            
            // Check if a step that was processing is now completed
            const oldSteps = JSON.parse(lastPresentationHash);
            const nowCompleted = updatedPresentation.steps.some((s) => {
              const oldStep = oldSteps?.find((os: any) => os.step === s.step);
              return oldStep?.status === "processing" && s.status === "completed";
            });
            
            // Only update current step automatically if user hasn't manually navigated
            // OR if a processing step just completed
            if (!hasManuallyNavigatedRef.current || nowCompleted) {
              const newCurrentStep = determineCurrentStep(updatedPresentation);
              if (newCurrentStep !== currentStepRef.current) {
                logInfo(`🔄 Polling: Auto-updating current step from ${currentStepRef.current} to ${newCurrentStep}`);
                setCurrentStep(newCurrentStep);
                
                // Reset manual navigation flag if we auto-navigated due to completion
                if (nowCompleted) {
                  setHasManuallyNavigated(false);
                }
              }
            } else {
              logInfo(`🚫 Polling: Skipping auto step update because user manually navigated`);
            }
            
            // Reset consecutive unchanged counter
            consecutiveUnchangedPolls = 0;
            
            // If we were in slow polling mode and detected changes, switch back to normal polling
            if (slowPollInterval) {
              clearInterval(slowPollInterval);
              slowPollInterval = undefined;
              // Instead of calling startNormalPolling recursively, just set up a new interval
              const intervalMs = getCurrentPollingInterval();
              logInfo(`🔄 Resuming normal polling with ${intervalMs}ms interval`);
              pollInterval = setInterval(pollPresentation, intervalMs);
            }
          } else {
            consecutiveUnchangedPolls++;
            logInfo(`🔄 No changes detected (${consecutiveUnchangedPolls}/${MAX_UNCHANGED_POLLS})`);
            
            // If we've had several polls with no changes and nothing is running,
            // slow down polling significantly
            if (consecutiveUnchangedPolls >= MAX_UNCHANGED_POLLS && !slowPollInterval) {
              const hasActiveProcessing = updatedPresentation.steps?.some(
                step => step.status === "processing" || step.status === "pending"
              );
              if (!hasActiveProcessing) {
                logInfo('🔄 No active processing, switching to slow polling');
                clearInterval(pollInterval);
                pollInterval = undefined;
                
                // Start slow polling
                slowPollInterval = setInterval(pollPresentation, 30000);
              }
            }
          }
        }
      } catch (error) {
        logError('Error polling presentation updates:', error);
      }
    };

    const startNormalPolling = () => {
      if (pollInterval) return; // Prevent multiple intervals
      
      const intervalMs = getCurrentPollingInterval();
      logInfo(`🔄 Starting polling with ${intervalMs}ms interval`);
      pollInterval = setInterval(pollPresentation, intervalMs);
    };

    startNormalPolling();

    return () => {
      logInfo('🔄 Cleaning up polling intervals');
      if (pollInterval) clearInterval(pollInterval);
      if (slowPollInterval) clearInterval(slowPollInterval);
    };
  }, [unwrappedParams.id]); // Only depend on presentation ID, not on state that changes within the effect

  // Manual refresh function that components can call
  const refreshPresentation = async () => {
    try {
      const updatedPresentation = await api.getPresentation(unwrappedParams.id);
      if (updatedPresentation) {
        logInfo('🔄 Presentation data manually refreshed');
        setPresentation(updatedPresentation);
        
        // Only update current step automatically if user hasn't manually navigated
        if (!hasManuallyNavigated) {
          const newCurrentStep = determineCurrentStep(updatedPresentation);
          setCurrentStep(newCurrentStep);
        }
        
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
    let firstProcessingStep = -1;
    
    for (let i = 0; i < STEP_API_NAMES.length; i++) {
      const stepName = STEP_API_NAMES[i];
      const step = presentationData.steps.find((s: any) => s.step === stepName);

      if (step && step.status === "completed") {
        highestCompletedStep = i;
      } else if (step && step.status === "processing" && firstProcessingStep === -1) {
        firstProcessingStep = i;
      } else {
        // Found first incomplete step
        break;
      }
    }

    // If a step is currently processing, show that step
    if (firstProcessingStep !== -1) {
      return firstProcessingStep;
    }
    
    // If nothing is completed, start with step 0
    if (highestCompletedStep === -1) return 0;

    // Show the last completed step so users can see their results
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
        // Reset manual navigation flag on initial load
        setHasManuallyNavigated(false);

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

  // Memoize step checking functions to prevent recreation on every render
  const isStepCompleted = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = STEP_API_NAMES[stepIndex];
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
  }, [presentation, VERBOSE_LOGGING]);

  // Check if a step is pending/processing
  const isStepPending = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = STEP_API_NAMES[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "pending";
  }, [presentation]);

  // Check if a step is processing
  const isStepProcessing = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = STEP_API_NAMES[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "processing";
  }, [presentation]);

  // Check if a step has failed
  const isStepFailed = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = STEP_API_NAMES[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "failed";
  }, [presentation]);

  // Memoize the completed steps array to ensure React detects changes
  const completedSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const completed = STEP_API_NAMES.map((name, index) => isStepCompleted(index));
    
    return completed;
  }, [presentation?.steps, isStepCompleted]);

  // Memoize the pending steps array
  const pendingSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const pending = STEP_API_NAMES.map((name, index) => isStepPending(index));
    
    return pending;
  }, [presentation?.steps, isStepPending]);

  // Memoize the processing steps array
  const processSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const processing = STEP_API_NAMES.map((name, index) => isStepProcessing(index));
    
    return processing;
  }, [presentation?.steps, isStepProcessing]);

  // Memoize the failed steps array
  const failedSteps = useMemo(() => {
    if (!presentation?.steps) return [];
    
    const failed = STEP_API_NAMES.map((name, index) => isStepFailed(index));
    
    return failed;
  }, [presentation?.steps, isStepFailed]);

  // Log step arrays for debugging (outside of memoization to avoid issues)
  useEffect(() => {
    if (VERBOSE_LOGGING && presentation?.steps) {
      logInfo('🔄 Step arrays updated:', {
        completedSteps: completedSteps.map((isCompleted, index) => ({
          step: STEP_API_NAMES[index],
          completed: isCompleted
        })),
        pendingSteps: pendingSteps.map((isPending, index) => ({
          step: STEP_API_NAMES[index],
          pending: isPending
        })),
        processSteps: processSteps.map((isProcessing, index) => ({
          step: STEP_API_NAMES[index],
          processing: isProcessing
        })),
        failedSteps: failedSteps.map((isFailed, index) => ({
          step: STEP_API_NAMES[index],
          failed: isFailed
        }))
      });
    }
  }, [completedSteps, pendingSteps, processSteps, failedSteps, VERBOSE_LOGGING]);

  // Continue to next step function
  const handleContinueToNextStep = async () => {
    if (!presentation) return;

    try {
      setIsProcessingStep(true);

      // Get the API step name for the next uncompleted step
      let nextStepIndex = -1;
      for (let i = 0; i < STEP_API_NAMES.length; i++) {
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

      const nextStepName = STEP_API_NAMES[nextStepIndex];

      // Call the API to run the next step
      const result = await api.runPresentationStep(
        String(presentation.id),
        nextStepName,
      );

      if (result) {
        toast({
          title: "Step initiated",
          description: `Starting ${STEPS[nextStepIndex]} generation process...`,
        });

        // Immediately update the step status to processing locally
        const updatedSteps = presentation.steps.map(s => 
          s.step === nextStepName ? { ...s, status: "processing" } : s
        );
        setPresentation({ ...presentation, steps: updatedSteps });
        
        // Navigate to the processing step
        setCurrentStep(nextStepIndex);
        setHasManuallyNavigated(false); // Allow auto-navigation during processing
        
        // Force immediate refresh to get latest status
        setTimeout(async () => {
          await refreshPresentation();
        }, 500);
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
    for (let i = 0; i < STEP_API_NAMES.length; i++) {
      if (!isStepCompleted(i)) {
        // If the step before this one is completed, we show the continue button
        return i > 0 && isStepCompleted(i - 1);
      }
    }

    return false; // All steps completed or no steps found
  };

  // Handle direct step navigation
  const handleStepChange = (stepIndex: number) => {
    logInfo(`🔄 Step change requested: ${stepIndex}, current: ${currentStep}, hasManuallyNavigated: ${hasManuallyNavigated}`);
    
    // We can always navigate to current step
    if (stepIndex === currentStep) return;

    // Allow navigation to completed steps
    if (isStepCompleted(stepIndex)) {
      logInfo(`✅ Navigating to completed step ${stepIndex}`);
      setCurrentStep(stepIndex);
      setHasManuallyNavigated(true);
      return;
    }

    // Allow navigation to the first uncompleted step (next step after completed ones)
    if (stepIndex > 0 && isStepCompleted(stepIndex - 1)) {
      logInfo(`✅ Navigating to next step ${stepIndex} after completed step ${stepIndex - 1}`);
      setCurrentStep(stepIndex);
      setHasManuallyNavigated(true);
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

  // Handle rerunning a step
  const handleRerunStep = async (stepIndex: number) => {
    if (!presentation) return;

    try {
      setIsProcessingStep(true);
      
      const stepName = STEP_API_NAMES[stepIndex];
      logInfo(`🔄 Rerunning step: ${stepName} (index: ${stepIndex})`);

      // Immediately update the step status to processing locally
      const updatedSteps = presentation.steps.map(s => 
        s.step === stepName ? { ...s, status: "processing" } : s
      );
      setPresentation({ ...presentation, steps: updatedSteps });
      
      // Navigate to the processing step
      setCurrentStep(stepIndex);
      setHasManuallyNavigated(false); // Allow auto-navigation during processing
      
      // Call the API to rerun the step
      const result = await api.runPresentationStep(
        typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id,
        stepName,
      );

      if (result) {
        toast({
          title: "Step rerun initiated",
          description: `${STEPS[stepIndex]} is being regenerated...`,
        });

        // Force immediate refresh to get latest status
        setTimeout(async () => {
          await refreshPresentation();
        }, 500);
      } else {
        throw new Error("Failed to rerun the step");
      }
    } catch (error) {
      logError("Error rerunning step:", error);
      toast({
        title: "Error",
        description: `Failed to rerun ${STEPS[stepIndex]}. Please try again.`,
        variant: "destructive",
      });
    } finally {
      setIsProcessingStep(false);
    }
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
              processSteps={processSteps}
              failedSteps={failedSteps}
              presentationId={presentation.id}
              onRerunStep={handleRerunStep}
            />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
              {/* Wizard Sidebar */}
              <div className="lg:col-span-1">
                <Wizard
                  presentation={presentation}
                  currentSlide={currentSlide}
                  context={wizardContext}
                  step={STEPS[currentStep]}
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