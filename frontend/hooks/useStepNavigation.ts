import { useState, useCallback, useRef, useEffect } from 'react';
import { Presentation, PresentationStep } from '@/lib/types';
import { toast } from '@/components/ui/use-toast';

interface UseStepNavigationOptions {
  steps: string[];
  stepApiNames: string[];
  presentation: Presentation | null;
  verboseLogging?: boolean;
}

export function useStepNavigation({
  steps,
  stepApiNames,
  presentation,
  verboseLogging = false
}: UseStepNavigationOptions) {
  const [currentStep, setCurrentStep] = useState(0);
  const [hasManuallyNavigated, setHasManuallyNavigated] = useState(false);
  
  // Refs to avoid stale closures
  const currentStepRef = useRef(currentStep);
  const hasManuallyNavigatedRef = useRef(hasManuallyNavigated);
  
  // Update refs when state changes
  useEffect(() => {
    currentStepRef.current = currentStep;
  }, [currentStep]);
  
  useEffect(() => {
    hasManuallyNavigatedRef.current = hasManuallyNavigated;
  }, [hasManuallyNavigated]);

  // Helper for structured logging
  const logInfo = useCallback((message: string, data?: any) => {
    if (verboseLogging) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  }, [verboseLogging]);

  // Check if a step is completed
  const isStepCompleted = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    if (stepIndex === 0 && verboseLogging) { // Research step
      logInfo(`🔍 Checking step completion for ${stepName} (index ${stepIndex}):`, {
        availableSteps: presentation.steps.map(s => ({ step: s.step, status: s.status })),
        foundStep: step ? { step: step.step, status: step.status } : null,
        isCompleted: step?.status === "completed"
      });
    }

    return step?.status === "completed";
  }, [presentation, stepApiNames, verboseLogging, logInfo]);

  // Check if a step is pending
  const isStepPending = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "pending";
  }, [presentation, stepApiNames]);

  // Check if a step is processing
  const isStepProcessing = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "processing";
  }, [presentation, stepApiNames]);

  // Check if a step has failed
  const isStepFailed = useCallback((stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;

    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find((s) => s.step === stepName);

    return step?.status === "failed";
  }, [presentation, stepApiNames]);

  // Get the highest step that is completed + 1 (if not the last step)
  const determineCurrentStep = useCallback((presentationData: Presentation) => {
    if (!presentationData.steps || !Array.isArray(presentationData.steps)) {
      return 0; // Default to first step if no steps data
    }

    let highestCompletedStep = -1;
    let firstProcessingStep = -1;
    
    for (let i = 0; i < stepApiNames.length; i++) {
      const stepName = stepApiNames[i];
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
  }, [stepApiNames]);

  // Handle direct step navigation
  const handleStepChange = useCallback((stepIndex: number) => {
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
  }, [currentStep, hasManuallyNavigated, isStepCompleted, logInfo]);

  // Update current step based on presentation data
  const updateCurrentStep = useCallback((presentationData: Presentation, force = false) => {
    // Only update current step automatically if user hasn't manually navigated or if forced
    if (!hasManuallyNavigatedRef.current || force) {
      const newCurrentStep = determineCurrentStep(presentationData);
      if (newCurrentStep !== currentStepRef.current) {
        logInfo(`🔄 Auto-updating current step from ${currentStepRef.current} to ${newCurrentStep}`);
        setCurrentStep(newCurrentStep);
        
        // Reset manual navigation flag if we auto-navigated due to completion
        if (force) {
          setHasManuallyNavigated(false);
        }
      }
    } else {
      logInfo(`🚫 Skipping auto step update because user manually navigated`);
    }
  }, [determineCurrentStep, logInfo]);

  // Reset navigation state
  const resetNavigation = useCallback(() => {
    setHasManuallyNavigated(false);
  }, []);

  // Get arrays of step statuses
  const getStepStatuses = useCallback(() => {
    const completedSteps = stepApiNames.map((_, index) => isStepCompleted(index));
    const pendingSteps = stepApiNames.map((_, index) => isStepPending(index));
    const processingSteps = stepApiNames.map((_, index) => isStepProcessing(index));
    const failedSteps = stepApiNames.map((_, index) => isStepFailed(index));

    return {
      completedSteps,
      pendingSteps,
      processingSteps,
      failedSteps
    };
  }, [stepApiNames, isStepCompleted, isStepPending, isStepProcessing, isStepFailed]);

  return {
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
  };
}