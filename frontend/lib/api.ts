import type { Presentation } from "./types";

// Always use the direct backend URL to avoid redirect issues
const API_URL = "http://localhost:8000";

// Helper function to ensure URL is properly formatted
const formatImageUrl = (url: string): string => {
  if (!url) return "";

  // If it's already an absolute URL, return it
  if (url.startsWith("http")) return url;

  // If it's a relative URL, prepend the API URL
  return `${API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
};

export const api = {
  async getPresentations(): Promise<Presentation[]> {
    try {
      const response = await fetch(`${API_URL}/presentations`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        mode: "cors",
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch presentations: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error fetching presentations:", error);
      return [];
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

            if (Array.isArray(content)) {
              content = content.join("\n");
            } else if (typeof content !== "string") {
              content = String(content || "");
            }

            const imageUrl = fields.image_url || slide.image_url || "";

            return {
              id: slide.id || `slide-${index}`,
              type: slide.type || "Content",
              fields,
              title,
              content,
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
      const backendPresentationData: Record<string, any> = {
        name: presentation.name,
        author: presentation.author,
        research_type:
          presentation.researchMethod === "ai" ? "research" : "manual_research",
      };

      if (presentation.researchMethod === "ai") {
        backendPresentationData.topic = presentation.topic;
      } else {
        backendPresentationData.research_content = presentation.manualResearch;
      }

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
        researchMethod: presentation.researchMethod,
        topic: responseData.topic || "",
        manualResearch: responseData.research_content || "",
        slides: [],
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
      const response = await fetch(`${API_URL}/presentations/${id}/modify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(presentation),
        mode: "cors",
      });

      if (!response.ok) {
        throw new Error(`Failed to update presentation: ${response.status}`);
      }

      return await response.json();
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

  async runPresentationStep(id: string, step: string): Promise<any> {
    try {
      const response = await fetch(
        `${API_URL}/presentations/${id}/steps/${step}/run`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
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

  // Get PPTX slide images
  async getPptxSlides(id: string): Promise<string[]> {
    try {
      console.log(`Requesting PPTX slides from ${API_URL}/presentations/${id}/pptx-slides`);
      const resp = await fetch(`${API_URL}/presentations/${id}/pptx-slides`, {
        method: "GET",
        mode: "cors",
      });
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
      console.error(`Error fetching PPTX slides for ${id}:`, error);
      return [];
    }
  },

  // Delete a presentation
  async deletePresentation(id: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}`, {
        method: "DELETE",
        mode: "cors",
      });

      return response.ok;
    } catch (error) {
      console.error(`Error deleting presentation ${id}:`, error);
      return false;
    }
  },
};