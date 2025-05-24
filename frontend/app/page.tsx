import Link from "next/link"
import { Button } from "@/components/ui/button"
import { PlusCircle, Presentation, Sparkles } from "lucide-react"
import PresentationList from "@/components/presentation-list"
import { PatternBackground, AnimatedContainer, AnimatedItem, GradientHeading } from "@/components/ui-elements"
import ClientWrapper from "@/components/client-wrapper"

export default function HomePage() {
  return (
    <div className="min-h-screen relative overflow-hidden" data-testid="presentations-page">
      <PatternBackground pattern="gradient" />

      <div className="container mx-auto px-4 py-12">
        <AnimatedContainer className="mb-12 text-center">
          <AnimatedItem>
            <div className="inline-flex items-center justify-center p-2 mb-4 bg-primary-100 rounded-full">
              <Sparkles className="h-6 w-6 text-primary-500 animate-bounce-light" />
            </div>
          </AnimatedItem>

          <AnimatedItem>
            <GradientHeading size="xl" className="mb-3" data-testid="page-title">
              AI Presentation Creator
            </GradientHeading>
          </AnimatedItem>

          <AnimatedItem>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
              Create stunning presentations with the power of AI. Transform your ideas into professional slides in
              minutes.
            </p>
          </AnimatedItem>

          <AnimatedItem>
            <Link href="/create">
              <Button 
                className="bg-primary hover:bg-primary-600 text-white font-medium px-6 py-2 rounded-full transition-all duration-300 shadow-lg hover:shadow-primary-500/25 flex items-center gap-2 text-lg"
                data-testid="ai-research-button"
              >
                <PlusCircle size={20} />
                Create New Presentation
              </Button>
            </Link>
          </AnimatedItem>
        </AnimatedContainer>

        <div className="relative">
          <PatternBackground pattern="dots" className="rounded-3xl" />
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-gray-100 dark:border-gray-700 animate-fade-in" data-testid="presentations-container">
            <div className="flex items-center gap-3 mb-6">
              <Presentation className="h-6 w-6 text-primary-500" />
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100" data-testid="presentations-section-title">Your Presentations</h2>
            </div>
            <ClientWrapper fallback={
              <div className="flex justify-center items-center py-12" data-testid="presentations-loading-fallback">
                <div className="h-8 w-8 rounded-full border-2 border-primary-500 border-t-transparent animate-spin"></div>
                <span className="ml-2 text-gray-600 dark:text-gray-300">Loading presentations...</span>
              </div>
            }>
              <PresentationList />
            </ClientWrapper>
          </div>
        </div>
      </div>
    </div>
  )
}
