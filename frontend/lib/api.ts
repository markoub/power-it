import type { Presentation } from './types';

// Always use the direct backend URL to avoid redirect issues
const API_URL = 'http://localhost:8000';

export const api = {
  // Get all presentations
  async getPresentations(): Promise<Presentation[]> {
    try {
      const response = await fetch(`${API_URL}/presentations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch presentations: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching presentations:', error);
      return [];
    }
  },

  // Get a single presentation by ID
  async getPresentation(id: string): Promise<Presentation | null> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch presentation: ${response.status}`);
      }
      
      const responseData = await response.json();
      console.log('Received presentation data:', responseData);
      
      // Extract slides from the steps (particularly from the 'slides' step if it exists)
      let slides: any[] = [];
      if (responseData.steps && Array.isArray(responseData.steps)) {
        // Find the slides step
        const slidesStep = responseData.steps.find(
          (step: any) => step.step === 'slides' && step.status === 'completed' && step.result && step.result.slides
        );
        
        if (slidesStep && slidesStep.result && Array.isArray(slidesStep.result.slides)) {
          // Convert backend slide format to frontend format
          slides = slidesStep.result.slides.map((slide: any, index: number) => {
            return {
              id: slide.id || `slide-${index}`,
              title: slide.fields?.title || `Slide ${index + 1}`,
              content: slide.fields?.content || '',
              order: index,
              imagePrompt: '',
              imageUrl: ''
            };
          });
        }
      }
      
      // Map backend response to frontend model
      return {
        id: responseData.id.toString(),
        name: responseData.name,
        author: responseData.author || '',
        researchMethod: 'ai', // Default to AI, can be updated later if needed
        topic: responseData.topic || '',
        manualResearch: responseData.research_content || '',
        slides: slides,
        steps: responseData.steps,
        createdAt: responseData.created_at,
        updatedAt: responseData.updated_at
      };
    } catch (error) {
      console.error(`Error fetching presentation ${id}:`, error);
      return null;
    }
  },

  // Create a new presentation
  async createPresentation(presentation: Omit<Presentation, 'id' | 'createdAt' | 'updatedAt'>): Promise<Presentation | null> {
    try {
      // Map frontend model to backend model
      const backendPresentationData: Record<string, any> = {
        name: presentation.name,
        author: presentation.author,
        research_type: presentation.researchMethod === 'ai' ? 'research' : 'manual_research',
      };
      
      // Add the appropriate research fields based on research type
      if (presentation.researchMethod === 'ai') {
        backendPresentationData.topic = presentation.topic;
      } else {
        backendPresentationData.research_content = presentation.manualResearch;
      }
      
      console.log('Sending presentation data to API:', JSON.stringify(backendPresentationData));
      
      const response = await fetch(`${API_URL}/presentations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendPresentationData),
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        // Enhanced error handling with detailed error information
        console.error(`Server error ${response.status}:`, responseData);
        
        let errorMessage = "Failed to create presentation";
        
        // If we have a detailed error message from the API, use it
        if (responseData && responseData.detail) {
          errorMessage = responseData.detail;
          
          // Attach additional error information if available
          if (responseData.error_type) {
            const errorDetails = {
              ...responseData
            };
            
            throw new Error(JSON.stringify({
              message: errorMessage,
              details: errorDetails
            }));
          }
        }
        
        throw new Error(errorMessage);
      }
      
      console.log('Received response:', responseData);
      
      // Map backend response to frontend model
      return {
        id: responseData.id.toString(),
        name: responseData.name,
        author: responseData.author || '',
        researchMethod: presentation.researchMethod, // Use the original value from frontend
        topic: responseData.topic || '',
        manualResearch: responseData.research_content || '',
        slides: [], // Always initialize slides as empty array
        createdAt: responseData.created_at,
        updatedAt: responseData.updated_at
      };
    } catch (error) {
      console.error('Error creating presentation:', error);
      throw error; // Re-throw to allow the component to handle the error
    }
  },
  
  // Update an existing presentation
  async updatePresentation(id: string, presentation: Partial<Presentation>): Promise<Presentation | null> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}/modify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(presentation),
        mode: 'cors',
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

  // Run a specific step for a presentation
  async runPresentationStep(id: string, step: string): Promise<any> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}/steps/${step}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to run step: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Error running step for presentation ${id}:`, error);
      return null;
    }
  },

  // Delete a presentation
  async deletePresentation(id: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_URL}/presentations/${id}`, {
        method: 'DELETE',
        mode: 'cors',
      });
      
      return response.ok;
    } catch (error) {
      console.error(`Error deleting presentation ${id}:`, error);
      return false;
    }
  }
}; 