import { useEffect, useRef, useState, useCallback } from 'react';
import { Presentation } from '@/lib/types';
import { api } from '@/lib/api';

interface UsePresentationPollingOptions {
  presentationId: string;
  onPresentationUpdate?: (presentation: Presentation) => void;
  onStepComplete?: (stepName: string) => void;
  verboseLogging?: boolean;
}

export function usePresentationPolling({
  presentationId,
  onPresentationUpdate,
  onStepComplete,
  verboseLogging = false
}: UsePresentationPollingOptions) {
  const [isPolling, setIsPolling] = useState(false);
  
  // Refs to avoid stale closures
  const presentationRef = useRef<Presentation | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const slowPollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const consecutiveUnchangedPollsRef = useRef(0);
  const lastPresentationHashRef = useRef<string>('');
  
  const MAX_UNCHANGED_POLLS = 5;
  const STEP_API_NAMES = ["research", "slides", "images", "compiled", "pptx"];

  // Helper for structured logging
  const logInfo = useCallback((message: string, data?: any) => {
    if (verboseLogging) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  }, [verboseLogging]);

  const logError = useCallback((message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  }, []);

  // Get appropriate polling interval based on presentation status
  const getCurrentPollingInterval = useCallback(() => {
    const presentation = presentationRef.current;
    if (!presentation?.steps) return 10000; // Default 10 seconds if no steps
    
    const hasProcessingSteps = presentation.steps.some(step => step.status === "processing");
    const hasPendingSteps = presentation.steps.some(step => step.status === "pending");
    
    if (hasProcessingSteps) return 1000; // 1 second when processing for faster updates
    if (hasPendingSteps) return 2000; // 2 seconds when pending
    return 10000; // 10 seconds when everything is stable
  }, []);

  // Poll for presentation updates
  const pollPresentation = useCallback(async () => {
    try {
      const updatedPresentation = await api.getPresentation(presentationId);
      if (updatedPresentation) {
        const newPresentationHash = JSON.stringify(updatedPresentation.steps);
        
        // Only update if there are actual changes to steps
        if (newPresentationHash !== lastPresentationHashRef.current) {
          logInfo('🔄 Presentation data updated from polling');
          
          // Check if a step that was processing is now completed
          if (lastPresentationHashRef.current && onStepComplete) {
            const oldSteps = JSON.parse(lastPresentationHashRef.current);
            updatedPresentation.steps?.forEach((step) => {
              const oldStep = oldSteps?.find((os: any) => os.step === step.step);
              if (oldStep?.status === "processing" && step.status === "completed") {
                onStepComplete(step.step);
              }
            });
          }
          
          presentationRef.current = updatedPresentation;
          lastPresentationHashRef.current = newPresentationHash;
          onPresentationUpdate?.(updatedPresentation);
          
          // Reset consecutive unchanged counter
          consecutiveUnchangedPollsRef.current = 0;
          
          // If we were in slow polling mode and detected changes, switch back to normal polling
          if (slowPollIntervalRef.current) {
            clearInterval(slowPollIntervalRef.current);
            slowPollIntervalRef.current = null;
            startNormalPolling();
          }
        } else {
          consecutiveUnchangedPollsRef.current++;
          logInfo(`🔄 No changes detected (${consecutiveUnchangedPollsRef.current}/${MAX_UNCHANGED_POLLS})`);
          
          // If we've had several polls with no changes and nothing is running,
          // slow down polling significantly
          if (consecutiveUnchangedPollsRef.current >= MAX_UNCHANGED_POLLS && !slowPollIntervalRef.current) {
            const hasActiveProcessing = updatedPresentation.steps?.some(
              step => step.status === "processing" || step.status === "pending"
            );
            if (!hasActiveProcessing) {
              logInfo('🔄 No active processing, switching to slow polling');
              stopNormalPolling();
              
              // Start slow polling (30 seconds)
              slowPollIntervalRef.current = setInterval(pollPresentation, 30000);
            }
          }
        }
      }
    } catch (error) {
      logError('Error polling presentation updates:', error);
    }
  }, [presentationId, onPresentationUpdate, onStepComplete, logInfo, logError]);

  // Start normal polling
  const startNormalPolling = useCallback(() => {
    if (pollIntervalRef.current) return; // Prevent multiple intervals
    
    const intervalMs = getCurrentPollingInterval();
    logInfo(`🔄 Starting polling with ${intervalMs}ms interval`);
    pollIntervalRef.current = setInterval(pollPresentation, intervalMs);
    setIsPolling(true);
  }, [getCurrentPollingInterval, pollPresentation, logInfo]);

  // Stop normal polling
  const stopNormalPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  // Stop all polling
  const stopPolling = useCallback(() => {
    logInfo('🔄 Stopping all polling');
    stopNormalPolling();
    if (slowPollIntervalRef.current) {
      clearInterval(slowPollIntervalRef.current);
      slowPollIntervalRef.current = null;
    }
    setIsPolling(false);
  }, [stopNormalPolling, logInfo]);

  // Manual refresh function
  const refreshPresentation = useCallback(async () => {
    try {
      const updatedPresentation = await api.getPresentation(presentationId);
      if (updatedPresentation) {
        logInfo('🔄 Presentation data manually refreshed');
        presentationRef.current = updatedPresentation;
        lastPresentationHashRef.current = JSON.stringify(updatedPresentation.steps);
        onPresentationUpdate?.(updatedPresentation);
        return updatedPresentation;
      }
    } catch (error) {
      logError('Error manually refreshing presentation:', error);
    }
    return null;
  }, [presentationId, onPresentationUpdate, logInfo, logError]);

  // Start polling when hook is mounted
  useEffect(() => {
    startNormalPolling();
    
    return () => {
      stopPolling();
    };
  }, []); // Empty deps - we only want to start/stop on mount/unmount

  // Update polling interval when presentation changes
  useEffect(() => {
    if (!isPolling) return;
    
    // Restart polling with new interval if needed
    const currentInterval = getCurrentPollingInterval();
    stopNormalPolling();
    
    logInfo(`🔄 Adjusting polling interval to ${currentInterval}ms`);
    pollIntervalRef.current = setInterval(pollPresentation, currentInterval);
  }, [isPolling]); // Only depend on isPolling state

  return {
    isPolling,
    refreshPresentation,
    stopPolling,
    startPolling: startNormalPolling
  };
}