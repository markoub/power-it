import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

interface PresentationHeaderProps {
  presentationName: string;
}

export function PresentationHeader({
  presentationName
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
    </header>
  );
}