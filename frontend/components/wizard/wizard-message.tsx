import type React from "react"
import { Sparkles } from "lucide-react"
import MarkdownRenderer from "@/components/ui/markdown-renderer"

interface WizardMessageProps {
  role: "user" | "assistant"
  content: string
}

export default function WizardMessage({ role, content }: WizardMessageProps) {
  const isAssistant = role === "assistant"

  return (
    <div className={`flex gap-3 ${isAssistant ? "flex-row" : "flex-row-reverse"}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${
          isAssistant 
            ? "bg-gradient-to-br from-primary/20 to-primary/30 text-primary dark:from-primary/30 dark:to-primary/40" 
            : "bg-gradient-to-br from-muted to-muted/80 text-muted-foreground"
        }`}
      >
        {isAssistant ? <Sparkles size={16} className="animate-pulse" /> : <UserIcon size={16} />}
      </div>
      <div
        className={`rounded-xl px-4 py-3 max-w-[85%] shadow-sm transition-all hover:shadow-md ${
          isAssistant 
            ? "bg-gradient-to-br from-primary/10 to-primary/5 text-foreground dark:from-primary/20 dark:to-primary/10 border border-primary/10" 
            : "bg-gradient-to-br from-muted to-muted/60 text-foreground ml-auto border border-muted-foreground/10"
        }`}
        data-testid={`wizard-message-${role}`}
      >
        <MarkdownRenderer 
          content={content} 
          className="text-sm leading-relaxed prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2 prose-p:text-foreground prose-li:text-foreground prose-headings:text-foreground"
        />
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
