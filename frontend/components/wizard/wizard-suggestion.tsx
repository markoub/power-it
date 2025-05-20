"use client"

import { Button } from "@/components/ui/button"
import { Check, X } from "lucide-react"
import type { Slide } from "@/lib/types"

interface WizardSuggestionProps {
  suggestion: any
  context: "all" | "single"
  currentSlide: Slide | null
  onApply: () => void
  onDismiss: () => void
}

export default function WizardSuggestion({
  suggestion,
  context,
  currentSlide,
  onApply,
  onDismiss,
}: WizardSuggestionProps) {
  const isSingleSlide = context === "single" && suggestion.slide
  const isAllSlides = context === "all" && suggestion.slides

  return (
    <div className="border border-primary-200 rounded-lg p-4 bg-primary-50">
      <div className="mb-3">
        <h4 className="font-medium text-primary-700 mb-1">Suggested Changes</h4>
        <p className="text-sm text-gray-600">
          {isSingleSlide
            ? "I've created some improvements for this slide."
            : isAllSlides
              ? "I've created improvements for all your slides."
              : "I've suggested some changes to your presentation."}
        </p>
      </div>

      <div className="bg-white rounded-md p-3 mb-3 text-sm max-h-40 overflow-y-auto">
        {isSingleSlide && (
          <div>
            {suggestion.slide.title && (
              <div className="mb-2">
                <span className="font-medium text-gray-700">Title:</span>{" "}
                <span className="text-primary-600">{suggestion.slide.title}</span>
              </div>
            )}
            {suggestion.slide.content && (
              <div className="mb-2">
                <span className="font-medium text-gray-700">Content:</span>
                <pre className="mt-1 whitespace-pre-wrap text-primary-600 font-sans">{suggestion.slide.content}</pre>
              </div>
            )}
            {suggestion.slide.imagePrompt && (
              <div>
                <span className="font-medium text-gray-700">Image Prompt:</span>{" "}
                <span className="text-primary-600">{suggestion.slide.imagePrompt}</span>
              </div>
            )}
          </div>
        )}

        {isAllSlides && (
          <div>
            <p className="text-gray-700 mb-2">Changes to {suggestion.slides.length} slides:</p>
            <ul className="list-disc pl-5 space-y-1">
              {suggestion.slides.slice(0, 3).map((slide: Slide, index: number) => (
                <li key={index} className="text-primary-600">
                  {slide.title}
                </li>
              ))}
              {suggestion.slides.length > 3 && <li className="text-gray-500">...and more</li>}
            </ul>
          </div>
        )}
      </div>

      <div className="flex justify-end gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex items-center gap-1 hover:bg-red-50 hover:text-red-600 transition-colors"
          onClick={onDismiss}
        >
          <X size={14} />
          Dismiss
        </Button>
        <Button
          size="sm"
          className="bg-primary hover:bg-primary-600 text-white flex items-center gap-1"
          onClick={onApply}
        >
          <Check size={14} />
          Apply Changes
        </Button>
      </div>
    </div>
  )
}
