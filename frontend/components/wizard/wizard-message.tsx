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
          isAssistant ? "bg-primary-100 text-primary-500" : "bg-gray-100 text-gray-500"
        }`}
      >
        {isAssistant ? <Sparkles size={16} /> : <UserIcon size={16} />}
      </div>
      <div
        className={`rounded-lg p-3 max-w-[85%] ${
          isAssistant ? "bg-primary-50 text-gray-800" : "bg-gray-100 text-gray-800 ml-auto"
        }`}
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
