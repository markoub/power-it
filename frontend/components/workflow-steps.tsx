"use client"

import { motion } from "framer-motion"
import { CheckCircle2 } from "lucide-react"

interface WorkflowStepsProps {
  steps: string[]
  currentStep: number
  onChange: (step: number) => void
}

export default function WorkflowSteps({ steps, currentStep, onChange }: WorkflowStepsProps) {
  return (
    <div className="w-full bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-100 p-4">
      <div className="flex justify-between items-center">
        {steps.map((step, index) => (
          <div key={step} className="flex flex-col items-center relative group">
            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="absolute top-4 left-[50%] w-full h-[2px] bg-gray-200 z-0">
                <motion.div
                  className="h-full bg-primary-500"
                  initial={{ width: "0%" }}
                  animate={{ width: currentStep > index ? "100%" : "0%" }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            )}

            {/* Step circle */}
            <button
              onClick={() => onChange(index)}
              className={`w-8 h-8 rounded-full flex items-center justify-center z-10 transition-all duration-300 ${
                index < currentStep
                  ? "bg-primary-500 text-white"
                  : index === currentStep
                    ? "bg-primary-500 text-white ring-4 ring-primary-100"
                    : "bg-gray-100 text-gray-400 hover:bg-gray-200"
              }`}
            >
              {index < currentStep ? <CheckCircle2 size={16} /> : index + 1}
            </button>

            {/* Step label */}
            <span
              className={`mt-2 text-sm font-medium ${
                index === currentStep ? "text-primary-600" : "text-gray-500"
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
