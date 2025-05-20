"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Edit, Trash2, FileIcon as FilePresentation, Sparkles, FileText, Loader2 } from "lucide-react"
import type { Presentation } from "@/lib/types"
import { motion } from "framer-motion"
import { AnimatedContainer, AnimatedItem } from "@/components/ui-elements"
import { api } from "@/lib/api"
import { toast } from "sonner"

export default function PresentationList() {
  const [presentations, setPresentations] = useState<Presentation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Load presentations from the API
    loadPresentations()
  }, [])

  const loadPresentations = async () => {
    setIsLoading(true)
    try {
      const fetchedPresentations = await api.getPresentations()
      setPresentations(fetchedPresentations)
      setError(null)
    } catch (err) {
      setError("Failed to load presentations")
      console.error("Error loading presentations:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      const success = await api.deletePresentation(id)
      if (success) {
        setPresentations(presentations.filter((presentation) => presentation.id !== id))
        toast.success("Presentation deleted successfully")
      } else {
        toast.error("Failed to delete presentation")
      }
    } catch (error) {
      console.error(`Error deleting presentation ${id}:`, error)
      toast.error("Failed to delete presentation")
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12" data-testid="presentations-loading">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
        <span className="ml-2 text-gray-600">Loading presentations...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12 bg-red-50/50 rounded-xl border border-dashed border-red-200" data-testid="presentations-error">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md mx-auto"
        >
          <h2 className="text-xl font-semibold mb-3 text-red-700">Failed to Load Presentations</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Button 
            className="bg-primary hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-full"
            onClick={loadPresentations}
            data-testid="retry-button"
          >
            Try Again
          </Button>
        </motion.div>
      </div>
    )
  }

  if (presentations.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50/50 rounded-xl border border-dashed border-gray-200" data-testid="no-presentations-message">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md mx-auto"
        >
          <FilePresentation className="h-16 w-16 mx-auto text-gray-300 mb-4" />
          <h2 className="text-2xl font-semibold mb-3 text-gray-700">No presentations yet</h2>
          <p className="text-gray-500 mb-6">Create your first presentation to get started with AI-powered slides</p>
          <Link href="/create">
            <Button 
              className="bg-primary hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-full transition-all duration-300 shadow-lg hover:shadow-primary-500/25"
              data-testid="create-presentation-button"
            >
              Create Presentation
            </Button>
          </Link>
        </motion.div>
      </div>
    )
  }

  return (
    <AnimatedContainer>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="presentations-grid">
        {presentations.map((presentation, index) => (
          <AnimatedItem key={presentation.id}>
            <Card 
              className="slide-card overflow-hidden border border-gray-100 bg-white/80 backdrop-blur-sm"
              data-testid={`presentation-card-${presentation.id}`}
            >
              <CardHeader className="pb-2 relative">
                <div className="absolute top-3 right-3">
                  {presentation.researchMethod === "ai" ? (
                    <div className="bg-primary-100 text-primary-600 text-xs px-2 py-1 rounded-full flex items-center gap-1" data-testid="research-method-ai">
                      <Sparkles size={12} />
                      AI Research
                    </div>
                  ) : (
                    <div className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full flex items-center gap-1" data-testid="research-method-manual">
                      <FileText size={12} />
                      Manual
                    </div>
                  )}
                </div>
                <CardTitle className="text-xl font-bold text-gray-800" data-testid="presentation-name">{presentation.name}</CardTitle>
                <p className="text-sm text-gray-500" data-testid="presentation-author">By {presentation.author}</p>
                <div className="hidden" data-testid="presentation-id">ID: {presentation.id}</div>
              </CardHeader>
              <CardContent>
                <div className="h-40 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-lg flex items-center justify-center mb-4 overflow-hidden group relative">
                  <img
                    src={`/placeholder.svg?height=160&width=280&query=colorful presentation slide with abstract shapes`}
                    alt="Presentation thumbnail"
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                    data-testid="presentation-thumbnail"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-4">
                    <p className="text-white text-sm font-medium" data-testid="presentation-slide-count">{presentation.slides && presentation.slides.length ? presentation.slides.length : 0} slides</p>
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  <p data-testid="presentation-created-date">Created: {typeof window !== 'undefined' && presentation.createdAt ? 
                    new Date(presentation.createdAt).toLocaleDateString() : 'N/A'}</p>
                  {presentation.topic && <p className="truncate" data-testid="presentation-topic">Topic: {presentation.topic}</p>}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Link href={`/edit/${presentation.id}`}>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-1 hover:bg-primary-50 hover:text-primary-600 transition-colors"
                    data-testid="edit-presentation-button"
                  >
                    <Edit size={16} />
                    Edit
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1 hover:bg-red-50 hover:text-red-600 transition-colors"
                  onClick={() => handleDelete(presentation.id)}
                  data-testid="delete-presentation-button"
                >
                  <Trash2 size={16} />
                  Delete
                </Button>
              </CardFooter>
            </Card>
          </AnimatedItem>
        ))}
      </div>
    </AnimatedContainer>
  )
}
