"use client"

import React, { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { AlertCircle, HelpCircle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface ClarificationQuestion {
  question: string
  context: string
  options?: string[]
}

interface ClarificationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  questions: ClarificationQuestion[]
  topic: string
  onClarify: (clarifiedTopic: string) => void
  onSkip: () => void
}

export function ClarificationDialog({
  open,
  onOpenChange,
  questions,
  topic,
  onClarify,
  onSkip,
}: ClarificationDialogProps) {
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [customAnswers, setCustomAnswers] = useState<Record<number, string>>({})

  const handleAnswerChange = (questionIndex: number, value: string) => {
    setAnswers({ ...answers, [questionIndex]: value })
    // Clear custom answer if selecting a predefined option
    if (value !== "custom") {
      const newCustom = { ...customAnswers }
      delete newCustom[questionIndex]
      setCustomAnswers(newCustom)
    }
  }

  const handleCustomAnswerChange = (questionIndex: number, value: string) => {
    setCustomAnswers({ ...customAnswers, [questionIndex]: value })
  }

  const handleSubmit = () => {
    // Build clarified topic based on answers
    let clarifiedTopic = topic
    
    questions.forEach((question, index) => {
      const answer = answers[index]
      if (answer === "custom") {
        const customAnswer = customAnswers[index]
        if (customAnswer) {
          clarifiedTopic += ` - ${customAnswer}`
        }
      } else if (answer) {
        clarifiedTopic = clarifiedTopic.replace(
          new RegExp(question.context.split(" ")[0], "gi"),
          answer
        )
      }
    })

    onClarify(clarifiedTopic)
  }

  const allQuestionsAnswered = questions.every((_, index) => {
    const answer = answers[index]
    return answer && (answer !== "custom" || customAnswers[index])
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5 text-primary" />
            Clarification Needed
          </DialogTitle>
          <DialogDescription>
            I noticed some ambiguities in your topic. Please help me understand better so I can provide more accurate research.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <Card className="bg-muted/30">
            <CardContent className="pt-4">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-muted-foreground mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">Your topic: "{topic}"</p>
                  <p className="text-muted-foreground mt-1">
                    Please answer the questions below to clarify your intent.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {questions.map((question, index) => (
            <div key={index} className="space-y-3">
              <div>
                <h4 className="font-medium">{question.question}</h4>
                <p className="text-sm text-muted-foreground mt-1">{question.context}</p>
              </div>

              <RadioGroup
                value={answers[index] || ""}
                onValueChange={(value) => handleAnswerChange(index, value)}
              >
                {question.options?.map((option, optionIndex) => (
                  <div key={optionIndex} className="flex items-center space-x-2">
                    <RadioGroupItem value={option} id={`q${index}-o${optionIndex}`} />
                    <Label
                      htmlFor={`q${index}-o${optionIndex}`}
                      className="cursor-pointer"
                    >
                      {option}
                    </Label>
                  </div>
                ))}
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="custom" id={`q${index}-custom`} />
                    <Label htmlFor={`q${index}-custom`} className="cursor-pointer">
                      Other (please specify)
                    </Label>
                  </div>
                  {answers[index] === "custom" && (
                    <Textarea
                      value={customAnswers[index] || ""}
                      onChange={(e) => handleCustomAnswerChange(index, e.target.value)}
                      placeholder="Enter your clarification..."
                      className="ml-6"
                      rows={2}
                    />
                  )}
                </div>
              </RadioGroup>
            </div>
          ))}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onSkip}>
            Skip Clarification
          </Button>
          <Button onClick={handleSubmit} disabled={!allQuestionsAnswered}>
            Continue with Clarified Topic
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}