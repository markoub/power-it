"use client"

import { motion } from "framer-motion"
import { CheckCircle2, ArrowRight, Loader2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import RerunButton from "@/components/ui/rerun-button"

interface WorkflowStepsProps {
  steps: string[]
  currentStep: number
  onChange: (step: number) => void
  onContinue?: () => Promise<void>
  isProcessing?: boolean
  completedSteps?: boolean[] // Array of booleans indicating which steps are completed
  pendingSteps?: boolean[] // Array of booleans indicating which steps are pending
  processSteps?: boolean[] // Array of booleans indicating which steps are processing
  failedSteps?: boolean[] // Array of booleans indicating which steps have failed
  presentationId?: string | number // Add presentation ID for rerun functionality
  onRerunStep?: (stepIndex: number) => Promise<void> // Callback for rerunning steps
}

export default function WorkflowSteps({ 
  steps, 
  currentStep, 
  onChange, 
  onContinue,
  isProcessing = false,
  completedSteps = [],
  pendingSteps = [],
  processSteps = [],
  failedSteps = [],
  presentationId,
  onRerunStep
}: WorkflowStepsProps) {
  
  // Map step index to API step name
  const getStepApiName = (index: number): string => {
    const stepApiNames = ["research", "slides", "images", "compiled", "pptx"];
    return stepApiNames[index] || "unknown";
  }
  
  // Function to check if a step is enabled for navigation
  const isStepEnabled = (index: number) => {
    // If we have completion data from the backend, use that
    if (completedSteps && completedSteps.length > 0) {
      // Always allow current step
      if (index === currentStep) return true;
      
      // Allow any completed step
      if (index < completedSteps.length && completedSteps[index]) return true;
      
      // Allow next step after a completed step (this is the "available" step)
      if (index > 0 && index - 1 < completedSteps.length && completedSteps[index - 1]) return true;
    } else {
      // Fallback to basic navigation: only allow current or previous steps,
      // or next step if there's no Continue button functionality
      return index <= currentStep || (index === currentStep + 1 && !onContinue);
    }
    
    return false;
  }
  
  // Check if a step is completed
  const isStepCompleted = (index: number) => {
    // If we have explicit completion data, use it
    if (completedSteps && completedSteps.length > index) {
      return completedSteps[index];
    }
    
    // Otherwise, fallback to assuming all previous steps are completed
    return index < currentStep;
  }

  // Check if a step is pending (waiting, greyed out)
  const isStepPending = (index: number) => {
    if (pendingSteps && pendingSteps.length > index) {
      return pendingSteps[index];
    }
    return false;
  }

  // Check if a step is processing (yellow with spinner)
  const isStepProcessing = (index: number) => {
    if (processSteps && processSteps.length > index) {
      return processSteps[index];
    }
    return false;
  }

  // Check if a step has failed (red)
  const isStepFailed = (index: number) => {
    if (failedSteps && failedSteps.length > index) {
      return failedSteps[index];
    }
    return false;
  }

  // Check if a step is the next available step (blue)
  const isStepAvailable = (index: number) => {
    // A step is available if it's not completed, not processing, not failed, 
    // and the previous step is completed
    if (isStepCompleted(index) || isStepProcessing(index) || isStepFailed(index)) {
      return false;
    }
    
    // First step is available if it's pending
    if (index === 0) {
      return isStepPending(index);
    }
    
    // Other steps are available if the previous step is completed
    return index > 0 && isStepCompleted(index - 1) && isStepPending(index);
  }

  // Check if any step is currently processing (to hide arrows)
  const hasAnyProcessingStep = processSteps && processSteps.some(isProcessing => isProcessing);
  
  // Find the last completed step that isn't the last step of the workflow
  const findLastActionableCompletedStep = () => {
    if (!completedSteps || completedSteps.length === 0) {
      return currentStep < steps.length - 1 ? currentStep : -1;
    }
    
    for (let i = 0; i < steps.length - 1; i++) {
      // Find a completed step where the next one is not completed
      if (completedSteps[i] && (i + 1 >= completedSteps.length || !completedSteps[i + 1])) {
        return i;
      }
    }
    
    return -1;
  }
  
  // Handle click on step button
  const handleStepClick = (index: number) => {
    console.log(`🔄 WorkflowSteps: Step click attempted for index ${index}`);
    console.log(`🔍 WorkflowSteps: isStepEnabled(${index}) = ${isStepEnabled(index)}`);
    
    if (isStepEnabled(index)) {
      console.log(`✅ WorkflowSteps: Calling onChange(${index})`);
      onChange(index);
    } else {
      console.log(`❌ WorkflowSteps: Step ${index} is not enabled, click ignored`);
    }
  }
  
  // The step after which we should show the continue button
  const continueButtonStep = findLastActionableCompletedStep();

  // Get step styling based on status
  const getStepStyling = (index: number) => {
    if (isStepCompleted(index)) {
      return index === currentStep
        ? "bg-green-500 text-white ring-4 ring-green-100" // Completed + current
        : "bg-green-500 text-white"; // Just completed (green)
    } else if (isStepProcessing(index)) {
      return "bg-yellow-500 text-white"; // Processing: yellow with spinner
    } else if (isStepFailed(index)) {
      return "bg-red-500 text-white"; // Failed: red
    } else if (isStepAvailable(index)) {
      return "bg-blue-500 text-white"; // Available: blue
    } else if (isStepPending(index)) {
      return "bg-muted text-muted-foreground"; // Pending: grey
    } else if (index === currentStep) {
      return "bg-blue-500 text-white ring-4 ring-blue-100"; // Current step (blue)
    } else if (isStepEnabled(index)) {
      return "bg-muted text-muted-foreground hover:bg-muted/80"; // Enabled
    } else {
      return "bg-muted text-muted-foreground/50 cursor-not-allowed opacity-60"; // Disabled
    }
  };

  // Get step text color
  const getStepTextColor = (index: number) => {
    if (index === currentStep) return "text-blue-600";
    if (isStepCompleted(index)) return "text-green-600";
    if (isStepProcessing(index)) return "text-yellow-600";
    if (isStepFailed(index)) return "text-red-600";
    if (isStepAvailable(index)) return "text-blue-600";
    if (isStepPending(index)) return "text-muted-foreground";
    return "text-muted-foreground";
  };

  return (
    <>
      <div className="w-full bg-card/80 backdrop-blur-sm rounded-xl shadow-sm border border-border p-6">
        <div className="relative flex justify-between items-start">
          {steps.map((step, index) => (
            <div key={step} className="flex flex-col items-center relative group flex-1">
              {/* Full-width dotted connector line between this step and next */}
              {index < steps.length - 1 && (
                <div className="absolute top-4 left-1/2 w-full h-[2px] z-0">
                  {/* Base dotted line */}
                  <div 
                    className="h-full w-full border-t-2 border-dotted border-muted-foreground/30"
                    style={{ 
                      borderImage: 'repeating-linear-gradient(to right, #d1d5db 0, #d1d5db 8px, transparent 8px, transparent 16px) 1'
                    }}
                  />
                  
                  {/* Progress overlay */}
                  <motion.div
                    className="absolute top-0 left-0 h-full border-t-2 border-dotted border-green-500"
                    style={{ 
                      borderImage: 'repeating-linear-gradient(to right, #10b981 0, #10b981 8px, transparent 8px, transparent 16px) 1'
                    }}
                    initial={{ width: "0%" }}
                    animate={{ width: isStepCompleted(index) ? "100%" : "0%" }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              )}

              {/* Step circle */}
              <button
                onClick={() => handleStepClick(index)}
                disabled={!isStepEnabled(index)}
                data-testid={`step-nav-${step.toLowerCase()}`}
                className={`w-10 h-10 rounded-full flex items-center justify-center z-10 transition-all duration-300 ${getStepStyling(index)}`}
                title={!isStepEnabled(index) ? "Complete previous steps first" : ""}
              >
                {isStepCompleted(index) ? (
                  <CheckCircle2 size={18} data-lucide="check-circle-2" />
                ) : isStepProcessing(index) ? (
                  <Loader2 size={18} className="animate-spin" data-lucide="loader-2" />
                ) : isStepFailed(index) ? (
                  <AlertCircle size={18} data-lucide="alert-circle" />
                ) : (
                  index + 1
                )}
              </button>

              {/* Step label */}
              <span
                className={`mt-3 text-sm font-medium ${getStepTextColor(index)} whitespace-nowrap`}
              >
                {step}
              </span>

              {/* Rerun button for completed steps */}
              {isStepCompleted(index) && presentationId && onRerunStep && (
                <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <RerunButton
                    presentationId={presentationId}
                    stepName={getStepApiName(index)}
                    stepDisplayName={step}
                    onRerunComplete={() => onRerunStep(index)}
                    size="sm"
                    variant="ghost"
                    className="text-xs px-2 py-1 h-6"
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Continue button - completely separate from the workflow steps container */}
      {onContinue && continueButtonStep >= 0 && (
        <div className="flex justify-center mt-4">
          <Button
            onClick={onContinue}
            disabled={isProcessing}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg shadow-lg flex items-center gap-2"
            data-testid="continue-button"
          >
            {isProcessing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Processing...
              </>
            ) : (
              <>
                Continue to Next Step
                <ArrowRight size={16} />
              </>
            )}
          </Button>
        </div>
      )}
    </>
  )
}
