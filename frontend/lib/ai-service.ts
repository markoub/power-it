import { generateText } from "ai"
import { openai } from "@ai-sdk/openai"
import type { Slide } from "./types"
import { v4 as uuidv4 } from "uuid"

export async function generatePresentationContent(topic: string): Promise<Slide[]> {
  try {
    const prompt = `
      Create a visually engaging presentation about "${topic}". 
      Generate 5 slides including:
      1. An attention-grabbing introduction slide
      2. 3 content slides with key points and engaging content
      3. A memorable conclusion slide
      
      For each slide, provide a creative title and detailed content.
      Make the content visually descriptive and engaging.
      
      Format your response as a JSON array of slide objects with the following structure:
      [
        {
          "title": "Creative Slide Title",
          "content": "Detailed slide content with multiple sentences. Make it engaging and informative."
        }
      ]
    `

    const { text } = await generateText({
      model: openai("gpt-4o"),
      prompt,
    })

    // Parse the response
    const slidesData = JSON.parse(text)

    // Convert to our Slide type with IDs and order
    const slides: Slide[] = slidesData.map((slide: any, index: number) => ({
      id: uuidv4(),
      title: slide.title,
      content: slide.content,
      order: index,
    }))

    return slides
  } catch (error) {
    console.error("Error generating presentation content:", error)
    // Return some default slides if AI generation fails
    return [
      {
        id: uuidv4(),
        title: `Exploring ${topic}`,
        content: `Introduction to ${topic}\nLet's discover what makes this topic fascinating and important in today's world.`,
        order: 0,
      },
      {
        id: uuidv4(),
        title: "Key Insights",
        content: `Main points about ${topic}\nThese are the critical aspects we need to understand.`,
        order: 1,
      },
      {
        id: uuidv4(),
        title: "Looking Forward",
        content: `Conclusion about ${topic}\nWhat we've learned and how it impacts our future.`,
        order: 2,
      },
    ]
  }
}
