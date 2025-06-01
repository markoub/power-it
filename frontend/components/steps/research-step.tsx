"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Sparkles, FileText, Loader2, RefreshCw, Search, BookOpen, ExternalLink } from "lucide-react"
import { motion } from "framer-motion"
import ReactMarkdown from 'react-markdown'
import type { Presentation, PresentationStep } from "@/lib/types"
import { api } from "@/lib/api"
import { toast } from "@/hooks/use-toast"

interface ResearchStepProps {
  presentation: Presentation
  setPresentation: (presentation: Presentation) => void
  savePresentation: () => Promise<void>
  mode?: 'edit' | 'manual'
  onEditResearch?: () => void
  refreshPresentation?: () => Promise<Presentation | null>
}

export default function ResearchStep({ presentation, setPresentation, savePresentation, mode = 'edit', onEditResearch, refreshPresentation }: ResearchStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isRedoing, setIsRedoing] = useState(false)
  
  // Check if research step is currently processing
  const researchStep = presentation.steps?.find(step => step.step === 'research' || step.step === 'manual_research');
  const isStepProcessing = researchStep?.status === 'processing';
  const [manualResearch, setManualResearch] = useState("")
  const [topic, setTopic] = useState("")
  const [researchMethod, setResearchMethod] = useState<"ai" | "manual">("ai")
  const [hasSelectedMethod, setHasSelectedMethod] = useState(false)

  // Check if any research has been completed
  const hasCompletedResearch = presentation.steps?.some(
    (step) => (step.step === "research" || step.step === "manual_research") && step.status === "completed"
  )

  // Check if there's an existing research step (even if not completed)
  const existingResearchStep = presentation.steps?.find(
    (step) => step.step === "research" || step.step === "manual_research"
  )

  useEffect(() => {
    // Set manual research content if available
    const manualResearchStep = presentation.steps?.find(
      (step) => step.step === "manual_research"
    )
    if (manualResearchStep?.result?.content) {
      setManualResearch(manualResearchStep.result.content as string)
      setResearchMethod("manual")
      setHasSelectedMethod(true)
    }

    // Set topic from presentation data (for AI research)
    if (presentation.topic) {
      setTopic(presentation.topic)
      setResearchMethod("ai")
      setHasSelectedMethod(true)
    }

    // If there's an existing research step, we consider method as selected
    if (existingResearchStep) {
      setHasSelectedMethod(true)
      if (existingResearchStep.step === "manual_research") {
        setResearchMethod("manual")
      } else {
        setResearchMethod("ai")
      }
    }
  }, [presentation, existingResearchStep])

  const handleMethodSelection = (method: "ai" | "manual") => {
    setResearchMethod(method)
    setHasSelectedMethod(true)
    setPresentation({
      ...presentation,
      researchMethod: method,
    })
  }

  const handleManualResearchChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setManualResearch(e.target.value)
  }

  const handleTopicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTopic(e.target.value)
  }

  const handleStartManualResearch = async () => {
    if (!manualResearch.trim()) {
      toast({
        title: "Error",
        description: "Please enter your research content.",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)

    try {
      // Call the API to run the manual research step directly
      const presentationId = typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id
      const result = await api.runPresentationStep(presentationId, 'manual_research', {
        research_content: manualResearch.trim()
      })
      
      console.log('Manual research API result:', result)
      
      // Update presentation with manual research in local state
      setPresentation({
        ...presentation,
        manualResearch: manualResearch.trim(),
        researchMethod: "manual",
      })
      
      toast({
        title: "Manual research started",
        description: "Your research content is being saved...",
      })
      
      // Poll until the manual research is ready (similar to AI research)
      let researchReady = false
      let attempts = 0
      const maxAttempts = 10 // Shorter polling for manual research
      
      while (!researchReady && attempts < maxAttempts) {
        attempts++
        
        // Wait 1 second between polls (shorter for manual research)
        await new Promise((resolve) => setTimeout(resolve, 1000))
        
        // Fetch the updated presentation
        const updatedPresentation = await api.getPresentation(presentationId)
        console.log(`Manual research poll attempt ${attempts}:`, updatedPresentation?.steps?.find(s => s.step === 'manual_research'))
        
        if (updatedPresentation) {
          // Check if manual research step is completed
          const manualResearchStep = updatedPresentation.steps?.find(
            (step) => step.step === "manual_research" && step.status === "completed"
          )
          
          if (manualResearchStep && manualResearchStep.result?.content) {
            researchReady = true
            
            // Update presentation with the new data
            setPresentation(updatedPresentation)
            
            // Refresh main presentation data to update step status
            if (refreshPresentation) {
              await refreshPresentation()
            }
            
            toast({
              title: "Manual research saved",
              description: "Your research content has been saved successfully.",
            })
          }
        }
      }
      
      if (!researchReady) {
        // Even if polling failed, try one final refresh
        const finalPresentation = await api.getPresentation(presentationId)
        if (finalPresentation) {
          setPresentation(finalPresentation)
        }
        
        toast({
          title: "Research saved",
          description: "Your research content has been saved. If it doesn't appear, please refresh the page.",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error saving manual research:", error)
      toast({
        title: "Error",
        description: "Failed to save research content. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleGenerateContent = async () => {
    if (!topic.trim()) {
      toast({
        title: "Error",
        description: "Please enter a topic for AI research.",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)

    try {
      // Update presentation with topic first in frontend state
      setPresentation({
        ...presentation,
        topic: topic.trim(),
        researchMethod: "ai",
      })
      
      // Save presentation to ensure topic is stored in backend
      await savePresentation()
      
      // Then call the API to run the research step and pass the topic directly
      const presentationId = typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id
      const result = await api.runPresentationStep(presentationId, 'research', {
        topic: topic.trim()
      })
      
      toast({
        title: "Research started",
        description: "Your research is being processed. This may take a minute...",
      })
      
      // Poll until the research is ready
      let researchReady = false
      let attempts = 0
      const maxAttempts = 20 // Limit polling attempts
      
      while (!researchReady && attempts < maxAttempts) {
        attempts++
        
        // Wait 2 seconds between polls
        await new Promise((resolve) => setTimeout(resolve, 2000))
        
        // Fetch the updated presentation
        const updatedPresentation = await api.getPresentation(presentationId)
        
        if (updatedPresentation) {
          // Check if research step is completed
          const researchStep = updatedPresentation.steps?.find(
            (step) => step.step === "research" && step.status === "completed"
          )
          
          if (researchStep) {
            researchReady = true
            
            // Update presentation with the new data
            setPresentation(updatedPresentation)
            
            // Refresh main presentation data to update step status
            if (refreshPresentation) {
              await refreshPresentation()
            }
            
            toast({
              title: "Research completed",
              description: "Research has been completed successfully.",
            })
          }
        }
      }
      
      if (!researchReady) {
        toast({
          title: "Taking longer than expected",
          description: "Research is still in progress. Please wait or refresh the page in a minute.",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error generating content:", error)
      toast({
        title: "Error",
        description: "Failed to generate research content. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRedoResearch = async () => {
    if (!topic.trim()) return
    
    setIsRedoing(true)
    
    try {
      // Get presentation ID
      const presentationId = typeof presentation.id === 'number' ? presentation.id.toString() : presentation.id
      
      // Call the new topic update endpoint directly
      // This will update the topic and trigger research regeneration in one step
      const updatedPresentation = await api.updatePresentationTopic(presentationId, {
        topic: topic.trim()
      })
      
      // Update frontend state with the result from the update call
      if (updatedPresentation) {
        setPresentation({
          ...presentation,
          ...updatedPresentation,
          topic: topic.trim(),
          researchMethod: "ai",
        })
      }
      
      toast({
        title: "Topic updated",
        description: "Your presentation topic is being updated and new research is being generated...",
      })
      
      // Poll until the research is ready
      let researchReady = false
      let attempts = 0
      const maxAttempts = 20
      
      while (!researchReady && attempts < maxAttempts) {
        attempts++
        
        await new Promise((resolve) => setTimeout(resolve, 2000))
        
        const updatedPresentation = await api.getPresentation(presentationId)
        
        if (updatedPresentation) {
          const researchStep = updatedPresentation.steps?.find(
            (step) => step.step === "research" && step.status === "completed"
          )
          
          if (researchStep) {
            researchReady = true
            setPresentation(updatedPresentation)
            
            // Refresh main presentation data to update step status
            if (refreshPresentation) {
              await refreshPresentation()
            }
            
            toast({
              title: "Research updated",
              description: "New research has been completed successfully.",
            })
          }
        }
      }
      
      if (!researchReady) {
        toast({
          title: "Taking longer than expected",
          description: "Research update is still in progress. Please wait or refresh the page in a minute.",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error redoing research:", error)
      toast({
        title: "Error",
        description: "Failed to update research. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsRedoing(false)
    }
  }

  // Get the research content to display
  const getResearchContent = () => {
    if (researchMethod === "manual") {
      const manualStep = presentation.steps?.find(step => step.step === "manual_research")
      return {
        content: manualStep?.result?.content as string || "",
        links: manualStep?.result?.links || []
      }
    } else {
      const researchStep = presentation.steps?.find(step => step.step === "research")
      return {
        content: researchStep?.result?.content as string || "",
        links: researchStep?.result?.links || []
      }
    }
  }

  const researchData = getResearchContent()
  const researchContent = researchData.content
  const researchLinks = researchData.links

  // Show processing state if research is being generated
  if (isStepProcessing) {
    return (
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold mb-4 gradient-text">Generating Research</h2>
          <p className="text-muted-foreground mb-6">
            AI is researching your topic and gathering comprehensive information.
          </p>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="flex items-center justify-center gap-3 text-primary-600 mb-4">
              <Loader2 size={32} className="animate-spin" />
              <h3 className="text-xl font-semibold">Researching...</h3>
            </div>
            <p className="text-muted-foreground mb-4">
              This process may take a minute as we gather and analyze information on your topic.
            </p>
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-500">
              The AI is searching for relevant information, analyzing sources, and structuring the research content for your presentation.
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // If no method has been selected yet, show the selection interface
  if (!hasSelectedMethod) {
    return (
      <Card className="max-w-4xl mx-auto" data-testid="research-method-selection">
        <CardHeader>
          <CardTitle className="text-2xl font-bold flex items-center gap-2" data-testid="research-method-title">
            <Search className="h-6 w-6 text-primary-500" />
            Choose Research Method
          </CardTitle>
          <p className="text-muted-foreground" data-testid="research-method-description">
            Select how you'd like to research content for your presentation.
          </p>
        </CardHeader>
        <CardContent>
          <RadioGroup
            value={researchMethod}
            onValueChange={(value) => setResearchMethod(value as "ai" | "manual")}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
            data-testid="research-method-radio-group"
          >
            <motion.div
              whileHover={{ scale: 1.02 }}
              className={`p-6 rounded-lg border cursor-pointer transition-all ${
                researchMethod === "ai" ? "border-primary-300 bg-primary-50" : "border-gray-200 bg-white"
              }`}
              onClick={() => setResearchMethod("ai")}
              data-testid="ai-research-option"
            >
              <div className="flex items-start space-x-3">
                <RadioGroupItem value="ai" id="ai" className="text-primary mt-1" data-testid="ai-research-radio" />
                <div className="flex-1">
                  <Label htmlFor="ai" className="flex items-center gap-2 cursor-pointer text-lg font-medium" data-testid="ai-research-label">
                    <Sparkles size={20} className="text-primary-500" />
                    AI Research
                  </Label>
                  <p className="text-sm text-muted-foreground mt-2" data-testid="ai-research-description">
                    Let AI generate comprehensive research content based on your topic. Perfect for exploring new subjects or getting structured insights.
                  </p>
                  <div className="mt-3 text-xs text-gray-500" data-testid="ai-research-features">
                    ✓ Comprehensive content generation<br/>
                    ✓ Structured research format<br/>
                    ✓ Time-saving approach
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className={`p-6 rounded-lg border cursor-pointer transition-all ${
                researchMethod === "manual" ? "border-primary-300 bg-primary-50" : "border-gray-200 bg-white"
              }`}
              onClick={() => setResearchMethod("manual")}
              data-testid="manual-research-option"
            >
              <div className="flex items-start space-x-3">
                <RadioGroupItem value="manual" id="manual" className="text-primary mt-1" data-testid="manual-research-radio" />
                <div className="flex-1">
                  <Label htmlFor="manual" className="flex items-center gap-2 cursor-pointer text-lg font-medium" data-testid="manual-research-label">
                    <BookOpen size={20} className="text-muted-foreground" />
                    Manual Research
                  </Label>
                  <p className="text-sm text-muted-foreground mt-2" data-testid="manual-research-description">
                    Enter your own research content, data, or prepared material. Ideal when you have specific information or expertise to include.
                  </p>
                  <div className="mt-3 text-xs text-gray-500" data-testid="manual-research-features">
                    ✓ Full control over content<br/>
                    ✓ Use existing research<br/>
                    ✓ Custom data and insights
                  </div>
                </div>
              </div>
            </motion.div>
          </RadioGroup>

          <div className="flex justify-center mt-6">
            <Button
              onClick={() => handleMethodSelection(researchMethod)}
              className="bg-primary hover:bg-primary-600 text-white px-8 py-2 rounded-full flex items-center gap-2"
              data-testid="continue-with-method-button"
            >
              Continue with {researchMethod === "ai" ? "AI Research" : "Manual Research"}
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Show the selected research method interface
  return (
    <div className="space-y-6" data-testid="research-method-interface">
      {/* Method indicator and option to change */}
      <Card data-testid="research-method-indicator">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3" data-testid="selected-method-display">
              {researchMethod === "ai" ? (
                <Sparkles className="h-5 w-5 text-primary-500" />
              ) : (
                <BookOpen className="h-5 w-5 text-muted-foreground" />
              )}
              <span className="font-medium" data-testid="selected-method-text">
                {researchMethod === "ai" ? "AI Research" : "Manual Research"} Selected
              </span>
            </div>
            {!hasCompletedResearch && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setHasSelectedMethod(false)}
                data-testid="change-method-button"
              >
                Change Method
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* AI Research Interface */}
      {researchMethod === "ai" && (
        <Card data-testid="ai-research-interface">
          <CardHeader>
            <CardTitle className="flex items-center gap-2" data-testid="ai-research-interface-title">
              <Sparkles className="h-5 w-5 text-primary-500" />
              AI Research
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="topic" className="text-sm font-medium" data-testid="topic-input-label">
                Research Topic *
              </Label>
              <Input
                id="topic"
                value={topic}
                onChange={handleTopicChange}
                placeholder="Enter the main topic for your presentation"
                className="mt-1"
                disabled={isGenerating || isRedoing}
                data-testid="topic-input"
              />
              <p className="text-xs text-gray-500 mt-1" data-testid="topic-input-help">
                Be specific about what you want to research (e.g., "Machine Learning in Healthcare", "Digital Marketing Strategies 2024")
              </p>
            </div>

            <div className="flex gap-2">
              {!hasCompletedResearch ? (
                <Button
                  onClick={handleGenerateContent}
                  disabled={isGenerating || !topic.trim()}
                  className="bg-primary hover:bg-primary-600 text-white flex items-center gap-2"
                  data-testid="start-ai-research-button"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Generating Research...
                    </>
                  ) : (
                    <>
                      <Sparkles size={16} />
                      Start AI Research
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  onClick={handleRedoResearch}
                  disabled={isRedoing || !topic.trim()}
                  variant="outline"
                  className="flex items-center gap-2"
                  data-testid="update-research-button"
                >
                  {isRedoing ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Updating Research...
                    </>
                  ) : (
                    <>
                      <RefreshCw size={16} />
                      Update Research
                    </>
                  )}
                </Button>
              )}
            </div>

            {/* Display research results */}
            {researchContent && (
              <div className="mt-6" data-testid="ai-research-content-display">
                <Label className="text-sm font-medium mb-2 block" data-testid="ai-research-content-label">Generated Research Content</Label>
                <div className="bg-gray-50 border rounded-lg p-4 max-h-96 overflow-y-auto" data-testid="ai-research-content">
                  <div className="prose prose-sm text-gray-700 max-w-none">
                    <ReactMarkdown>{researchContent}</ReactMarkdown>
                  </div>
                </div>
                
                {/* Display research links if available */}
                {researchLinks && researchLinks.length > 0 && (
                  <div className="mt-4" data-testid="ai-research-links-display">
                    <Label className="text-sm font-medium mb-2 block" data-testid="ai-research-links-label">Research Sources</Label>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <ul className="space-y-2" data-testid="ai-research-links">
                        {researchLinks.map((link: any, index: number) => (
                          <li key={index} className="flex items-center gap-2">
                            <ExternalLink className="h-3 w-3 text-blue-600 flex-shrink-0" />
                            <a
                              href={link.href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-800 underline"
                              data-testid={`research-link-${index}`}
                            >
                              {link.title || link.href}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Manual Research Interface */}
      {researchMethod === "manual" && (
        <Card data-testid="manual-research-interface">
          <CardHeader>
            <CardTitle className="flex items-center gap-2" data-testid="manual-research-interface-title">
              <BookOpen className="h-5 w-5 text-muted-foreground" />
              Manual Research
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="manual-research" className="text-sm font-medium" data-testid="manual-research-input-label">
                Research Content *
              </Label>
              <Textarea
                id="manual-research"
                value={manualResearch}
                onChange={handleManualResearchChange}
                placeholder="Enter your research notes, data, or prepared content for the presentation..."
                rows={12}
                className="mt-1"
                disabled={isGenerating}
                data-testid="manual-research-input"
              />
              <p className="text-xs text-gray-500 mt-1" data-testid="manual-research-input-help">
                Include all the information you want to use in your presentation. This can be research notes, data points, existing content, or any material you've prepared.
              </p>
            </div>

            <Button
              onClick={handleStartManualResearch}
              disabled={isGenerating || !manualResearch.trim()}
              className="bg-primary hover:bg-primary-600 text-white flex items-center gap-2"
              data-testid="save-manual-research-button"
            >
              {isGenerating ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Saving Research...
                </>
              ) : (
                <>
                  <FileText size={16} />
                  Save Research Content
                </>
              )}
            </Button>

            {/* Display saved research content */}
            {researchContent && (
              <div className="mt-6" data-testid="manual-research-content-display">
                <Label className="text-sm font-medium mb-2 block" data-testid="manual-research-content-label">Saved Research Content</Label>
                <div className="bg-gray-50 border rounded-lg p-4 max-h-96 overflow-y-auto" data-testid="manual-research-content">
                  <div className="prose prose-sm text-gray-700 max-w-none">
                    <ReactMarkdown>{researchContent}</ReactMarkdown>
                  </div>
                </div>
                
                {/* Display research links if available */}
                {researchLinks && researchLinks.length > 0 && (
                  <div className="mt-4" data-testid="manual-research-links-display">
                    <Label className="text-sm font-medium mb-2 block" data-testid="manual-research-links-label">Research Sources</Label>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <ul className="space-y-2" data-testid="manual-research-links">
                        {researchLinks.map((link: any, index: number) => (
                          <li key={index} className="flex items-center gap-2">
                            <ExternalLink className="h-3 w-3 text-blue-600 flex-shrink-0" />
                            <a
                              href={link.href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-800 underline"
                              data-testid={`manual-research-link-${index}`}
                            >
                              {link.title || link.href}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
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
      <polyline points="22,4 12,14.01 9,11.01" />
    </svg>
  )
}
