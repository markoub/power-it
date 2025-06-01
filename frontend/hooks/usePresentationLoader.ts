import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Presentation } from '@/lib/types';
import { api } from '@/lib/api';

interface UsePresentationLoaderOptions {
  presentationId: string;
  onPresentationLoaded?: (presentation: Presentation) => void;
  onError?: (error: string) => void;
  redirectOnError?: boolean;
  verboseLogging?: boolean;
}

interface UsePresentationLoaderReturn {
  presentation: Presentation | null;
  isLoading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

export function usePresentationLoader({
  presentationId,
  onPresentationLoaded,
  onError,
  redirectOnError = true,
  verboseLogging = false
}: UsePresentationLoaderOptions): UsePresentationLoaderReturn {
  const router = useRouter();
  const [presentation, setPresentation] = useState<Presentation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Helper for structured logging
  const logInfo = useCallback((message: string, data?: any) => {
    if (verboseLogging) {
      console.log(`[PowerIT] ${message}`, data || '');
    }
  }, [verboseLogging]);

  const logError = useCallback((message: string, error?: any) => {
    console.error(`[PowerIT Error] ${message}`, error || '');
  }, []);

  // Load presentation function
  const loadPresentation = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      logInfo(`Loading presentation: ${presentationId}`);
      const fetchedPresentation = await api.getPresentation(presentationId);
      
      if (fetchedPresentation) {
        setPresentation(fetchedPresentation);
        onPresentationLoaded?.(fetchedPresentation);
        logInfo('Presentation loaded successfully', fetchedPresentation);
      } else {
        const errorMsg = "Presentation not found";
        setError(errorMsg);
        onError?.(errorMsg);
        
        if (redirectOnError) {
          logInfo('Redirecting to home page in 3 seconds...');
          setTimeout(() => router.push("/"), 3000);
        }
      }
    } catch (err) {
      const errorMsg = "Failed to load presentation";
      logError(errorMsg, err);
      setError(errorMsg);
      onError?.(errorMsg);
      
      if (redirectOnError && err instanceof Error && err.message.includes('404')) {
        logInfo('Redirecting to home page in 3 seconds...');
        setTimeout(() => router.push("/"), 3000);
      }
    } finally {
      setIsLoading(false);
    }
  }, [presentationId, onPresentationLoaded, onError, redirectOnError, router, logInfo, logError]);

  // Load on mount
  useEffect(() => {
    loadPresentation();
  }, [loadPresentation]);

  return {
    presentation,
    isLoading,
    error,
    reload: loadPresentation
  };
}