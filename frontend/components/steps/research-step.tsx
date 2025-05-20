"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Sparkles, FileText, Loader2 } from "lucide-react"
import { motion } from "framer-motion"
import type { Presentation, PresentationStep } from "@/lib/types"
import { generatePresentationContent } from "@/lib/ai-service"

interface ResearchStepProps {
  presentation: Presentation
  setPresentation: (presentation: Presentation) => void
  savePresentation: () => void
  mode?: 'edit' | 'view'
}

export default function ResearchStep({ presentation, setPresentation, savePresentation, mode = 'edit' }: ResearchStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [manualResearch, setManualResearch] = useState("")
  const [topic, setTopic] = useState("")
  const [activeTab, setActiveTab] = useState(presentation.researchMethod || "ai")

  useEffect(() => {
    const researchStep = presentation.steps?.find(
      (step) => step.step === "research" || step.step === "manual_research"
    )

    // Set manual research content if available
    if (researchStep?.step === "manual_research" && researchStep?.result?.content) {
      setManualResearch(researchStep.result.content as string)
    }

    // Set topic from presentation data (for AI research tab)
    if (presentation.topic) {
      setTopic(presentation.topic)
    }

    // Determine active tab based on available data or preference
    if (presentation.researchMethod === "manual" && researchStep?.step === "manual_research" && researchStep?.result?.content) {
      setActiveTab("manual")
    } else if (presentation.researchMethod === "ai" && presentation.topic) {
      // If AI is the method and topic exists, prefer AI tab
      // Content for AI research is generated, not pre-filled in the same way as manual
      setActiveTab("ai")
    } else if (researchStep?.step === "manual_research" && researchStep?.result?.content) {
      // Fallback if manual research exists but wasn't the primary method
      setActiveTab("manual")
    } else {
      // Default to AI or presentation's method
      setActiveTab(presentation.researchMethod || "ai")
    }
  }, [presentation])

  const handleManualResearchChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setManualResearch(e.target.value)
    setPresentation({
      ...presentation,
      manualResearch: e.target.value,
      researchMethod: "manual",
    })
  }

  const handleTopicChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTopic(e.target.value)
    setPresentation({
      ...presentation,
      topic: e.target.value,
      researchMethod: "ai",
    })
  }

  const handleTabChange = (value: string) => {
    setActiveTab(value)
    setPresentation({
      ...presentation,
      researchMethod: value as "ai" | "manual",
    })
  }

  const handleGenerateContent = async () => {
    if (!topic.trim()) return

    setIsGenerating(true)

    try {
      // In a real app, this would call an API endpoint
      const generatedSlides = await generatePresentationContent(topic)

      setPresentation({
        ...presentation,
        slides: generatedSlides,
        researchMethod: "ai",
        topic,
      })

      savePresentation()
    } catch (error) {
      console.error("Error generating content:", error)
    } finally {
      setIsGenerating(false)
    }
  }

  // View mode component - shows research results only
  if (mode === 'view') {
    return (
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h2 className="text-2xl font-bold mb-4 gradient-text">Research</h2>
          
          {presentation.researchMethod === 'ai' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary-500" />
                  AI-Powered Research Results
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {presentation.topic && (
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Topic</label>
                    <div className="p-3 bg-gray-50 rounded-md border border-gray-200">
                      {presentation.topic}
                    </div>
                  </div>
                )}
                
                {/* Display full research content */}
                {presentation.steps?.find(step => step.step === "research")?.result?.content && (
                  <div className="space-y-2 mt-4">
                    <label className="text-sm font-medium">Research Content</label>
                    <div className="p-4 bg-white rounded-md border border-gray-200 whitespace-pre-wrap prose max-w-none">
                      {(() => {
                        const content = presentation.steps.find(step => step.step === "research")?.result?.content;
                        if (typeof content === 'string') {
                          return content;
                        } else if (typeof content === 'object') {
                          try {
                            // Try to extract the content field from JSON if it exists
                            if (content.content) {
                              return content.content;
                            } else {
                              return JSON.stringify(content, null, 2);
                            }
                          } catch (e) {
                            return JSON.stringify(content, null, 2);
                          }
                        } else {
                          return JSON.stringify(content, null, 2);
                        }
                      })()}
                    </div>
                  </div>
                )}
                
                {/* Display research links if they exist */}
                {presentation.steps?.find(step => step.step === "research")?.result?.links && (
                  <div className="space-y-2 mt-4">
                    <label className="text-sm font-medium">Research Sources</label>
                    <div className="p-4 bg-white rounded-md border border-gray-200">
                      <ul className="list-disc pl-5 space-y-1">
                        {(Array.isArray(presentation.steps.find(step => step.step === "research")?.result?.links)
                          ? presentation.steps.find(step => step.step === "research")?.result?.links
                          : []
                        ).map((link, index) => (
                          <li key={index}>
                            <a 
                              href={typeof link === 'string' ? link : link.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-primary-600 hover:underline"
                            >
                              {typeof link === 'string' ? link : link.title || link.url}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {presentation.researchMethod === 'manual' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-gray-500" />
                  Manual Research Notes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="p-3 bg-gray-50 rounded-md border border-gray-200 whitespace-pre-wrap prose max-w-none">
                    {manualResearch}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h2 className="text-2xl font-bold mb-4 gradient-text">Research</h2>
        <p className="text-gray-600 mb-6">
          Start by gathering information for your presentation. You can either use AI to generate content based on a
          topic, or enter your own research notes.
        </p>

        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
          <TabsList className="mb-6 bg-gray-100 p-1 rounded-lg">
            <TabsTrigger
              value="ai"
              className="data-[state=active]:bg-white data-[state=active]:text-primary-600 rounded-md transition-all"
            >
              <div className="flex items-center gap-2">
                <Sparkles size={16} />
                AI Research
              </div>
            </TabsTrigger>
            <TabsTrigger
              value="manual"
              className="data-[state=active]:bg-white data-[state=active]:text-primary-600 rounded-md transition-all"
            >
              <div className="flex items-center gap-2">
                <FileText size={16} />
                Manual Research
              </div>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="ai" className="animate-fade-in">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary-500" />
                  AI-Powered Research
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Topic</label>
                  <Textarea
                    value={topic}
                    onChange={handleTopicChange}
                    placeholder="Enter a topic for your presentation (e.g., 'The Future of Artificial Intelligence')"
                    rows={3}
                    className="resize-none border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                    data-testid="research-topic-input"
                  />
                </div>

                <Button
                  onClick={handleGenerateContent}
                  className="w-full bg-primary hover:bg-primary-600 text-white transition-all duration-300"
                  disabled={isGenerating || !topic.trim()}
                  data-testid="run-research-button"
                >
                  {isGenerating ? (
                    <span className="flex items-center gap-2">
                      <Loader2 size={18} className="animate-spin" />
                      Generating Content...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Sparkles size={18} />
                      Generate Presentation Content
                    </span>
                  )}
                </Button>

                {presentation.slides.length > 0 && presentation.researchMethod === "ai" && (
                  <div className="mt-4 p-4 bg-primary-50 rounded-lg border border-primary-100">
                    <p className="text-primary-700 font-medium flex items-center gap-2">
                      <CheckCircleIcon className="h-5 w-5 text-primary-500" />
                      Content generated successfully!
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {presentation.slides.length} slides have been created based on your topic.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="manual" className="animate-fade-in">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-gray-500" />
                  Manual Research
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Research Notes</label>
                  <Textarea
                    value={manualResearch}
                    onChange={handleManualResearchChange}
                    placeholder="Enter your research notes, key points, and any other information you want to include in your presentation..."
                    rows={12}
                    className="resize-none border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                    data-testid="manual-research-textarea"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  )
}

function CheckCircleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}
