import { useState } from "react"
import { Button } from "@/components/ui/button"
import { RefreshCw } from "lucide-react"
import { api } from "@/lib/api"
import { toast } from "@/components/ui/use-toast"

interface RerunButtonProps {
  presentationId: string | number
  stepName: string
  stepDisplayName: string
  onRerunComplete?: () => Promise<void>
  disabled?: boolean
  variant?: "default" | "outline" | "secondary" | "destructive" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
  className?: string
  params?: { [key: string]: any }
}

export default function RerunButton({
  presentationId,
  stepName,
  stepDisplayName,
  onRerunComplete,
  disabled = false,
  variant = "outline",
  size = "sm",
  className = "",
  params = {}
}: RerunButtonProps) {
  const [isRerunning, setIsRerunning] = useState(false)

  const handleRerun = async () => {
    setIsRerunning(true)
    try {
      const id = typeof presentationId === 'number' ? presentationId.toString() : presentationId
      await api.runPresentationStep(id, stepName, params)
      
      toast({
        title: `${stepDisplayName} rerun started`,
        description: `Your ${stepDisplayName.toLowerCase()} is being regenerated...`,
      })

      // Wait a moment to let the backend process start
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Call the completion callback if provided
      if (onRerunComplete) {
        await onRerunComplete()
      }
    } catch (error) {
      console.error(`Error rerunning ${stepName}:`, error)
      toast({
        title: "Error",
        description: `Failed to rerun ${stepDisplayName.toLowerCase()}. Please try again.`,
        variant: "destructive",
      })
    } finally {
      setIsRerunning(false)
    }
  }

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleRerun}
      disabled={disabled || isRerunning}
      className={`flex items-center gap-2 ${className}`}
      data-testid={`rerun-${stepName}-button`}
    >
      <RefreshCw size={16} className={isRerunning ? 'animate-spin' : ''} />
      {isRerunning ? `Rerunning ${stepDisplayName}...` : `Rerun ${stepDisplayName}`}
    </Button>
  )
} 