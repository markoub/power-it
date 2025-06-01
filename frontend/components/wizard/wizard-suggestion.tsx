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
      
      // Debug logging to understand the issue
      console.log('[DEBUG] hasChanges check:', {
        currentSlide: {
          title: currentSlide.title,
          content: typeof currentSlide.content === 'string' 
            ? currentSlide.content.substring(0, 100) + '...'
            : Array.isArray(currentSlide.content) 
              ? currentSlide.content.join(' ').substring(0, 100) + '...'
              : 'No content'
        },
        suggestedSlide: {
          title: suggestedSlide.title,
          content: typeof suggestedSlide.content === 'string'
            ? suggestedSlide.content.substring(0, 100) + '...'
            : Array.isArray(suggestedSlide.content)
              ? suggestedSlide.content.join(' ').substring(0, 100) + '...'
              : 'No content'
        }
      })
      
      // More robust comparison that handles formatting differences
      const titleChanged = suggestedSlide.title && suggestedSlide.title.trim() !== (currentSlide.title || '').trim()
      
      // Handle content comparison for both string and array types
      const normalizeContent = (content: string | string[] | undefined): string => {
        if (!content) return ''
        if (typeof content === 'string') return content.trim()
        if (Array.isArray(content)) return content.join(' ').trim()
        return ''
      }
      
      const contentChanged = suggestedSlide.content && 
        normalizeContent(suggestedSlide.content) !== normalizeContent(currentSlide.content)
      
      console.log('[DEBUG] hasChanges result:', { titleChanged, contentChanged, hasChanges: titleChanged || contentChanged })
      
      return titleChanged || contentChanged
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
      
      // Helper function to normalize content for comparison
      const normalizeContent = (content: string | string[] | undefined): string => {
        if (!content) return ''
        if (typeof content === 'string') return content.trim()
        if (Array.isArray(content)) return content.join(' ').trim()
        return ''
      }
      
      if (suggestedSlide.title !== currentSlide.title) {
        changes.push("title")
      }
      if (normalizeContent(suggestedSlide.content) !== normalizeContent(currentSlide.content)) {
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
    <div className="border border-primary/20 rounded-lg p-4 bg-primary/10 dark:bg-primary/20 dark:border-primary/30" data-testid="wizard-suggestion">
      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium text-primary">Suggested Changes</h4>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowPreview(!showPreview)}
            className="text-primary hover:text-primary/80 h-auto p-1"
            data-testid="wizard-preview-toggle"
          >
            <Eye className="h-4 w-4 mr-1" />
            {showPreview ? "Hide" : "Preview"}
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          {isSingleSlide
            ? `I've created improvements for this slide. ${getChangesSummary()}`
            : isAllSlides
              ? `I've created improvements for ${suggestion.slides.length} slides.`
              : isPresentationLevel
                ? `I've modified your presentation. ${getChangesSummary()}`
                : "I've suggested some changes to your presentation."}
        </p>
      </div>

      <div className="bg-background border border-border rounded-md p-3 mb-3 text-sm max-h-60 overflow-y-auto">
        {isSingleSlide && (
          <div className="space-y-3">
            {suggestion.slide.title && suggestion.slide.title !== currentSlide?.title && (
              <div className="space-y-2">
                <span className="font-medium text-foreground block">Title Changes:</span>
                <div className="bg-muted rounded p-2 space-y-1">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-red-600 font-medium">Before:</span>
                    <span className="text-muted-foreground">{currentSlide?.title || "No title"}</span>
                  </div>
                  <ArrowRight className="h-3 w-3 text-muted-foreground mx-auto" />
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-green-600 font-medium">After:</span>
                    <span className="text-primary font-medium">{suggestion.slide.title}</span>
                  </div>
                </div>
              </div>
            )}
            
            {suggestion.slide.content && suggestion.slide.content !== currentSlide?.content && (
              <div className="space-y-2">
                <span className="font-medium text-foreground block">Content Changes:</span>
                <div className="bg-muted rounded p-2">
                  {showPreview ? (
                    <div className="space-y-2">
                      <div>
                        <span className="text-red-600 font-medium text-xs block mb-1">Current:</span>
                        <div className="text-xs text-muted-foreground bg-background p-2 rounded border-l-2 border-red-200">
                          {typeof currentSlide?.content === 'string' 
                            ? currentSlide.content 
                            : Array.isArray(currentSlide?.content)
                              ? currentSlide.content.join(' ')
                              : "No content"}
                        </div>
                      </div>
                      <ArrowRight className="h-3 w-3 text-muted-foreground mx-auto" />
                      <div>
                        <span className="text-green-600 font-medium text-xs block mb-1">Suggested:</span>
                        <div className="text-xs text-primary bg-background p-2 rounded border-l-2 border-green-200">
                          <pre className="whitespace-pre-wrap font-sans">
                            {typeof suggestion.slide.content === 'string' 
                              ? suggestion.slide.content 
                              : Array.isArray(suggestion.slide.content)
                                ? suggestion.slide.content.join(' ')
                                : "No content"}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-primary">
                      <pre className="whitespace-pre-wrap font-sans text-xs">
                        {typeof suggestion.slide.content === 'string' 
                          ? suggestion.slide.content 
                          : Array.isArray(suggestion.slide.content)
                            ? suggestion.slide.content.join(' ')
                            : "No content"}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {suggestion.slide.imagePrompt && (
              <div className="space-y-2">
                <span className="font-medium text-foreground block">Image Suggestion:</span>
                <div className="bg-blue-500/10 dark:bg-blue-500/20 rounded p-2">
                  <span className="text-blue-600 dark:text-blue-400 text-xs">{suggestion.slide.imagePrompt}</span>
                </div>
              </div>
            )}
          </div>
        )}

        {isAllSlides && (
          <div>
            <p className="text-foreground mb-2 font-medium">Changes to {suggestion.slides.length} slides:</p>
            <div className="space-y-2">
              {suggestion.slides.slice(0, 5).map((slide: Slide, index: number) => (
                <div key={index} className="bg-muted rounded p-2">
                  <div className="font-medium text-primary text-xs">{slide.title}</div>
                  {showPreview && slide.content && (
                    <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {typeof slide.content === 'string' 
                        ? slide.content.substring(0, 100) + '...' 
                        : Array.isArray(slide.content)
                          ? slide.content.join(' ').substring(0, 100) + '...'
                          : ''}
                    </div>
                  )}
                </div>
              ))}
              {suggestion.slides.length > 5 && (
                <div className="text-xs text-muted-foreground text-center py-1">
                  ...and {suggestion.slides.length - 5} more slides
                </div>
              )}
            </div>
          </div>
        )}
        
        {isResearch && (
          <div>
            <p className="text-foreground mb-2 font-medium">Updated Research:</p>
            <div className="bg-muted rounded p-2 text-sm whitespace-pre-wrap max-h-60 overflow-y-auto">
              {suggestion.research.content}
            </div>
          </div>
        )}

        {isPresentationLevel && (
          <div>
            <p className="text-foreground mb-2 font-medium">
              Modified presentation with {suggestion.presentation.slides.length} slides:
            </p>
            <div className="space-y-2">
              {suggestion.presentation.slides.slice(0, 5).map((slide: any, index: number) => (
                <div key={index} className="bg-muted rounded p-2">
                  <div className="font-medium text-primary text-xs">{slide.title}</div>
                  {showPreview && slide.content && (
                    <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {typeof slide.content === 'string'
                        ? slide.content.substring(0, 100) + '...'
                        : Array.isArray(slide.content)
                          ? slide.content.join(' ').substring(0, 100) + '...'
                          : ''}
                    </div>
                  )}
                </div>
              ))}
              {suggestion.presentation.slides.length > 5 && (
                <div className="text-xs text-muted-foreground text-center py-1">
                  …and {suggestion.presentation.slides.length - 5} more slides
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center">
        <div className="text-xs text-muted-foreground">
          {hasChanges() ? "Ready to apply" : "No changes detected"}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex items-center gap-1 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-colors"
            onClick={onDismiss}
            data-testid="wizard-dismiss-button"
          >
            <X size={14} />
            Dismiss
          </Button>
          <Button
            size="sm"
            className="bg-primary hover:bg-primary/90 text-primary-foreground flex items-center gap-1 disabled:opacity-50"
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
