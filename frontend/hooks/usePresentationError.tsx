import { ReactNode } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface UsePresentationErrorOptions {
  isLoading: boolean;
  error: string | null;
  presentation: any | null;
}

interface UsePresentationErrorReturn {
  shouldShowError: boolean;
  errorContent: ReactNode | null;
}

export function usePresentationError({
  isLoading,
  error,
  presentation
}: UsePresentationErrorOptions): UsePresentationErrorReturn {
  // Determine if we should show error state
  const shouldShowError = isLoading || error || !presentation;

  // Generate error content based on state
  let errorContent: ReactNode | null = null;

  if (isLoading) {
    errorContent = (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary-500" />
          <p className="text-gray-600 dark:text-gray-300">Loading presentation...</p>
        </div>
      </div>
    );
  } else if (error) {
    errorContent = (
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
    );
  } else if (!presentation) {
    errorContent = (
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
    );
  }

  return {
    shouldShowError,
    errorContent
  };
}