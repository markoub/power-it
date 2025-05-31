"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Link, ChevronDown, ChevronRight, FileText, Lightbulb } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import type { Presentation } from "@/lib/types"

interface ResearchContextProps {
  presentation: Presentation
}

export default function ResearchContext({ presentation }: ResearchContextProps) {
  const [expandedSections, setExpandedSections] = useState<string[]>([])
  const [researchData, setResearchData] = useState<{ content: string; links: any[] } | null>(null)
  const [sections, setSections] = useState<{ title: string; content: string; level: number }[]>([])

  useEffect(() => {
    // Extract research data from presentation steps
    const researchStep = presentation.steps?.find(
      (step) => step.step === "research" || step.step === "manual_research"
    )
    
    if (researchStep?.result) {
      const data = researchStep.result as { content: string; links: any[] }
      setResearchData(data)
      
      // Parse sections from markdown content
      if (data.content) {
        const parsedSections = parseMarkdownSections(data.content)
        setSections(parsedSections)
      }
    }
  }, [presentation])

  const parseMarkdownSections = (content: string) => {
    const lines = content.split("\n")
    const sections: { title: string; content: string; level: number }[] = []
    let currentSection: { title: string; content: string; level: number } | null = null

    lines.forEach((line) => {
      const headerMatch = line.match(/^(#{1,6})\s+(.+)/)
      if (headerMatch) {
        if (currentSection) {
          sections.push(currentSection)
        }
        currentSection = {
          title: headerMatch[2],
          content: "",
          level: headerMatch[1].length,
        }
      } else if (currentSection) {
        currentSection.content += line + "\n"
      }
    })

    if (currentSection) {
      sections.push(currentSection)
    }

    return sections
  }

  const toggleSection = (title: string) => {
    setExpandedSections((prev) =>
      prev.includes(title)
        ? prev.filter((t) => t !== title)
        : [...prev, title]
    )
  }

  const getSectionStats = () => {
    const wordCount = researchData?.content.split(/\s+/).length || 0
    const linkCount = researchData?.links?.length || 0
    const sectionCount = sections.filter((s) => s.level === 2).length
    
    return { wordCount, linkCount, sectionCount }
  }

  if (!researchData) {
    return (
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Research Context
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No research content available yet.</p>
        </CardContent>
      </Card>
    )
  }

  const stats = getSectionStats()

  return (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <span className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Research Context
          </span>
          <div className="flex gap-2">
            <Badge variant="secondary" className="text-xs">
              {stats.wordCount} words
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {stats.sectionCount} sections
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {stats.linkCount} sources
            </Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[200px]">
          <div className="p-4 space-y-2">
            {/* Topic */}
            <div className="mb-3">
              <h4 className="text-xs font-semibold text-muted-foreground mb-1">Topic</h4>
              <p className="text-sm font-medium">{presentation.topic || "No topic set"}</p>
            </div>

            {/* Sections Outline */}
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                <FileText className="h-3 w-3" />
                Content Outline
              </h4>
              <div className="space-y-1">
                {sections.map((section, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <button
                      onClick={() => toggleSection(section.title)}
                      className="w-full text-left hover:bg-muted/50 rounded p-1.5 transition-colors"
                      style={{ paddingLeft: `${(section.level - 1) * 12}px` }}
                    >
                      <div className="flex items-center gap-1">
                        {section.level === 2 && (
                          expandedSections.includes(section.title) ? 
                            <ChevronDown className="h-3 w-3" /> : 
                            <ChevronRight className="h-3 w-3" />
                        )}
                        <span className={`text-xs ${section.level === 2 ? 'font-medium' : 'text-muted-foreground'}`}>
                          {section.title}
                        </span>
                      </div>
                    </button>
                    <AnimatePresence>
                      {expandedSections.includes(section.title) && section.content.trim() && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <p className="text-xs text-muted-foreground p-2 pl-6 line-clamp-3">
                            {section.content.trim().substring(0, 150)}...
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Sources */}
            {researchData.links && researchData.links.length > 0 && (
              <div className="mt-3 pt-3 border-t">
                <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                  <Link className="h-3 w-3" />
                  Sources
                </h4>
                <div className="space-y-1">
                  {researchData.links.slice(0, 3).map((link, index) => (
                    <a
                      key={index}
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary hover:underline block truncate"
                    >
                      {link.title || link.href}
                    </a>
                  ))}
                  {researchData.links.length > 3 && (
                    <p className="text-xs text-muted-foreground">
                      +{researchData.links.length - 3} more sources
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Quick Actions Hint */}
            <div className="mt-3 pt-3 border-t">
              <h4 className="text-xs font-semibold text-muted-foreground mb-1 flex items-center gap-1">
                <Lightbulb className="h-3 w-3" />
                Try asking me to:
              </h4>
              <ul className="text-xs text-muted-foreground space-y-0.5">
                <li>• Add a section about ethics</li>
                <li>• Expand on future trends</li>
                <li>• Make the introduction more engaging</li>
                <li>• Add more recent statistics</li>
              </ul>
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}