"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { Presentation } from "@/lib/types"
import Link from "next/link"
import { ArrowLeft, Loader2, PlusCircle } from "lucide-react"
import { motion } from "framer-motion"
import { PatternBackground, GradientHeading } from "@/components/ui-elements"
import { api } from "@/lib/api"
import { toast } from "sonner"
import ClientWrapper from "@/components/client-wrapper"

export default function CreatePage() {
  const router = useRouter()
  const [title, setTitle] = useState("")
  const [author, setAuthor] = useState("")
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

      // Create a new presentation object with minimal data
      const newPresentation = {
        name: title.trim(),
        author: author.trim(),
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
                <CardTitle className="text-2xl flex items-center gap-2">
                  <PlusCircle className="h-6 w-6 text-primary-500" />
                  Presentation Details
                </CardTitle>
                <p className="text-gray-600">
                  Get started by giving your presentation a name and adding your details.
                  You'll choose your research method on the next step.
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6" data-testid="create-presentation-form">
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="title" className="text-sm font-medium text-gray-700">
                        Presentation Title *
                      </Label>
                      <Input
                        type="text"
                        id="title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter a descriptive title for your presentation"
                        className="mt-1"
                        data-testid="presentation-title-input"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="author" className="text-sm font-medium text-gray-700">
                        Author *
                      </Label>
                      <Input
                        type="text"
                        id="author"
                        value={author}
                        onChange={(e) => setAuthor(e.target.value)}
                        placeholder="Your name or organization"
                        className="mt-1"
                        data-testid="presentation-author-input"
                        required
                      />
                    </div>

                    {/* Error message display */}
                    {error && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="p-3 bg-red-50 border border-red-200 rounded-lg"
                        data-testid="error-message"
                      >
                        <p className="text-red-600 text-sm">{error}</p>
                      </motion.div>
                    )}
                  </div>

                  <div className="flex justify-end pt-4">
                    <Button 
                      type="submit" 
                      className="bg-primary hover:bg-primary-600 text-white font-medium px-8 py-2 rounded-full transition-all duration-300 shadow-lg hover:shadow-primary-500/25 flex items-center gap-2"
                      disabled={isLoading}
                      data-testid="submit-presentation-button"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 size={20} className="animate-spin" />
                          Creating...
                        </>
                      ) : (
                        <>
                          <PlusCircle size={20} />
                          Create Presentation
                        </>
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
