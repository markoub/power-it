import type { Presentation, PaginatedPresentations } from "./types";

// Use environment variable for API URL, fallback to production backend
// When running tests, NEXT_PUBLIC_API_URL should be set to http://localhost:8001
const API_URL = typeof window !== 'undefined' 
  ? (window.location.port === '3001' ? 'http://localhost:8001' : 'http://localhost:8000')
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

// Helper function to ensure URL is properly formatted
const formatImageUrl = (url: string): string => {
  if (!url) return "";

  // If it's already an absolute URL, return it
  if (url.startsWith("http")) return url;

  // If it's a relative URL, prepend the API URL
  return `${API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
};

export const api = {
  async getPresentations(
    page = 1,
    size = 10,
    status: "all" | "finished" | "in_progress" = "all"
  ): Promise<PaginatedPresentations> {
    try {
      const params = new URLSearchParams({
        page: String(page),
        size: String(size),
        status,
      });
      const response = await fetch(`${API_URL}/presentations?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch presentations: ${response.status}`);
      }
      const data = await response.json();
      
      // Transform the response to match frontend expectations
      const transformedItems = data.items.map((item: any) => ({
        id: item.id,
        name: item.name,
        topic: item.topic,
        author: item.author,
        thumbnailUrl: item.thumbnail_url ? formatImageUrl(item.thumbnail_url) : undefined,
        createdAt: item.created_at,
        updatedAt: item.updated_at,
        slides: [], // Will be populated when individual presentation is loaded
        researchMethod: "ai" as const,
        manualResearch: ""
      }));
      
      return {
        items: transformedItems,
        total: data.total
      };
    } catch (error) {
      console.error("Error fetching presentations:", error);
      return { items: [], total: 0 };
    }
  },

  async getPresentation(id: string): Promise<Presentation | null> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors",
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch presentation: ${response.status}`);
      }

      const responseData = await response.json();
      console.log("Received presentation data:", responseData);

      let slides: any[] = [];

      if (responseData.steps && Array.isArray(responseData.steps)) {
        const slidesStep = responseData.steps.find(
          (step: any) =>
            step.step === "slides" &&
            step.status === "completed" &&
            step.result &&
            step.result.slides
        );

        if (
          slidesStep &&
          slidesStep.result &&
          Array.isArray(slidesStep.result.slides)
        ) {
          slides = slidesStep.result.slides.map((slide: any, index: number) => {
            const fields = slide.fields || {};
            const title = fields.title || `Slide ${index + 1}`;
            let content: any = fields.content || "";

            // Handle different slide types that store content in different fields
            if (!content) {
              switch (slide.type) {
                case "Welcome":
                  // Welcome slides often have subtitle and author instead of content
                  content = [fields.subtitle, fields.author].filter(Boolean).join('\n\n');
                  break;
                case "Section":
                  // Section slides might not have content, that's OK
                  content = "";
                  break;
                case "TableOfContents":
                  // TOC slides have sections array
                  if (fields.sections && Array.isArray(fields.sections)) {
                    content = fields.sections.map((section: string) => `- ${section}`).join('\n');
                  }
                  break;
                case "3Images":
                  // 3Images slides store content in image descriptions
                  content = [
                    fields.image1 ? `**Image 1:** ${fields.image1}` : '',
                    fields.image2 ? `**Image 2:** ${fields.image2}` : '',
                    fields.image3 ? `**Image 3:** ${fields.image3}` : ''
                  ].filter(Boolean).join('\n\n');
                  break;
                case "ContentWithLogos":
                  // Logos slides might have company info
                  const logos = [fields.logo1, fields.logo2, fields.logo3].filter(Boolean);
                  if (logos.length > 0) {
                    content = `Companies featured: ${logos.join(', ')}`;
                  }
                  break;
              }
            }

            // Preserve original content structure but ensure it's valid
            if (Array.isArray(content)) {
              // Keep as array for proper markdown rendering
              content = content.filter(item => item && typeof item === 'string');
            } else if (typeof content !== "string") {
              content = String(content || "");
            }

            const imageUrl = fields.image_url || slide.image_url || "";

            return {
              id: slide.id || `slide-${index}`,
              type: slide.type || "Content",
              fields,
              title,
              content, // Now preserves array structure
              notes: typeof fields.notes === "string" ? fields.notes : "",
              order: index,
              imagePrompt: "",
              imageUrl: imageUrl ? formatImageUrl(imageUrl) : "",
            };
          });

          console.log(
            "Slides after initial mapping:",
            slides.map((s) => ({ id: s.id, title: s.title }))
          );
        }

        const imagesStep = responseData.steps.find(
          (step: any) =>
            step.step === "images" &&
            step.status === "completed" &&
            step.result &&
            Array.isArray(step.result.images)
        );

        if (
          imagesStep &&
          imagesStep.result &&
          Array.isArray(imagesStep.result.images)
        ) {
          console.log("Found images:", imagesStep.result.images);

          imagesStep.result.images.forEach((image: any) => {
            const formattedImageUrl = formatImageUrl(image.image_url);
            console.log("Formatted image URL:", formattedImageUrl);

            if (
              typeof image.slide_index === "number" &&
              slides[image.slide_index]
            ) {
              console.log(
                `Mapped image to slide at index ${image.slide_index}:`,
                slides[image.slide_index].title
              );
              slides[image.slide_index].imageUrl = formattedImageUrl;
              if (image.prompt) {
                slides[image.slide_index].imagePrompt = image.prompt;
              }
            } else if (image.slide_title) {
              const normalizedTitle = image.slide_title.trim();

              let matchedSlide = slides.find(
                (s) => s.title === normalizedTitle
              );

              if (!matchedSlide) {
                matchedSlide = slides.find(
                  (s) =>
                    s.title.includes(normalizedTitle) ||
                    normalizedTitle.includes(s.title)
                );
              }

              if (matchedSlide) {
                console.log(
                  `Mapped image to slide by title "${normalizedTitle}":`,
                  matchedSlide.title
                );
                matchedSlide.imageUrl = formattedImageUrl;
                if (image.prompt) {
                  matchedSlide.imagePrompt = image.prompt;
                }
              } else {
                console.warn(
                  `Could not find slide matching title: "${normalizedTitle}"`
                );
              }
            }
          });

          console.log(
            "Slides with mapped images:",
            slides.map((s) => ({
              title: s.title,
              hasImage: !!s.imageUrl,
              imageUrl: s.imageUrl,
            }))
          );
        }
      }

      return {
        id: responseData.id.toString(),
        name: responseData.name,
        author: responseData.author || "",
        researchMethod: "ai",
        topic: responseData.topic || "",
        manualResearch: responseData.research_content || "",
        slides: slides,
        steps: responseData.steps,
        thumbnailUrl: responseData.thumbnail_url,
        createdAt: responseData.created_at,
        updatedAt: responseData.updated_at,
      };
    } catch (error) {
      console.error(`Error fetching presentation ${id}:`, error);
      return null;
    }
  },

  async createPresentation(
    presentation: Omit<Presentation, "id" | "createdAt" | "updatedAt">
  ): Promise<Presentation | null> {
    try {
      // For simplified creation, we only send name and author
      // Research method will be determined later on the edit page
      const backendPresentationData: Record<string, any> = {
        name: presentation.name,
        author: presentation.author,
        research_type: "pending", // Default to pending, will be set later
      };

      console.log(
        "Sending presentation data to API:",
        JSON.stringify(backendPresentationData)
      );

      const response = await fetch(`${API_URL}/presentations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(backendPresentationData),
      });

      const responseData = await response.json();

      if (!response.ok) {
        console.error(`Server error ${response.status}:`, responseData);

        let errorMessage = "Failed to create presentation";

        if (responseData && responseData.detail) {
          errorMessage = responseData.detail;
          if (responseData.error_type) {
            const errorDetails = {
              ...responseData,
            };
            throw new Error(
              JSON.stringify({
                message: errorMessage,
                details: errorDetails,
              })
            );
          }
        }

        throw new Error(errorMessage);
      }

      return {
        id: responseData.id.toString(),
        name: responseData.name,
        author: responseData.author || "",
        researchMethod: undefined, // Will be set later
        topic: "",
        manualResearch: "",
        slides: [],
        thumbnailUrl: responseData.thumbnail_url,
        createdAt: responseData.created_at,
        updatedAt: responseData.updated_at,
      };
    } catch (error) {
      console.error("Error creating presentation:", error);
      throw error;
    }
  },

  async updatePresentation(
    id: string,
    presentation: Partial<Presentation>
  ): Promise<Presentation | null> {
    try {
      // Use the metadata endpoint for basic presentation updates
      const response = await fetch(`${API_URL}/presentations/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(presentation),
        mode: "cors",
      });

      if (!response.ok) {
        throw new Error(`Failed to update presentation: ${response.status}`);
      }

      const updatedData = await response.json();
      
      // Convert backend format to frontend format
      return {
        id: updatedData.id.toString(),
        name: updatedData.name,
        author: updatedData.author || "",
        topic: updatedData.topic || "",
        researchMethod: updatedData.research_type === "manual" ? "manual" : "ai",
        manualResearch: "",
        slides: presentation.slides || [],
        steps: presentation.steps || [],
        thumbnailUrl: presentation.thumbnailUrl || "",
        createdAt: updatedData.created_at || "",
        updatedAt: updatedData.updated_at || "",
      };
    } catch (error) {
      console.error(`Error updating presentation ${id}:`, error);
      return null;
    }
  },

  async modifyPresentation(
    id: string | number,
    prompt: string,
    slideIndex?: number,
    currentStep?: string
  ): Promise<any> {
    const payload: any = { prompt };
    if (typeof slideIndex === "number") payload.slide_index = slideIndex;
    if (currentStep) payload.current_step = currentStep;

    const response = await fetch(`${API_URL}/presentations/${id}/modify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      mode: "cors",
    });

    if (!response.ok) {
      throw new Error(`Failed to modify presentation: ${response.status}`);
    }

    return await response.json();
  },

  async processWizardRequest(
    id: string | number,
    prompt: string,
    currentStep: string,
    context?: any
  ): Promise<any> {
    const payload = {
      prompt,
      current_step: currentStep,
      context: context || {}
    };

    const response = await fetch(`${API_URL}/presentations/${id}/wizard`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      mode: "cors",
    });

    if (!response.ok) {
      throw new Error(`Failed to process wizard request: ${response.status}`);
    }

    return await response.json();
  },

  async modifyResearch(id: string | number, prompt: string): Promise<any> {
    const response = await fetch(
      `${API_URL}/presentations/${id}/research/modify`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
        mode: "cors",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to modify research: ${response.status}`);
    }

    return await response.json();
  },

  async saveModifiedResearch(
    id: string | number,
    data: any
  ): Promise<boolean> {
    const response = await fetch(
      `${API_URL}/presentations/${id}/save_modified_research`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        mode: "cors",
      }
    );

    return response.ok;
  },

  async saveModifiedPresentation(
    id: string | number,
    data: any
  ): Promise<boolean> {
    const response = await fetch(
      `${API_URL}/presentations/${id}/save_modified`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        mode: "cors",
      }
    );

    return response.ok;
  },

  async processWizardRequest(
    presentationId: number | string,
    query: string,
    step: string,
    context: any
  ): Promise<any> {
    try {
      const response = await fetch(
        `${API_URL}/presentations/${presentationId}/wizard`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query,
            step: step.toLowerCase(),
            context
          }),
          mode: "cors",
        }
      );

      if (!response.ok) {
        throw new Error(`Wizard request failed: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error("Error processing wizard request:", error);
      throw error;
    }
  },

  async runPresentationStep(id: string, step: string, params?: { 
    topic?: string; 
    research_content?: string; 
    image_provider?: string;
    target_slides?: number;
    target_audience?: string;
    content_density?: string;
    presentation_duration?: number;
    custom_prompt?: string;
  }): Promise<any> {
    try {
      // Prepare request body with optional parameters
      const body = params ? JSON.stringify(params) : undefined;

      const response = await fetch(
        `${API_URL}/presentations/${id}/steps/${step}/run`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: body,
          mode: "cors",
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to run step: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error running step for presentation ${id}:`, error);
      return null;
    }
  },

  async regenerateImage(
    id: string | number,
    slideIndex: number,
    prompt: string,
    provider?: string
  ): Promise<any> {
    const response = await fetch(
      `${API_URL}/presentations/${id}/slides/${slideIndex}/image`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, provider }),
        mode: "cors",
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to regenerate image: ${response.status}`);
    }

    return await response.json();
  },

  // Get PPTX slide images
  async getPptxSlides(id: string): Promise<string[]> {
    try {
      console.log(`Requesting PPTX slides from ${API_URL}/presentations/${id}/pptx-slides`);
      const resp = await fetch(`${API_URL}/presentations/${id}/pptx-slides`, {
        method: "GET",
        mode: "cors",
      });
      
      // If presentation doesn't exist or PPTX isn't ready, return empty array quietly
      if (resp.status === 404 || resp.status === 500) {
        console.log(`PPTX slides not available for presentation ${id} (status: ${resp.status})`);
        return [];
      }
      
      if (!resp.ok) {
        throw new Error(`Failed to fetch PPTX slides: ${resp.status}`);
      }
      
      const data = await resp.json();
      console.log(`PPTX slides response:`, data);
      
      if (data && Array.isArray(data.slides)) {
        const formattedUrls = data.slides.map((s: any) => formatImageUrl(s.url));
        console.log(`Formatted ${formattedUrls.length} PPTX slide URLs`);
        return formattedUrls;
      }
      return [];
    } catch (error) {
      console.warn(`Error fetching PPTX slides for ${id}:`, error);
      return [];
    }
  },

  // Get only the first PPTX slide image URL
  async getFirstPptxSlide(id: string): Promise<string | null> {
    try {
      const slides = await this.getPptxSlides(id);
      return slides.length > 0 ? slides[0] : null;
    } catch (error) {
      console.warn(`Error fetching first PPTX slide for ${id}:`, error);
      return null;
    }
  },

  // Delete a presentation
  async deletePresentation(id: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      return response.ok;
    } catch (error) {
      console.error(`Error deleting presentation ${id}:`, error);
      return false;
    }
  },

  async updatePresentationTopic(
    id: string,
    data: { topic: string }
  ): Promise<Presentation | null> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}/update-topic`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`Server error ${response.status}:`, errorData);
        throw new Error(errorData.detail || `Failed to update topic: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error updating topic for presentation ${id}:`, error);
      throw error;
    }
  },

  // TTS (Text-to-Speech) methods
  async streamSlideAudio(
    presentationId: number,
    slideIndex: number,
    options?: {
      voice?: string;
      rate?: string;
      pitch?: string;
      volume?: string;
    }
  ): Promise<Response> {
    const params = new URLSearchParams();
    if (options?.voice) params.append('voice', options.voice);
    if (options?.rate) params.append('rate', options.rate);
    if (options?.pitch) params.append('pitch', options.pitch);
    if (options?.volume) params.append('volume', options.volume);
    
    const url = `${API_URL}/presentations/${presentationId}/tts/slide/${slideIndex}?${params.toString()}`;
    return fetch(url);
  },

  async getAvailableVoices(locale?: string): Promise<{ voices: any[], total: number }> {
    const params = new URLSearchParams();
    if (locale) params.append('locale', locale);
    
    const response = await fetch(`${API_URL}/presentations/0/tts/voices?${params.toString()}`);
    if (!response.ok) {
      throw new Error('Failed to fetch voices');
    }
    return response.json();
  },

  async checkTopicClarification(topic: string): Promise<{
    needs_clarification: boolean;
    initial_message: string;
  }> {
    try {
      const response = await fetch(`${API_URL}/research/clarification/check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error(`Failed to check clarification: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error checking clarification:", error);
      // Return no clarification needed on error
      return { needs_clarification: false, initial_message: "" };
    }
  },
};