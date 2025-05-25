export interface Slide {
  id: string;
  /** Raw slide type from the backend (e.g. Welcome, ContentImage) */
  type: string;
  /** Original fields object returned by the API */
  fields: Record<string, any>;
  /** Convenience title extracted from fields */
  title: string;
  /** Convenience content (can be string or array of strings) */
  content: string | string[];
  notes?: string;
  order: number;
  imagePrompt?: string;
  imageUrl?: string;
}

export interface PresentationStep {
  id: number;
  step:
    | "research"
    | "manual_research"
    | "slides"
    | "images"
    | "compiled"
    | "pptx";
  status: "pending" | "processing" | "completed" | "failed";
  result?: Record<string, any> | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Presentation {
  id: string | number; // Allow number for ID from backend, string for frontend state consistency if needed
  name: string; // Changed from title to name to match backend
  author?: string; // Made optional to match backend
  researchMethod?: "ai" | "manual"; // Keep for frontend logic, though backend uses step type
  topic?: string;
  manualResearch?: string; // This can be deprecated if research content is always in steps
  slides: Slide[];
  steps?: PresentationStep[]; // Add steps array
  thumbnailUrl?: string; // URL to the first slide thumbnail image
  createdAt: string;
  updatedAt: string;
}

export interface PaginatedPresentations {
  items: Presentation[];
  total: number;
}
