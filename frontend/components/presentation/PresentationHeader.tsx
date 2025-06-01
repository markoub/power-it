import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, Save, Loader2 } from 'lucide-react';

interface PresentationHeaderProps {
  presentationName: string;
  isSaving: boolean;
  isExporting: boolean;
  onSave: () => void;
  onExport: () => void;
}

export function PresentationHeader({
  presentationName,
  isSaving,
  isExporting,
  onSave,
  onExport
}: PresentationHeaderProps) {
  return (
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
          {presentationName}
        </h1>
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={onSave}
          className="flex items-center gap-1 hover:bg-primary-50 hover:text-primary-600 transition-colors"
          disabled={isSaving}
          data-testid="save-button"
        >
          {isSaving ? (
            <span className="flex items-center gap-1">
              <Loader2 className="h-4 w-4 animate-spin" />
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
          onClick={onExport}
          className="bg-primary hover:bg-primary-600 text-white flex items-center gap-1 transition-all duration-300 shadow-md hover:shadow-primary-500/25"
          disabled={isExporting}
          data-testid="export-pptx-button"
        >
          {isExporting ? (
            <span className="flex items-center gap-1">
              <Loader2 className="h-4 w-4 animate-spin" />
              Exporting...
            </span>
          ) : (
            <>
              <Download size={18} />
              Export PPTX
            </>
          )}
        </Button>
      </div>
    </header>
  );
}