"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Download, Save, Loader2 } from "lucide-react"
import type { Presentation, Slide } from "@/lib/types"
import Link from "next/link"
import { PatternBackground } from "@/components/ui-elements"
import { toast } from "@/components/ui/use-toast"
import { ToastAction } from "@/components/ui/toast"
import WorkflowSteps from "@/components/workflow-steps"
import ResearchStep from "@/components/steps/research-step"
import SlidesStep from "@/components/steps/slides-step"
import IllustrationStep from "@/components/steps/illustration-step"
import CompiledStep from "@/components/steps/compiled-step"
import PptxStep from "@/components/steps/pptx-step"
import Wizard from "@/components/wizard/wizard"
import { api } from "@/lib/api"
import { v4 as uuidv4 } from "uuid"
import ClientWrapper from "@/components/client-wrapper"
import { use } from "react"

export default function EditPage({ params }: { params: { id: string } }) {
  // Properly unwrap params to get the id
  const unwrappedParams = use(params);
  const router = useRouter()
  const [presentation, setPresentation] = useState<Presentation | null>(null)
  const [currentSlide, setCurrentSlide] = useState<Slide | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [wizardContext, setWizardContext] = useState<"all" | "single">("all")
  const [isProcessingStep, setIsProcessingStep] = useState(false)

  const steps = ["Research", "Slides", "Illustration", "Compiled", "PPTX"]
  const stepApiNames = ["research", "slides", "images", "compiled", "pptx"]

  useEffect(() => {
    // Load presentation from API
    fetchPresentation();
  }, [unwrappedParams.id]);

  // Get the highest step that is completed + 1 (if not the last step)
  const determineCurrentStep = (presentationData: any) => {
    if (!presentationData.steps || !Array.isArray(presentationData.steps)) {
      return 0; // Default to first step if no steps data
    }
    
    let highestCompletedStep = -1;
    for (let i = 0; i < stepApiNames.length; i++) {
      const stepName = stepApiNames[i];
      const step = presentationData.steps.find((s: any) => s.step === stepName);
      
      if (step && step.status === 'completed') {
        highestCompletedStep = i;
      } else {
        // Found first incomplete step
        break;
      }
    }
    
    // If nothing is completed, start with step 0
    if (highestCompletedStep === -1) return 0;
    
    // Otherwise, go to the next uncompleted step (or stay at the last step)
    return Math.min(highestCompletedStep + 1, steps.length - 1);
  };

  const fetchPresentation = async () => {
    setIsLoading(true);
    try {
      const fetchedPresentation = await api.getPresentation(unwrappedParams.id);
      if (fetchedPresentation) {
        setPresentation(fetchedPresentation);
        
        // Determine the current step based on completion status
        const newCurrentStep = determineCurrentStep(fetchedPresentation);
        setCurrentStep(newCurrentStep);
        
        if (fetchedPresentation.slides && fetchedPresentation.slides.length > 0) {
          setCurrentSlide(fetchedPresentation.slides[0]);
        }
        setError(null);
      } else {
        setError("Presentation not found");
        setTimeout(() => router.push("/"), 3000);
      }
    } catch (err) {
      console.error("Error fetching presentation:", err);
      setError("Failed to load presentation");
    } finally {
      setIsLoading(false);
    }
  };

  const savePresentation = async () => {
    if (!presentation) return;

    setIsSaving(true);
    try {
      const updatedPresentation = await api.updatePresentation(presentation.id, presentation);
      
      if (updatedPresentation) {
        setPresentation(updatedPresentation);
        
        toast({
          title: "Changes saved",
          description: "Your presentation has been updated successfully.",
          action: <ToastAction altText="OK">OK</ToastAction>,
        });
      } else {
        throw new Error("Failed to update presentation");
      }
    } catch (error) {
      console.error("Error saving presentation:", error);
      toast({
        title: "Error",
        description: "Failed to save changes. Please try again.",
        variant: "destructive",
        action: <ToastAction altText="Try again">Try again</ToastAction>,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const addNewSlide = () => {
    if (!presentation) return

    const newSlide: Slide = {
      id: uuidv4(),
      title: "New Slide",
      content: "",
      order: presentation.slides.length,
      imagePrompt: "",
      imageUrl: "",
    }

    const updatedPresentation = {
      ...presentation,
      slides: [...presentation.slides, newSlide],
    }

    setPresentation(updatedPresentation)
    setCurrentSlide(newSlide)
    savePresentation()
  }

  const updateSlide = (updatedSlide: Slide) => {
    if (!presentation) return

    const updatedSlides = presentation.slides.map((slide) => (slide.id === updatedSlide.id ? updatedSlide : slide))

    setPresentation({
      ...presentation,
      slides: updatedSlides,
    })
    setCurrentSlide(updatedSlide)
  }

  const deleteSlide = (slideId: string) => {
    if (!presentation) return

    const updatedSlides = presentation.slides
      .filter((slide) => slide.id !== slideId)
      .map((slide, index) => ({ ...slide, order: index }))

    const updatedPresentation = {
      ...presentation,
      slides: updatedSlides,
    }

    setPresentation(updatedPresentation)

    if (currentSlide?.id === slideId) {
      setCurrentSlide(updatedSlides.length > 0 ? updatedSlides[0] : null)
    }

    savePresentation()
  }

  const handleExport = async () => {
    if (!presentation) return;

    toast({
      title: "PPTX Generation Started",
      description: "Your presentation is being generated on the server...",
    });

    try {
      // Assuming your backend endpoint for PPTX generation is '/api/generate-pptx-backend'
      // This needs to be an endpoint on your Python backend, not a Next.js API route.
      // Adjust the URL as per your actual backend API structure.
      const response = await fetch("http://localhost:8000/api/v1/presentations/generate-pptx", { // Example backend URL
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(presentation),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          // If parsing JSON fails, use text
          errorData = { message: await response.text() || "Unknown error" };
        }
        throw new Error(
          `Failed to generate PPTX: ${response.status} ${response.statusText} - ${errorData?.detail || errorData?.message || 'Server error'}`
        );
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      // Use presentation name for filename, default to 'presentation.pptx'
      const fileName = presentation.name ? `${presentation.name.replace(/[^a-z0-9_-\s\.]/gi, '_')}.pptx` : "presentation.pptx";
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: "Presentation Exported",
        description: "Your PPTX file has been downloaded successfully.",
        action: <ToastAction altText="OK">OK</ToastAction>,
      });
    } catch (error) {
      console.error("Error during PPTX export:", error);
      toast({
        title: "Export Error",
        description: error instanceof Error ? error.message : "Failed to export PPTX. See console for details.",
        variant: "destructive",
        action: <ToastAction altText="OK">OK</ToastAction>,
      });
    }
  };

  const handleWizardContextChange = (context: "all" | "single") => {
    setWizardContext(context)
  }

  const applyWizardChanges = async (changes: any) => {
    if (!presentation) return

    if (wizardContext === "single" && currentSlide) {
      // Apply changes to current slide
      const updatedSlide = { ...currentSlide, ...changes.slide }
      updateSlide(updatedSlide)
    } else if (wizardContext === "all") {
      // Apply changes to all slides or presentation
      if (changes.slides) {
        setPresentation({
          ...presentation,
          slides: changes.slides,
        })
      }
      if (changes.presentation) {
        setPresentation({
          ...presentation,
          ...changes.presentation,
        })
      }
    }

    await savePresentation()

    toast({
      title: "Changes applied",
      description: "The suggested changes have been applied to your presentation.",
      action: <ToastAction altText="OK">OK</ToastAction>,
    })
  }

  // Check if a step is completed based on backend data
  const isStepCompleted = (stepIndex: number) => {
    if (!presentation || !presentation.steps) return false;
    
    const stepName = stepApiNames[stepIndex];
    const step = presentation.steps.find(s => s.step === stepName);
    
    return step?.status === 'completed';
  };

  // Continue to next step function
  const handleContinueToNextStep = async () => {
    if (!presentation) return;
    
    try {
      setIsProcessingStep(true);
      
      // Get the API step name for the next uncompleted step
      let nextStepIndex = -1;
      for (let i = 0; i < stepApiNames.length; i++) {
        if (!isStepCompleted(i)) {
          nextStepIndex = i;
          break;
        }
      }
      
      if (nextStepIndex === -1) {
        console.log('All steps are already completed');
        setIsProcessingStep(false);
        return;
      }
      
      const nextStepName = stepApiNames[nextStepIndex];
      
      // Call the API to run the next step
      const result = await api.runPresentationStep(presentation.id, nextStepName);
      
      if (result) {
        toast({
          title: "Step initiated",
          description: `Starting ${steps[nextStepIndex]} generation process...`,
        });
        
        // Wait a bit for the step to be processed
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Refresh the presentation to get updated step status
        await fetchPresentation();
        
        // Move to the next step
        setCurrentStep(nextStepIndex);
      } else {
        throw new Error("Failed to start the next step");
      }
    } catch (error) {
      console.error("Error continuing to next step:", error);
      toast({
        title: "Error",
        description: "Failed to continue to the next step. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessingStep(false);
    }
  };

  // Determine if continue button should be shown
  const shouldShowContinueButton = () => {
    if (!presentation || !presentation.steps) return false;
    
    // Find if there are any incomplete steps
    for (let i = 0; i < stepApiNames.length; i++) {
      if (!isStepCompleted(i)) {
        // If the step before this one is completed, we show the continue button
        return i > 0 && isStepCompleted(i - 1);
      }
    }
    
    return false; // All steps completed or no steps found
  };

  // Handle direct step navigation
  const handleStepChange = (stepIndex: number) => {
    // We can always navigate to current step
    if (stepIndex === currentStep) return;
    
    // Allow navigation to completed steps
    if (isStepCompleted(stepIndex)) {
      setCurrentStep(stepIndex);
      return;
    }
    
    // Allow navigation to the first uncompleted step (next step after completed ones)
    if (stepIndex > 0 && isStepCompleted(stepIndex - 1)) {
      setCurrentStep(stepIndex);
      return;
    }
    
    // Otherwise, show error message
    toast({
      title: "Step unavailable",
      description: "You need to complete previous steps first.",
      variant: "destructive",
    });
  };

  return (
    <ClientWrapper fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
          <p className="text-gray-600">Loading presentation...</p>
        </div>
      </div>
    }>
      {isLoading ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-10 w-10 animate-spin text-primary-500" />
            <p className="text-gray-600">Loading presentation...</p>
          </div>
        </div>
      ) : error ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center p-8 bg-red-50 rounded-xl border border-red-200 max-w-md">
            <h2 className="text-xl font-semibold text-red-600 mb-4">{error}</h2>
            <p className="text-gray-600 mb-6">Redirecting to home page...</p>
            <Link href="/">
              <Button className="bg-primary hover:bg-primary-600 text-white">
                Go to Home
              </Button>
            </Link>
          </div>
        </div>
      ) : !presentation ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center p-8 bg-red-50 rounded-xl border border-red-200 max-w-md">
            <h2 className="text-xl font-semibold text-red-600 mb-4">Presentation not found</h2>
            <p className="text-gray-600 mb-6">Unable to load the requested presentation.</p>
            <Link href="/">
              <Button className="bg-primary hover:bg-primary-600 text-white">
                Go to Home
              </Button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="min-h-screen relative">
          <PatternBackground pattern="grid" />

          <div className="container mx-auto p-4">
            <header className="flex justify-between items-center mb-6 bg-white/80 backdrop-blur-sm p-4 rounded-xl shadow-sm border border-gray-100">
              <div className="flex items-center gap-4">
                <Link href="/">
                  <Button
                    variant="outline"
                    size="icon"
                    className="rounded-full hover:bg-primary-50 hover:text-primary-600 transition-colors"
                  >
                    <ArrowLeft size={18} />
                  </Button>
                </Link>
                <h1 className="text-2xl font-bold gradient-text">{presentation.name}</h1>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={savePresentation}
                  className="flex items-center gap-1 hover:bg-primary-50 hover:text-primary-600 transition-colors"
                  disabled={isSaving}
                  data-testid="save-button"
                >
                  {isSaving ? (
                    <span className="flex items-center gap-1">
                      <div className="h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                      Saving...
                    </span>
                  ) : (
                    <>
                      <Save size={18} />
                      Save
                    </>
                  )}
                </Button>
                <Button
                  onClick={handleExport}
                  className="bg-primary hover:bg-primary-600 text-white flex items-center gap-1 transition-all duration-300 shadow-md hover:shadow-primary-500/25"
                  data-testid="export-pptx-button"
                >
                  <Download size={18} />
                  Export PPTX
                </Button>
              </div>
            </header>

            <WorkflowSteps 
              steps={steps} 
              currentStep={currentStep} 
              onChange={handleStepChange} 
              onContinue={shouldShowContinueButton() ? handleContinueToNextStep : undefined}
              isProcessing={isProcessingStep}
              completedSteps={presentation?.steps ? stepApiNames.map((name, index) => 
                isStepCompleted(index)
              ) : []}
            />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
              {/* Wizard Sidebar */}
              <div className="lg:col-span-1">
                <Wizard
                  presentation={presentation}
                  currentSlide={currentSlide}
                  context={wizardContext}
                  step={steps[currentStep]}
                  onApplyChanges={applyWizardChanges}
                />
              </div>

              {/* Main Content Area */}
              <div className="lg:col-span-3">
                <div className="bg-white/80 backdrop-blur-sm p-6 rounded-xl shadow-sm border border-gray-100">
                  {currentStep === 0 && (
                    <ResearchStep
                      presentation={presentation}
                      setPresentation={setPresentation}
                      savePresentation={savePresentation}
                      mode="view"
                    />
                  )}
                  {currentStep === 1 && (
                    <SlidesStep
                      presentation={presentation}
                      currentSlide={currentSlide}
                      setCurrentSlide={setCurrentSlide}
                      updateSlide={updateSlide}
                      addNewSlide={addNewSlide}
                      deleteSlide={deleteSlide}
                      onContextChange={handleWizardContextChange}
                    />
                  )}
                  {currentStep === 2 && (
                    <IllustrationStep
                      presentation={presentation}
                      currentSlide={currentSlide}
                      setCurrentSlide={setCurrentSlide}
                      updateSlide={updateSlide}
                      onContextChange={handleWizardContextChange}
                    />
                  )}
                  {currentStep === 3 && (
                    <CompiledStep
                      presentation={presentation}
                      currentSlide={currentSlide}
                      setCurrentSlide={setCurrentSlide}
                      onContextChange={handleWizardContextChange}
                    />
                  )}
                  {currentStep === 4 && <PptxStep presentation={presentation} />}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </ClientWrapper>
  )
}
