"use client"

import { cn } from "@/lib/utils"
import { cva } from "class-variance-authority"
import type { VariantProps } from "class-variance-authority"
import { motion } from "framer-motion"
import type { HTMLAttributes } from "react"

// Pattern Background
interface PatternBackgroundProps extends HTMLAttributes<HTMLDivElement> {
  pattern: "dots" | "grid" | "diagonal" | "gradient"
}

export function PatternBackground({ pattern, className, ...props }: PatternBackgroundProps) {
  return (
    <div
      className={cn(
        "absolute inset-0 -z-10",
        {
          "pattern-dots": pattern === "dots",
          "pattern-grid": pattern === "grid",
          "pattern-diagonal": pattern === "diagonal",
          "gradient-bg": pattern === "gradient",
        },
        className,
      )}
      {...props}
    />
  )
}

// Animated Container
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 15,
    },
  },
}

export function AnimatedContainer({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" className={className} {...props}>
      {children}
    </motion.div>
  )
}

export function AnimatedItem({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <motion.div variants={itemVariants} className={className} {...props}>
      {children}
    </motion.div>
  )
}

// Gradient Heading
const headingVariants = cva("font-bold gradient-text", {
  variants: {
    size: {
      sm: "text-xl",
      md: "text-2xl",
      lg: "text-3xl",
      xl: "text-4xl",
      "2xl": "text-5xl",
    },
  },
  defaultVariants: {
    size: "lg",
  },
})

interface GradientHeadingProps extends HTMLAttributes<HTMLHeadingElement>, VariantProps<typeof headingVariants> {}

export function GradientHeading({ size, className, children, ...props }: GradientHeadingProps) {
  return (
    <h1 className={cn(headingVariants({ size, className }))} {...props}>
      {children}
    </h1>
  )
}

// Glass Card
export function GlassCard({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("glass-effect rounded-xl border border-white/20 shadow-lg", className)} {...props}>
      {children}
    </div>
  )
}

// Animated Button
export function AnimatedButton({ children, className, ...props }: HTMLAttributes<HTMLButtonElement>) {
  return (
    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className={className} {...props}>
      {children}
    </motion.button>
  )
}
