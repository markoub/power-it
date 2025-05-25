"use client";

import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

interface MarkdownRendererProps {
  content: string | string[];
  mini?: boolean;
  className?: string;
  animated?: boolean;
}

// Helper function to convert content to markdown string
function contentToMarkdown(content: string | string[]): string {
  if (Array.isArray(content)) {
    // Convert array to markdown bullet points
    return content
      .filter(item => item && typeof item === 'string' && item.trim())
      .map(item => `- ${item.trim()}`)
      .join('\n');
  }
  
  if (typeof content === 'string') {
    // Check if content looks like it was originally an array joined with newlines
    // If it has multiple lines without markdown formatting, convert to bullet points
    const lines = content.split('\n').filter(line => line.trim());
    
    // If we have multiple lines and none start with markdown bullets/numbers/headers
    if (lines.length > 1) {
      const hasMarkdownFormatting = lines.some(line => 
        line.trim().match(/^[-*+]\s/) ||  // bullet points
        line.trim().match(/^\d+\.\s/) ||  // numbered lists
        line.trim().match(/^#{1,6}\s/) || // headers
        line.trim().match(/^>\s/)         // blockquotes
      );
      
      // If no markdown formatting detected, convert to bullet points
      if (!hasMarkdownFormatting) {
        return lines.map(line => `- ${line.trim()}`).join('\n');
      }
    }
    
    // Return as-is if it already has markdown or is a single line
    return content;
  }
  
  return '';
}

export default function MarkdownRenderer({ 
  content, 
  mini = false, 
  className = "",
  animated = false 
}: MarkdownRendererProps) {
  const markdownContent = contentToMarkdown(content);
  
  const baseClass = mini 
    ? "prose prose-xs max-w-none prose-headings:text-xs prose-p:text-[8px] prose-p:leading-tight prose-ul:text-[8px] prose-li:text-[8px] prose-strong:text-[8px] prose-em:text-[8px]"
    : "prose prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-a:text-primary-600 prose-strong:text-gray-900 prose-em:text-gray-600";

  const combinedClassName = `${baseClass} ${className}`;

  if (animated && !mini) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className={combinedClassName}
      >
        <ReactMarkdown
          components={{
            // Custom components for better control
            h1: ({ children }) => (
              <motion.h1
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                {children}
              </motion.h1>
            ),
            h2: ({ children }) => (
              <motion.h2
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                {children}
              </motion.h2>
            ),
            h3: ({ children }) => (
              <motion.h3
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                {children}
              </motion.h3>
            ),
            p: ({ children }) => (
              <motion.p
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                {children}
              </motion.p>
            ),
            ul: ({ children }) => (
              <motion.ul
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                {children}
              </motion.ul>
            ),
            ol: ({ children }) => (
              <motion.ol
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                {children}
              </motion.ol>
            ),
            li: ({ children }) => (
              <motion.li
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
              >
                {children}
              </motion.li>
            ),
          }}
        >
          {markdownContent}
        </ReactMarkdown>
      </motion.div>
    );
  }

  return (
    <div className={combinedClassName}>
      <ReactMarkdown>
        {markdownContent}
      </ReactMarkdown>
    </div>
  );
} 