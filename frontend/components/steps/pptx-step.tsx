"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { RefreshCw, Download, ExternalLink, Play } from "lucide-react"
import type { Presentation } from "@/lib/types"
import PptxPreview from "../pptx-preview"
import { api } from "@/lib/api"

interface PptxStepProps {
  presentation: Presentation
  refreshPresentation?: () => Promise<Presentation | null>
}

export default function PptxStep({ presentation, refreshPresentation }: PptxStepProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const [slideCount, setSlideCount] = useState<number | null>(null)

  // Check if PPTX step is completed
  const pptxStep = presentation.steps?.find(step => step.step === 'pptx')
  const isPptxCompleted = pptxStep?.status === 'completed'
  const isProcessing = pptxStep?.status === 'processing'

  const generatePptx = async () => {
    setIsGenerating(true)
    try {
      await api.runPresentationStep(presentation.id, "pptx")
      // Wait a moment to let the backend process start
      await new Promise(resolve => setTimeout(resolve, 2000))
      // Update the refresh key to force the preview to reload
      setRefreshKey(prev => prev + 1)
      
      // Refresh main presentation data to update step status
      if (refreshPresentation) {
        await refreshPresentation()
      }
    } catch (error) {
      console.error("Error generating PPTX:", error)
    } finally {
      setIsGenerating(false)
    }
  }

  const regeneratePptx = async () => {
    setIsRegenerating(true)
    try {
      await api.runPresentationStep(presentation.id, "pptx")
      // Wait a moment to let the backend process start
      await new Promise(resolve => setTimeout(resolve, 2000))
      // Update the refresh key to force the preview to reload
      setRefreshKey(prev => prev + 1)
      
      // Refresh main presentation data to update step status
      if (refreshPresentation) {
        await refreshPresentation()
      }
    } catch (error) {
      console.error("Error regenerating PPTX:", error)
    } finally {
      setIsRegenerating(false)
    }
  }

  const updateSlideCount = (count: number) => {
    setSlideCount(count)
  }

  const downloadPptx = () => {
    // Create a direct download link to bypass any frontend processing
    const downloadUrl = `http://localhost:8000/presentations/${presentation.id}/download-pptx`
    window.open(downloadUrl, "_blank")
  }

  // Link to debug compiled step
  const viewCompiledStep = () => {
    // Open the compiled step in a new tab for debugging
    const apiUrl = `http://localhost:8000/presentations/${presentation.id}`
    window.open(apiUrl, "_blank")
  }

  // Show generate button if PPTX hasn't been generated yet
  if (!isPptxCompleted && !isProcessing) {
    return (
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold gradient-text">Generate PPTX</h2>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={viewCompiledStep}
                data-testid="view-compiled-step-button"
              >
                <ExternalLink size={16} className="mr-2" />
                View API Data
              </Button>
            </div>
          </div>
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <p className="text-muted-foreground mb-6">
              Ready to generate your PowerPoint presentation from the compiled slides and images.
            </p>
            <Button 
              onClick={generatePptx}
              disabled={isGenerating}
              className="bg-primary hover:bg-primary-600 text-white flex items-center gap-2"
              data-testid="run-pptx-button"
            >
              {isGenerating ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  Generating PPTX...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Generate PPTX
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    )
  }

  // Show processing state
  if (isProcessing) {
    return (
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold gradient-text">Generating PPTX</h2>
          </div>
          <div className="text-center py-12 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <div className="flex items-center justify-center gap-2 text-primary-600">
              <RefreshCw size={24} className="animate-spin" />
              <p className="text-lg font-medium">Generating your PowerPoint presentation...</p>
            </div>
            <p className="text-gray-500 mt-2">This may take a few moments.</p>
          </div>
        </motion.div>
      </div>
    )
  }

  // Show completed PPTX with preview
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold gradient-text">Presentation Ready</h2>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={viewCompiledStep}
              data-testid="view-compiled-step-button"
            >
              <ExternalLink size={16} className="mr-2" />
              View API Data
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={downloadPptx}
              data-testid="download-pptx-button"
            >
              <Download size={16} className="mr-2" />
              Direct Download
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={regeneratePptx}
              disabled={isRegenerating}
              data-testid="regenerate-pptx-button"
            >
              <RefreshCw size={16} className={`mr-2 ${isRegenerating ? 'animate-spin' : ''}`} />
              {isRegenerating ? "Regenerating..." : "Regenerate PPTX"}
            </Button>
          </div>
        </div>
        <p className="text-muted-foreground mb-6">
          Your presentation, "{presentation.name}", is structured and ready. You can export it as a PowerPoint file using the "Export PPTX" button in the header.
          {slideCount !== null && <span className="font-medium"> (Preview shows {slideCount} slides)</span>}
        </p>
      </motion.div>
      <PptxPreview presentation={presentation} key={refreshKey} onSlidesLoaded={updateSlideCount} />
    </div>
  )
}
