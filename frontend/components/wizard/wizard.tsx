"use client"

import { useState, useEffect, useRef, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Sparkles, Send, AlertCircle, CheckCircle, Clock } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Presentation, Slide } from "@/lib/types"
import WizardMessage from "@/components/wizard/wizard-message"
import WizardSuggestion from "@/components/wizard/wizard-suggestion"
import { api } from "@/lib/api"

interface WizardProps {
  presentation: Presentation
  currentSlide: Slide | null
  context: "all" | "single"
  step: string
  onApplyChanges: (changes: any) => void
}

type MessageStatus = "sending" | "success" | "error" | "processing"

interface Message {
  role: "user" | "assistant"
  content: string
  status?: MessageStatus
  timestamp?: Date
}

export default function Wizard({ presentation, currentSlide, context, step, onApplyChanges }: WizardProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [suggestion, setSuggestion] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Memoize currentSlide properties to prevent unnecessary re-renders
  const currentSlideId = useMemo(() => currentSlide?.id, [currentSlide?.id])
  const currentSlideTitle = useMemo(() => currentSlide?.title, [currentSlide?.title])

  // Update welcome message when step, context, or currentSlide changes
  useEffect(() => {
    const getWelcomeMessage = () => {
      const baseMessage = "Welcome to the AI Presentation Wizard! I'm here to help you create an amazing presentation."
      
      if (step === "Research") {
        return `${baseMessage} You're currently on the Research step. I can help you understand research topics and methods, but slide modifications are available once you generate slides.`
      } else if (step === "Slides") {
        if (context === "single" && currentSlide) {
          return `${baseMessage} You're working on the slide titled "${currentSlide.title}". I can help you improve the title, content, and structure of this specific slide.`
        } else {
          return `${baseMessage} You're on the Slides step. Select a slide to get specific help, or ask me general questions about slide creation.`
        }
      } else if (step === "Illustrations") {
        return `${baseMessage} You're on the Illustrations step. I can help with image suggestions and visual improvements for your slides.`
      } else if (step === "PPTX") {
        return `${baseMessage} Your presentation is being finalized. If you need to make changes, please go back to the Slides step.`
      } else {
        return `${baseMessage} You're currently on the ${step} step. How can I help you today?`
      }
    }

    const welcomeMessage: Message = {
      role: "assistant",
      content: getWelcomeMessage(),
      status: "success",
      timestamp: new Date()
    }
    
    setMessages([welcomeMessage])
    setError(null)
  }, [step, context, currentSlideId, currentSlideTitle])

  const updateMessageStatus = (messageIndex: number, status: MessageStatus) => {
    setMessages(prev => prev.map((msg, idx) => 
      idx === messageIndex ? { ...msg, status } : msg
    ))
  }

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = { 
      role: "user", 
      content: input,
      status: "sending",
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    const userMessageIndex = messages.length
    setInput("")
    setIsLoading(true)
    setError(null)

    // Update user message status to success
    setTimeout(() => updateMessageStatus(userMessageIndex, "success"), 500)

    try {
      let response = ""
      let suggestedChanges = null as any

      // Add processing message
      const processingMessage: Message = {
        role: "assistant",
        content: "Processing your request...",
        status: "processing",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, processingMessage])
      const processingMessageIndex = userMessageIndex + 1

      // Check if this is a presentation-level modification (add/remove slides)
      const isPresentationLevelModification = (prompt: string) => {
        const lowerPrompt = prompt.toLowerCase();
        return lowerPrompt.includes('add') && (lowerPrompt.includes('slide') || lowerPrompt.includes('slides')) ||
               lowerPrompt.includes('remove') && (lowerPrompt.includes('slide') || lowerPrompt.includes('slides')) ||
               lowerPrompt.includes('delete') && (lowerPrompt.includes('slide') || lowerPrompt.includes('slides')) ||
               lowerPrompt.includes('new slide') ||
               lowerPrompt.includes('another slide') ||
               lowerPrompt.includes('more slide') ||
               lowerPrompt.includes('extra slide');
      };

      // Only allow slide modifications if we're on the slides step and have slides data
      if (step === "Slides") {
        // Check if slides are actually available before attempting modification
        const hasSlidesData = presentation.slides && presentation.slides.length > 0;
        const slidesStep = presentation.steps?.find(s => s.step === "slides");
        const isSlidesCompleted = slidesStep?.status === "completed";
        
        if (!hasSlidesData || !isSlidesCompleted) {
          response = "I can't modify slides yet because they haven't been generated. Please generate slides first by going to the Slides step.";
        } else {
          try {
            // Determine if this is a presentation-level or single-slide modification
            const isFullPresentationModification = isPresentationLevelModification(input);
            
            if (isFullPresentationModification) {
              // Handle presentation-level modifications (add/remove slides)
              console.log("Handling presentation-level modification:", input);
              
              const apiResp = await api.modifyPresentation(presentation.id, input, undefined, "slides");
              
              if (apiResp && apiResp.modified_presentation) {
                response = "I've analyzed your request and created modifications to the presentation. You can preview the changes below and choose to apply or dismiss them.";
                
                // Transform the modified presentation data to match frontend expectations
                const modifiedSlides = apiResp.modified_presentation.slides?.map((slide: any, index: number) => {
                  const fields = slide.fields || {};
                  const title = fields.title || `Slide ${index + 1}`;
                  let content: any = fields.content || "";

                  if (Array.isArray(content)) {
                    content = content.join("\n");
                  } else if (typeof content !== "string") {
                    content = String(content || "");
                  }

                  return {
                    id: slide.id || `slide-${index}`,
                    type: slide.type || "Content",
                    fields,
                    title,
                    content,
                    order: index,
                    imagePrompt: "",
                    imageUrl: slide.image_url || "",
                  };
                }) || [];

                suggestedChanges = {
                  presentation: {
                    ...presentation,
                    slides: modifiedSlides
                  }
                };
              } else {
                response = "I've processed your request, but no specific changes were suggested. You could try a more specific request about what slides to add or remove.";
              }
            } else if (context === "single" && currentSlide) {
              // Handle single slide modifications
              const slideIndex = presentation.slides.findIndex(s => s.id === currentSlide.id);
              
              if (slideIndex === -1) {
                response = "I couldn't find the selected slide. Please try selecting a different slide.";
              } else {
                const apiResp = await api.modifyPresentation(presentation.id, input, slideIndex, "slides");
                const mod = apiResp.modified_slide;
                
                if (mod && mod.fields) {
                  response = "I've analyzed your slide and created some improvements. You can preview the changes below and choose to apply or dismiss them.";
                  suggestedChanges = {
                    slide: {
                      ...currentSlide,
                      title: mod.fields.title || currentSlide.title,
                      content: Array.isArray(mod.fields.content) ? mod.fields.content.join("\n") : (mod.fields.content || currentSlide.content)
                    }
                  };
                } else {
                  response = "I've processed your request, but no specific changes were suggested. The slide might already be well-optimized, or you could try a more specific request.";
                }
              }
            } else {
              // Context is "all" but not a presentation-level modification
              response = "I can help with general questions about your presentation. For specific slide modifications, please select a slide first. For adding or removing slides, try requests like 'add a slide about...' or 'remove the slide about...'.";
            }
          } catch (error) {
            console.error("Error modifying presentation/slide:", error);
            response = "I encountered an error while trying to process your request. This might be because the presentation data isn't ready yet. Please try again after ensuring all previous steps are completed.";
            setError("Failed to process modification. Please try again.");
          }
        }
      } else if (step === "Research") {
        try {
          const apiResp = await api.modifyResearch(presentation.id, input);
          if (apiResp && apiResp.content) {
            response = "I've prepared updated research content. You can apply the changes below.";
            suggestedChanges = { research: apiResp };
          } else {
            response = "I've processed your request, but no specific changes were suggested.";
          }
        } catch (error) {
          console.error("Error modifying research:", error);
          response = "I encountered an error while trying to modify the research.";
          setError("Failed to process research modification. Please try again.");
        }
      } else if (step === "Illustrations") {
        response = "I can help with image suggestions and visual improvements. For slide content changes, please use the Slides step.";
      } else if (step === "PPTX") {
        response = "The presentation is being finalized. If you need to make changes, please go back to the Slides step.";
      } else {
        response = "I'm here to help! Wizard support varies by step. For the best experience with slide modifications, please navigate to the Slides step and select a specific slide.";
      }

      // Update processing message with actual response
      setMessages(prev => prev.map((msg, idx) => 
        idx === processingMessageIndex 
          ? { ...msg, content: response, status: "success" }
          : msg
      ))

      if (suggestedChanges) {
        setSuggestion(suggestedChanges)
      }
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage = "Sorry, I encountered an error processing your request. Please try again."
      
      setMessages(prev => prev.map((msg, idx) => 
        idx === prev.length - 1 
          ? { ...msg, content: errorMessage, status: "error" }
          : msg
      ))
      setError("Failed to send message. Please check your connection and try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const applySuggestion = () => {
    if (suggestion) {
      onApplyChanges(suggestion)
      setSuggestion(null)

      const successMessage: Message = {
        role: "assistant",
        content: step === "Research"
          ? "Great! The research has been updated with the suggested changes."
          : suggestion.presentation
            ? "Perfect! I've successfully applied the changes to your presentation. The modifications should now be visible in the slide editor."
            : "Perfect! I've successfully applied the changes to your slide. The improvements should now be visible in the slide editor.",
        status: "success",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, successMessage])
    }
  }


  const dismissSuggestion = () => {
    setSuggestion(null)
    
    const dismissMessage: Message = {
      role: "assistant", 
      content: "No problem! The suggestions have been dismissed. Feel free to ask for different improvements or try a more specific request.",
      status: "success",
      timestamp: new Date()
    }
    setMessages(prev => [...prev, dismissMessage])
  }

  const getStatusIcon = (status?: MessageStatus) => {
    switch (status) {
      case "sending":
        return <Clock className="h-3 w-3 text-yellow-500 animate-pulse" />
      case "success":
        return <CheckCircle className="h-3 w-3 text-green-500" />
      case "error":
        return <AlertCircle className="h-3 w-3 text-red-500" />
      case "processing":
        return <Clock className="h-3 w-3 text-blue-500 animate-spin" />
      default:
        return null
    }
  }

  return (
    <Card className="h-[calc(100vh-200px)] flex flex-col bg-white/90 backdrop-blur-sm">
      <CardHeader className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-t-xl">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          AI Presentation Wizard
        </CardTitle>
        <CardDescription className="text-white/90 text-sm" data-testid="wizard-header">
          Context: {context === "single" && currentSlide ? `Single Slide - ${currentSlide.title}` : "All Slides"} | Step: {step}
        </CardDescription>
      </CardHeader>
      
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-3 mx-4 mt-2 rounded">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-400 mr-2" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}
      
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-start gap-2"
            >
              <div className="flex-1">
                <WizardMessage role={message.role} content={message.content} />
              </div>
              <div className="mt-2">
                {getStatusIcon(message.status)}
              </div>
            </motion.div>
          ))}

          {suggestion && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <WizardSuggestion
                suggestion={suggestion}
                context={context}
                currentSlide={currentSlide}
                onApply={applySuggestion}
                onDismiss={dismissSuggestion}
              />
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </CardContent>
      
      <CardFooter className="border-t p-4">
        <div className="flex w-full gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI wizard for help..."
            className="min-h-[60px] resize-none"
            data-testid="wizard-input"
            disabled={isLoading}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
          />
          <Button
            className="bg-primary hover:bg-primary-600 text-white"
            size="icon"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            data-testid="wizard-send-button"
          >
            {isLoading ? (
              <Clock className="h-4 w-4 animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}
