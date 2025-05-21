"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, Send } from "lucide-react"
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

export default function Wizard({ presentation, currentSlide, context, step, onApplyChanges }: WizardProps) {
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content: `Welcome to the AI Presentation Wizard! I'm here to help you create an amazing presentation. You're currently on the ${step} step. ${
        context === "single" && currentSlide
          ? `I see you're working on a slide titled "${currentSlide.title}". How can I help with this slide?`
          : "How can I help with your presentation?"
      }`,
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [suggestion, setSuggestion] = useState<any | null>(null)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: "user" as const, content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      let response = ""
      let suggestedChanges = null as any

      if (context === "single" && currentSlide && step === "Slides") {
        const slideIndex = presentation.slides.findIndex(s => s.id === currentSlide.id)
        const apiResp = await api.modifyPresentation(presentation.id, input, slideIndex, "slides")
        const mod = apiResp.modified_slide
        response = "Here are some improvements for the slide.";
        if (mod && mod.fields) {
          suggestedChanges = {
            slide: {
              ...currentSlide,
              title: mod.fields.title || currentSlide.title,
              content: Array.isArray(mod.fields.content) ? mod.fields.content.join("\n") : (mod.fields.content || currentSlide.content)
            }
          }
        }
      } else {
        response = "Wizard support for this step is coming soon.";
      }

      setMessages((prev) => [...prev, { role: "assistant", content: response }])

      if (suggestedChanges) {
        setSuggestion(suggestedChanges)
      }
    } catch (error) {
      console.error("Error sending message:", error)
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again." },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const applySuggestion = () => {
    if (suggestion) {
      onApplyChanges(suggestion)
      setSuggestion(null)
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Great! I've applied the changes to your presentation." },
      ])
    }
  }

  const dismissSuggestion = () => {
    setSuggestion(null)
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "No problem. Let me know if you need any other assistance." },
    ])
  }

  // Helper functions to generate responses
  const generateSlideResponse = (slide: Slide, query: string) => {
    if (query.toLowerCase().includes("improve") || query.toLowerCase().includes("better")) {
      return `I've analyzed your slide "${slide.title}" and have some suggestions to make it more engaging. Would you like me to enhance the title and content?`
    } else if (query.toLowerCase().includes("example") || query.toLowerCase().includes("sample")) {
      return `Here's an example of how you could structure this slide:\n\n**Title: ${slide.title}**\n\n- Key point 1: Important information about the topic\n- Key point 2: Supporting evidence or examples\n- Key point 3: Conclusion or takeaway\n\nWould you like me to apply a structure like this to your slide?`
    } else {
      return `I can help improve your slide "${slide.title}". I suggest making the title more engaging and structuring the content with clear bullet points for better readability. Would you like me to suggest specific improvements?`
    }
  }

  const generateIllustrationResponse = (slide: Slide, query: string) => {
    return `For your slide "${slide.title}", I recommend an image that visually represents the key concepts. I can suggest a better image prompt that will generate a more relevant illustration. Would you like me to create a better prompt?`
  }

  const enhanceSlideContent = (content: string) => {
    if (!content.trim()) {
      return "• This is an important point about the topic\n• Here's supporting evidence or an example\n• This is a conclusion or key takeaway"
    }

    // Add bullet points if there aren't any
    if (!content.includes("•") && !content.includes("-")) {
      return content
        .split("\n")
        .filter((line) => line.trim())
        .map((line) => `• ${line}`)
        .join("\n")
    }

    return content
  }

  const generateBetterImagePrompt = (slide: Slide) => {
    return `Professional illustration for presentation slide about ${slide.title}. Modern, clean design with abstract elements representing ${slide.content
      .split(" ")
      .slice(0, 10)
      .join(" ")}...`
  }

  return (
    <Card className="h-[calc(100vh-200px)] flex flex-col bg-white/90 backdrop-blur-sm">
      <CardHeader className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-t-xl">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          AI Presentation Wizard
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <WizardMessage role={message.role} content={message.content} />
            </motion.div>
          ))}

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center space-x-2 text-gray-500"
            >
              <div className="flex space-x-1">
                <div className="h-2 w-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div
                  className="h-2 w-2 bg-primary-400 rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="h-2 w-2 bg-primary-400 rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
              <span className="text-sm">AI is thinking...</span>
            </motion.div>
          )}

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
      </CardContent>
      <CardFooter className="border-t p-4">
        <div className="flex w-full gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI wizard for help..."
            className="min-h-[60px] resize-none"
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
          >
            <Send size={18} />
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}
