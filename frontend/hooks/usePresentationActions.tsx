import { useState, useCallback } from 'react';
import { Presentation } from '@/lib/types';
import { api } from '@/lib/api';
import { toast } from '@/components/ui/use-toast';
import { ToastAction } from '@/components/ui/toast';

interface UsePresentationActionsOptions {
  presentation: Presentation | null;
  verboseLogging?: boolean;
}

export function usePresentationActions({
  presentation,
  verboseLogging = false
}: UsePresentationActionsOptions) {
  const [isProcessingStep, setIsProcessingStep] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Helper for structured logging
  const logInfo = useCallback((message: string, data?: any) => {
    if (verboseLogging) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  }, [verboseLogging]);

  const logError = useCallback((message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  }, []);

  // Export to PPTX
  const handleExport = useCallback(async () => {
    if (!presentation) return;

    setIsExporting(true);
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
    } finally {
      setIsExporting(false);
    }
  }, [presentation, logError]);

  // Run presentation step
  const runPresentationStep = useCallback(async (stepName: string, onComplete?: () => void) => {
    if (!presentation) return;

    try {
      setIsProcessingStep(true);
      
      logInfo(`🔄 Running step: ${stepName}`);

      // Call the API to run the step
      const result = await api.runPresentationStep(
        String(presentation.id),
        stepName,
      );

      if (result) {
        toast({
          title: "Step initiated",
          description: `Starting ${stepName} generation process...`,
        });

        onComplete?.();
        return true;
      } else {
        throw new Error("Failed to start the step");
      }
    } catch (error) {
      logError(`Error running step ${stepName}:`, error);
      toast({
        title: "Error",
        description: `Failed to run ${stepName}. Please try again.`,
        variant: "destructive",
      });
      return false;
    } finally {
      setIsProcessingStep(false);
    }
  }, [presentation, logInfo, logError]);

  // Continue to next step
  const continueToNextStep = useCallback(async (
    stepApiNames: string[],
    isStepCompleted: (index: number) => boolean,
    onStepStarted?: (stepIndex: number, stepName: string) => void
  ) => {
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
        logInfo("All steps are already completed");
        setIsProcessingStep(false);
        return;
      }

      const nextStepName = stepApiNames[nextStepIndex];

      // Call the API to run the next step
      const result = await api.runPresentationStep(
        String(presentation.id),
        nextStepName,
      );

      if (result) {
        toast({
          title: "Step initiated",
          description: `Starting ${nextStepName} generation process...`,
        });

        onStepStarted?.(nextStepIndex, nextStepName);
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
  }, [presentation, logInfo, logError]);

  // Rerun step
  const rerunStep = useCallback(async (
    stepIndex: number,
    stepApiNames: string[],
    steps: string[],
    onStepStarted?: (stepIndex: number, stepName: string) => void
  ) => {
    if (!presentation) return;

    try {
      setIsProcessingStep(true);
      
      const stepName = stepApiNames[stepIndex];
      logInfo(`🔄 Rerunning step: ${stepName} (index: ${stepIndex})`);
      
      // Call the API to rerun the step
      const result = await api.runPresentationStep(
        typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id,
        stepName,
      );

      if (result) {
        toast({
          title: "Step rerun initiated",
          description: `${steps[stepIndex]} is being regenerated...`,
        });

        onStepStarted?.(stepIndex, stepName);
      } else {
        throw new Error("Failed to rerun the step");
      }
    } catch (error) {
      logError("Error rerunning step:", error);
      toast({
        title: "Error",
        description: `Failed to rerun ${steps[stepIndex]}. Please try again.`,
        variant: "destructive",
      });
    } finally {
      setIsProcessingStep(false);
    }
  }, [presentation, logInfo, logError]);

  // Delete presentation
  const deletePresentation = useCallback(async (id: string) => {
    try {
      const success = await api.deletePresentation(id);
      if (success) {
        toast({
          title: "Presentation deleted",
          description: "The presentation has been deleted successfully.",
        });
        return true;
      }
      throw new Error("Failed to delete presentation");
    } catch (error) {
      logError("Error deleting presentation:", error);
      toast({
        title: "Error",
        description: "Failed to delete presentation. Please try again.",
        variant: "destructive",
      });
      return false;
    }
  }, [logError]);

  return {
    isProcessingStep,
    isExporting,
    handleExport,
    runPresentationStep,
    continueToNextStep,
    rerunStep,
    deletePresentation
  };
}