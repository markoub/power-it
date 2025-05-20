"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import type { Presentation } from "@/lib/types"
import Link from "next/link"
import { ArrowLeft, Sparkles, FileText, Loader2 } from "lucide-react"
import { motion } from "framer-motion"
import { PatternBackground, GradientHeading } from "@/components/ui-elements"
import { api } from "@/lib/api"
import { toast } from "sonner"
import ClientWrapper from "@/components/client-wrapper"

export default function CreatePage() {
  const router = useRouter()
  const [title, setTitle] = useState("")
  const [author, setAuthor] = useState("")
  const [researchMethod, setResearchMethod] = useState("ai")
  const [topic, setTopic] = useState("")
  const [manualResearch, setManualResearch] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      // Validate form
      if (!title) {
        setError('Please enter a title')
        setIsLoading(false)
        return
      }

      if (!author) {
        setError('Please enter author name')
        setIsLoading(false)
        return
      }

      if (researchMethod === 'ai' && !topic) {
        setError('Please enter a topic for AI research')
        setIsLoading(false) 
        return
      }

      if (researchMethod === 'manual' && !manualResearch) {
        setError('Please enter your manual research')
        setIsLoading(false)
        return
      }

      // Create a new presentation object
      const newPresentation = {
        name: title.trim(),
        author: author.trim(),
        researchMethod,
        topic: researchMethod === "ai" ? topic.trim() : "",
        manualResearch: researchMethod === "manual" ? manualResearch.trim() : "",
        slides: [],
      }

      console.log("Submitting presentation:", newPresentation)

      try {
        // Send to the API
        const createdPresentation = await api.createPresentation(newPresentation as any)
        
        if (!createdPresentation) {
          throw new Error("Failed to create presentation")
        }

        toast.success("Presentation created successfully")
        
        // Redirect to edit page
        router.push(`/edit/${createdPresentation.id}`)
      } catch (apiError: any) {
        console.error("API Error:", apiError)
        
        // Handle API-specific errors
        if (apiError.message && apiError.message.includes("UNIQUE constraint failed")) {
          setError(`A presentation with this title already exists. Please choose a different title.`)
        } else if (apiError.message && apiError.message.includes("detail")) {
          // Try to parse the error message as JSON
          try {
            const errorDetails = JSON.parse(apiError.message.substring(apiError.message.indexOf('{')));
            setError(errorDetails.detail || String(apiError))
          } catch {
            setError(String(apiError))
          }
        } else {
          setError(apiError.message || "Failed to create presentation. Please try again.")
        }
        
        toast.error("Failed to create presentation")
      }
    } catch (err) {
      console.error("Error creating presentation:", err)
      setError(err instanceof Error ? err.message : "Failed to create presentation")
      toast.error("Failed to create presentation")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ClientWrapper fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-10 w-10 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
      </div>
    }>
      <div className="min-h-screen relative" data-testid="create-page">
        <PatternBackground pattern="diagonal" />

        <div className="container mx-auto px-4 py-8">
          <Link href="/" className="inline-block mb-6">
            <Button variant="outline" size="sm" className="flex items-center gap-1" data-testid="back-button">
              <ArrowLeft size={16} />
              Back to Home
            </Button>
          </Link>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <GradientHeading className="mb-6" data-testid="page-title">Create New Presentation</GradientHeading>

            <Card className="max-w-2xl mx-auto bg-white/90 backdrop-blur-sm border border-gray-100 shadow-xl">
              <CardHeader>
                <CardTitle className="text-2xl">Presentation Details</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6" data-testid="create-presentation-form">
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                        Presentation Title
                      </label>
                      <input
                        type="text"
                        id="title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter presentation title"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        data-testid="presentation-title-input"
                      />
                    </div>

                    <div>
                      <label htmlFor="author" className="block text-sm font-medium text-gray-700">
                        Author
                      </label>
                      <input
                        type="text"
                        id="author"
                        value={author}
                        onChange={(e) => setAuthor(e.target.value)}
                        placeholder="Your name"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        data-testid="presentation-author-input"
                      />
                    </div>

                    {/* Error message display */}
                    {error && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-600" data-testid="error-message">
                        {error}
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Research Method
                      </label>
                      <RadioGroup
                        value={researchMethod}
                        onValueChange={setResearchMethod}
                        className="flex flex-col space-y-3"
                        data-testid="research-method-group"
                      >
                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          className={`flex items-center space-x-3 p-4 rounded-lg border ${
                            researchMethod === "ai" ? "border-primary-300 bg-primary-50" : "border-gray-200 bg-white"
                          }`}
                          data-testid="ai-research-option"
                        >
                          <RadioGroupItem value="ai" id="ai" className="text-primary" />
                          <div className="flex-1">
                            <Label htmlFor="ai" className="flex items-center gap-2 cursor-pointer">
                              <Sparkles size={18} className="text-primary-500" />
                              <span className="font-medium">AI Research</span>
                            </Label>
                            <p className="text-sm text-gray-500 mt-1">Let AI generate content based on your topic</p>
                          </div>
                        </motion.div>

                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          className={`flex items-center space-x-3 p-4 rounded-lg border ${
                            researchMethod === "manual" ? "border-primary-300 bg-primary-50" : "border-gray-200 bg-white"
                          }`}
                          data-testid="manual-research-option"
                        >
                          <RadioGroupItem value="manual" id="manual" className="text-primary" />
                          <div className="flex-1">
                            <Label htmlFor="manual" className="flex items-center gap-2 cursor-pointer">
                              <FileText size={18} className="text-gray-500" />
                              <span className="font-medium">Manual Research</span>
                            </Label>
                            <p className="text-sm text-gray-500 mt-1">Enter your own research and content</p>
                          </div>
                        </motion.div>
                      </RadioGroup>
                    </div>

                    {researchMethod === "ai" ? (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="space-y-2"
                        data-testid="ai-topic-container"
                      >
                        <Label htmlFor="topic" className="text-gray-700">
                          Research Topic
                        </Label>
                        <Input
                          id="topic"
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          placeholder="Enter topic for AI research"
                          required={researchMethod === "ai"}
                          className="border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                          data-testid="ai-topic-input"
                        />
                        <p className="text-sm text-gray-500 flex items-center gap-1">
                          <Sparkles size={14} className="text-primary-500" />
                          AI will generate presentation content based on this topic
                        </p>
                      </motion.div>
                    ) : (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="space-y-2"
                        data-testid="manual-research-container"
                      >
                        <Label htmlFor="manualResearch" className="text-gray-700">
                          Research Notes
                        </Label>
                        <Textarea
                          id="manualResearch"
                          value={manualResearch}
                          onChange={(e) => setManualResearch(e.target.value)}
                          placeholder="Enter your research notes or content for the presentation"
                          rows={6}
                          required={researchMethod === "manual"}
                          className="border-gray-200 focus:border-primary-300 focus:ring focus:ring-primary-200 transition-all"
                          data-testid="manual-research-input"
                        />
                      </motion.div>
                    )}
                  </div>

                  <div className="flex justify-end">
                    <Button 
                      type="submit" 
                      className="bg-primary hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-full transition-all duration-300 shadow-lg hover:shadow-primary-500/25"
                      disabled={isLoading}
                      data-testid="submit-presentation-button"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 size={20} className="animate-spin mr-2" />
                          Creating...
                        </>
                      ) : (
                        "Create Presentation"
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </ClientWrapper>
  )
}
