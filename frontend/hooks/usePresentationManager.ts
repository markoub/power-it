import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Presentation } from '@/lib/types';
import { api } from '@/lib/api';
import { usePresentationPolling } from './usePresentationPolling';

interface UsePresentationManagerOptions {
  presentationId: string;
  onStepUpdate?: (presentation: Presentation) => void;
  onStepComplete?: (stepName: string) => void;
  verboseLogging?: boolean;
}

interface UsePresentationManagerReturn {
  presentation: Presentation | null;
  isLoading: boolean;
  error: string | null;
  isPolling: boolean;
  refreshPresentation: () => Promise<any>;
  setPresentationState: (presentation: Presentation) => void;
}

export function usePresentationManager({
  presentationId,
  onStepUpdate,
  onStepComplete,
  verboseLogging = false
}: UsePresentationManagerOptions): UsePresentationManagerReturn {
  const router = useRouter();
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Helper for structured logging
  const logInfo = useCallback((message: string, data?: any) => {
    if (verboseLogging) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  }, [verboseLogging]);

  const logError = useCallback((message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  }, []);

  // Initialize polling hook but start it manually after initial load
  const {
    isPolling,
    refreshPresentation: pollRefresh,
    stopPolling,
    startPolling
  } = usePresentationPolling({
    presentationId,
    onPresentationUpdate: (updatedPresentation) => {
      setPresentation(updatedPresentation);
      onStepUpdate?.(updatedPresentation);
    },
    onStepComplete,
    verboseLogging
  });

  // Initial load function
  const loadInitialPresentation = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Stop polling during initial load
      stopPolling();
      
      logInfo(`Loading initial presentation: ${presentationId}`);
      const fetchedPresentation = await api.getPresentation(presentationId);
      
      if (fetchedPresentation) {
        setPresentation(fetchedPresentation);
        onStepUpdate?.(fetchedPresentation);
        setIsInitialized(true);
        logInfo('Initial presentation loaded successfully');
        
        // Start polling after successful load
        startPolling();
      } else {
        const errorMsg = "Presentation not found";
        setError(errorMsg);
        logError(errorMsg);
        setTimeout(() => router.push("/"), 3000);
      }
    } catch (err) {
      const errorMsg = "Failed to load presentation";
      logError(errorMsg, err);
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [presentationId, onStepUpdate, router, stopPolling, startPolling, logInfo, logError]);

  // Combined refresh function that uses polling refresh
  const refreshPresentation = useCallback(async () => {
    return pollRefresh();
  }, [pollRefresh]);

  // Set presentation state (for external updates)
  const setPresentationState = useCallback((newPresentation: Presentation) => {
    setPresentation(newPresentation);
  }, []);

  // Load initial presentation on mount
  useEffect(() => {
    if (!isInitialized) {
      loadInitialPresentation();
    }
    
    // Cleanup: stop polling on unmount
    return () => {
      stopPolling();
    };
  }, [isInitialized, loadInitialPresentation, stopPolling]);

  return {
    presentation,
    isLoading,
    error,
    isPolling,
    refreshPresentation,
    setPresentationState
  };
}