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
import ResearchContext from "@/components/wizard/research-context"
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



      // Use the new wizard system
      try {
        // Prepare context for the wizard
        const wizardContext: any = {
          mode: context
        };
        
        // Add slide information if in single slide mode
        if (context === "single" && currentSlide) {
          const slideIndex = presentation.slides.findIndex(s => s.id === currentSlide.id);
          wizardContext.slide_index = slideIndex;
          wizardContext.current_slide = currentSlide;
        }
        
        // Call the new wizard API
        const apiResp = await api.processWizardRequest(
          presentation.id,
          input,
          step,
          wizardContext
        );
        
        if (apiResp) {
          response = apiResp.response || "I've processed your request.";
          
          // Handle suggestions from the wizard
          if (apiResp.suggestions) {
            suggestedChanges = apiResp.suggestions;
          }
        } else {
          response = "I've processed your request, but no specific response was generated.";
        }
        
      } catch (error) {
        console.error("Error processing wizard request:", error);
        response = "I encountered an error while processing your request. Please try again.";
        setError("Failed to process wizard request. Please try again.");
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
    <Card className="h-[calc(100vh-200px)] flex flex-col bg-card/95 backdrop-blur-sm border-border">
      <CardHeader className="relative bg-gradient-to-r from-primary/20 to-secondary/20 dark:from-primary/10 dark:to-secondary/10 border-b border-border rounded-t-xl overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5" />
        <div className="absolute right-0 top-0 w-24 h-24 opacity-20 dark:opacity-10">
          <img src="/wizard.png" alt="AI Wizard" className="object-contain w-full h-full" />
        </div>
        <div className="relative z-10">
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Presentation Wizard
          </CardTitle>
          <CardDescription className="text-muted-foreground text-sm" data-testid="wizard-header">
            Context: {context === "single" && currentSlide ? `Single Slide - ${currentSlide.title}` : "All Slides"} | Step: {step}
          </CardDescription>
        </div>
      </CardHeader>
      
      {error && (
        <div className="bg-destructive/10 border-l-4 border-destructive p-3 mx-4 mt-2 rounded">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-red-400 mr-2" />
            <p className="text-sm text-destructive">{error}</p>
          </div>
        </div>
      )}
      
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Show research context when on Research step */}
        {step === "Research" && (
          <ResearchContext presentation={presentation} />
        )}
        
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
