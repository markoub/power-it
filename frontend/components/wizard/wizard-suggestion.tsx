"use client"

import { Button } from "@/components/ui/button"
import { Check, X, ArrowRight, Eye } from "lucide-react"
import { useState } from "react"
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
  const [showPreview, setShowPreview] = useState(false)
  const isSingleSlide = context === "single" && suggestion.slide
  const isAllSlides = context === "all" && suggestion.slides
  const isResearch = !!suggestion.research
  const isPresentationLevel = suggestion.presentation

  const hasChanges = () => {
    if (isSingleSlide && currentSlide) {
      const suggestedSlide = suggestion.slide
      return (
        suggestedSlide.title !== currentSlide.title ||
        suggestedSlide.content !== currentSlide.content
      )
    }
    if (isPresentationLevel) {
      return true // Presentation-level changes always have changes
    }
    return true
  }

  const getChangesSummary = () => {
    if (isSingleSlide && currentSlide) {
      const suggestedSlide = suggestion.slide
      const changes = []
      
      if (suggestedSlide.title !== currentSlide.title) {
        changes.push("title")
      }
      if (suggestedSlide.content !== currentSlide.content) {
        changes.push("content")
      }
      
      if (changes.length === 0) return "No changes detected"
      return `Updated: ${changes.join(", ")}`
    }
    if (isPresentationLevel) {
      return `Presentation modified with ${suggestion.presentation.slides.length} slides`
    }
    return "Multiple slide changes"
  }

  return (
    <div className="border border-primary-200 rounded-lg p-4 bg-primary-50" data-testid="wizard-suggestion">
      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium text-primary-700">Suggested Changes</h4>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowPreview(!showPreview)}
            className="text-primary-600 hover:text-primary-700 h-auto p-1"
            data-testid="wizard-preview-toggle"
          >
            <Eye className="h-4 w-4 mr-1" />
            {showPreview ? "Hide" : "Preview"}
          </Button>
        </div>
        <p className="text-sm text-gray-600">
          {isSingleSlide
            ? `I've created improvements for this slide. ${getChangesSummary()}`
            : isAllSlides
              ? `I've created improvements for ${suggestion.slides.length} slides.`
              : isPresentationLevel
                ? `I've modified your presentation. ${getChangesSummary()}`
                : "I've suggested some changes to your presentation."}
        </p>
      </div>

      <div className="bg-white rounded-md p-3 mb-3 text-sm max-h-60 overflow-y-auto">
        {isSingleSlide && (
          <div className="space-y-3">
            {suggestion.slide.title && suggestion.slide.title !== currentSlide?.title && (
              <div className="space-y-2">
                <span className="font-medium text-gray-700 block">Title Changes:</span>
                <div className="bg-gray-50 rounded p-2 space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-red-600 font-medium">Before:</span>
                    <span className="text-gray-600">{currentSlide?.title || "No title"}</span>
                  </div>
                  <ArrowRight className="h-3 w-3 text-gray-400 mx-auto" />
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-green-600 font-medium">After:</span>
                    <span className="text-primary-600 font-medium">{suggestion.slide.title}</span>
                  </div>
                </div>
              </div>
            )}
            
            {suggestion.slide.content && suggestion.slide.content !== currentSlide?.content && (
              <div className="space-y-2">
                <span className="font-medium text-gray-700 block">Content Changes:</span>
                <div className="bg-gray-50 rounded p-2">
                  {showPreview ? (
                    <div className="space-y-2">
                      <div>
                        <span className="text-red-600 font-medium text-xs block mb-1">Current:</span>
                        <div className="text-xs text-gray-600 bg-white p-2 rounded border-l-2 border-red-200">
                          {currentSlide?.content || "No content"}
                        </div>
                      </div>
                      <ArrowRight className="h-3 w-3 text-gray-400 mx-auto" />
                      <div>
                        <span className="text-green-600 font-medium text-xs block mb-1">Suggested:</span>
                        <div className="text-xs text-primary-600 bg-white p-2 rounded border-l-2 border-green-200">
                          <pre className="whitespace-pre-wrap font-sans">{suggestion.slide.content}</pre>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-primary-600">
                      <pre className="whitespace-pre-wrap font-sans text-xs">{suggestion.slide.content}</pre>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {suggestion.slide.imagePrompt && (
              <div className="space-y-2">
                <span className="font-medium text-gray-700 block">Image Suggestion:</span>
                <div className="bg-blue-50 rounded p-2">
                  <span className="text-blue-700 text-xs">{suggestion.slide.imagePrompt}</span>
                </div>
              </div>
            )}
          </div>
        )}

        {isAllSlides && (
          <div>
            <p className="text-gray-700 mb-2 font-medium">Changes to {suggestion.slides.length} slides:</p>
            <div className="space-y-2">
              {suggestion.slides.slice(0, 5).map((slide: Slide, index: number) => (
                <div key={index} className="bg-gray-50 rounded p-2">
                  <div className="font-medium text-primary-600 text-xs">{slide.title}</div>
                  {showPreview && slide.content && (
                    <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {typeof slide.content === 'string' ? slide.content.substring(0, 100) + '...' : ''}
                    </div>
                  )}
                </div>
              ))}
              {suggestion.slides.length > 5 && (
                <div className="text-xs text-gray-500 text-center py-1">
                  ...and {suggestion.slides.length - 5} more slides
                </div>
              )}
            </div>
          </div>
        )}
        
              <div>
        {isResearch && (
          <div>
            <p className="text-gray-700 mb-2 font-medium">Updated Research:</p>
            <div className="bg-gray-50 rounded p-2 text-sm whitespace-pre-wrap max-h-60 overflow-y-auto">
              {suggestion.research.content}
            </div>
          </div>
        )}

        {isPresentationLevel && (
          <div>
            <p className="text-gray-700 mb-2 font-medium">
              Modified presentation with {suggestion.presentation.slides.length} slides:
            </p>
            <div className="space-y-2">
              {suggestion.presentation.slides.slice(0, 5).map((slide: any, index: number) => (
                <div key={index} className="bg-gray-50 rounded p-2">
                  <div className="font-medium text-primary-600 text-xs">{slide.title}</div>
                  {showPreview && slide.content && (
                    <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {typeof slide.content === 'string'
                        ? slide.content.substring(0, 100) + '...'
                        : ''}
                    </div>
                  )}
                </div>
              ))}
              {suggestion.presentation.slides.length > 5 && (
                <div className="text-xs text-gray-500 text-center py-1">
                  …and {suggestion.presentation.slides.length - 5} more slides
                </div>
              )}
            </div>
          </div>
        )}
      </div>
        {isResearch && (
          <div>
            <p className="text-gray-700 mb-2 font-medium">Updated Research:</p>
            <div className="bg-gray-50 rounded p-2 text-sm whitespace-pre-wrap max-h-60 overflow-y-auto">
              {suggestion.research.content}
            </div>
          </div>
        )}

        {isPresentationLevel && (
          <div>
            <p className="text-gray-700 mb-2 font-medium">
              Modified presentation with {suggestion.presentation.slides.length} slides:
            </p>
            <div className="space-y-2">
              {suggestion.presentation.slides.slice(0, 5).map((slide: any, index: number) => (
                <div key={index} className="bg-gray-50 rounded p-2">
                  <div className="font-medium text-primary-600 text-xs">{slide.title}</div>
                  {showPreview && slide.content && (
                    <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                      {typeof slide.content === 'string'
                        ? slide.content.substring(0, 100) + '...'
                        : ''}
                    </div>
                  )}
                </div>
              ))}
              {suggestion.presentation.slides.length > 5 && (
                <div className="text-xs text-gray-500 text-center py-1">
                  …and {suggestion.presentation.slides.length - 5} more slides
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center">
        <div className="text-xs text-gray-500">
          {hasChanges() ? "Ready to apply" : "No changes detected"}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex items-center gap-1 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
            onClick={onDismiss}
            data-testid="wizard-dismiss-button"
          >
            <X size={14} />
            Dismiss
          </Button>
          <Button
            size="sm"
            className="bg-primary hover:bg-primary-600 text-white flex items-center gap-1 disabled:opacity-50"
            onClick={onApply}
            disabled={!hasChanges()}
            data-testid="wizard-apply-button"
          >
            <Check size={14} />
            Apply Changes
          </Button>
        </div>
      </div>
    </div>
  )
}
