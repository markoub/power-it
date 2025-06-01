import type React from "react"
import { Sparkles } from "lucide-react"

interface WizardMessageProps {
  role: "user" | "assistant"
  content: string
}

export default function WizardMessage({ role, content }: WizardMessageProps) {
  const isAssistant = role === "assistant"

  return (
    <div className={`flex gap-2 ${isAssistant ? "flex-row" : "flex-row-reverse"}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isAssistant ? "bg-primary/20 text-primary dark:bg-primary/30" : "bg-muted text-muted-foreground"
        }`}
      >
        {isAssistant ? <Sparkles size={16} /> : <UserIcon size={16} />}
      </div>
      <div
        className={`rounded-lg p-3 max-w-[85%] ${
          isAssistant ? "bg-primary/10 text-foreground dark:bg-primary/20" : "bg-muted text-foreground ml-auto"
        }`}
        data-testid={`wizard-message-${role}`}
      >
        <div className="whitespace-pre-wrap">{content}</div>
      </div>
    </div>
  )
}

function UserIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  )
}
