"use client"

import { motion } from "framer-motion"
import { CheckCircle2, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface WorkflowStepsProps {
  steps: string[]
  currentStep: number
  onChange: (step: number) => void
  onContinue?: () => Promise<void>
  isProcessing?: boolean
  completedSteps?: boolean[] // Array of booleans indicating which steps are completed
}

export default function WorkflowSteps({ 
  steps, 
  currentStep, 
  onChange, 
  onContinue,
  isProcessing = false,
  completedSteps = [] 
}: WorkflowStepsProps) {
  
  // Function to check if a step is enabled for navigation
  const isStepEnabled = (index: number) => {
    // If we have completion data from the backend, use that
    if (completedSteps && completedSteps.length > 0) {
      // Always allow current step
      if (index === currentStep) return true;
      
      // Allow any completed step
      if (index < completedSteps.length && completedSteps[index]) return true;
      
      // Allow next step after a completed step
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
    if (isStepEnabled(index)) {
      onChange(index);
    }
  }
  
  // The step after which we should show the continue button
  const continueButtonStep = findLastActionableCompletedStep();

  return (
    <div className="w-full bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100 p-4">
      <div className="flex justify-between items-center">
        {steps.map((step, index) => (
          <div key={step} className="flex flex-col items-center relative group">
            {/* Connector line between this step and next */}
            {index < steps.length - 1 && (
              <div className="absolute top-4 left-[50%] w-full h-[2px] bg-gray-200 z-0">
                <motion.div
                  className="h-full bg-primary-500"
                  initial={{ width: "0%" }}
                  animate={{ width: isStepCompleted(index) ? "100%" : "0%" }}
                  transition={{ duration: 0.5 }}
                />
                
                {/* Continue button - show if this is the last completed step before a non-completed step */}
                {onContinue && index === continueButtonStep && (
                  <div className="absolute top-[-16px] right-0 transform translate-x-[50%] z-20">
                    <Button
                      onClick={onContinue}
                      disabled={isProcessing}
                      className="w-8 h-8 p-0 rounded-full bg-primary-500 hover:bg-primary-600 text-white shadow-lg"
                      size="icon"
                      title="Continue to next step"
                    >
                      {isProcessing ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        <ArrowRight size={14} />
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Step circle */}
            <button
              onClick={() => handleStepClick(index)}
              disabled={!isStepEnabled(index)}
              className={`w-8 h-8 rounded-full flex items-center justify-center z-10 transition-all duration-300 ${
                isStepCompleted(index)
                  ? "bg-primary-500 text-white"
                  : index === currentStep
                    ? "bg-primary-500 text-white ring-4 ring-primary-100"
                    : isStepEnabled(index)
                      ? "bg-gray-100 text-gray-400 hover:bg-gray-200"
                      : "bg-gray-100 text-gray-300 cursor-not-allowed opacity-60"
              }`}
              title={!isStepEnabled(index) ? "Complete previous steps first" : ""}
            >
              {isStepCompleted(index) ? <CheckCircle2 size={16} /> : index + 1}
            </button>

            {/* Step label */}
            <span
              className={`mt-2 text-sm font-medium ${
                index === currentStep ? "text-primary-600" : 
                isStepCompleted(index) ? "text-primary-500" : "text-gray-500"
              } whitespace-nowrap`}
            >
              {step}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
