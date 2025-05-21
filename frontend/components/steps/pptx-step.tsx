"use client"

import { motion } from "framer-motion"
import type { Presentation } from "@/lib/types"
import PptxPreview from "../pptx-preview"

interface PptxStepProps {
  presentation: Presentation
}

export default function PptxStep({ presentation }: PptxStepProps) {
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h2 className="text-2xl font-bold mb-4 gradient-text">Presentation Ready</h2>
        <p className="text-gray-600 mb-6">
          Your presentation, "{presentation.name}", is structured and ready. You can export it as a PowerPoint file using the "Export PPTX" button in the header.
        </p>
      </motion.div>
      <PptxPreview presentation={presentation} />
    </div>
  )
}
