DEFAULT_RESEARCH_PROMPT = """You are a professional researcher creating detailed content for presentations.
Research the following topic thoroughly and create comprehensive markdown content: {query}

Make sure to include:
1. Introduction to the topic
2. Key facts, theories, or concepts
3. Historical background if relevant
4. Current state or applications
5. Future directions or trends
6. Organize with proper markdown headings, lists, and emphasis

For any source links, provide actual destination URLs, not redirect or tracking URLs.
Focus on creating substantial, informative content that would be valuable for a presentation."""

DEFAULT_SLIDES_PROMPT = """You are tasked with creating a professional presentation based on the following research:

{research_content}

Review the research content carefully and follow these guidelines:

1. If the research content contains specific instructions about:
   - Exact slide content
   - Specific number of slides
   - Particular speaker notes
   - Specific visual elements
   - Slide organization or structure
   - Any other precise details about the presentation

   Follow these instructions closely as specified. Do not deviate too much from explicit instructions, only if you want to introduce more visual elements.

2. If the research does not contain specific instructions:
   Create approximately {target_slides} slides for a professional presentation organized by sections.

IMPORTANT: You MUST use MULTIPLE DIFFERENT slide types. DO NOT default to using mostly 'Content' slides.
PRIORITIZE using 'ContentImage', 'ImageFull', and '3Images' slides wherever possible to make the presentation visually engaging.
AIM for no more than 30-40% of the main content slides (excluding Welcome/TOC/Section) to be of the plain 'Content' type.

REQUIRED SLIDE TYPES (these MUST be included):\n- 'Welcome' as the FIRST slide with title, subtitle, and author\n- At least 2-3 'Section' slides to divide your content into logical sections\n- A mix of 'Content' and 'ContentImage' slides (prefer 'ContentImage')\n- At least one '3Images' or 'ImageFull' slide if the content suits visual presentation

Available slide types:
{slide_types_info}

SPECIAL INSTRUCTIONS FOR 'ContentWithLogos' SLIDES:
- Use the 'ContentWithLogos' slide type when discussing specific companies, products, technologies, tools, or services
- You can include 1 to 3 logos per slide
- For each logo, simply include the company or product name (e.g., "Amazon AWS", "Microsoft", "Google Cloud")
- Do not include any URLs or placeholders; the actual logos will be fetched automatically

The presentation MUST follow this structure:
- First slide MUST be a 'Welcome' slide that includes the presentation title, subtitle, and "{author}" as the author
- Content MUST be organized into sections, each STARTING with a 'Section' slide
- Use 'ContentImage' slides for important points that would benefit from visual illustration
- Use regular 'Content' slides for general material when you have too much text, and no suitable image (do not have too many slides with only text)
- Use 'ImageFull' for topics that need visual emphasis
- Use '3Images' for comparing multiple items visually
- Use 'ContentWithLogos' whenever discussing specific companies, products, or technologies that have recognizable logos

The slides should be organized in clear sections (like "Market Research", "Our Services", "Reference Cases", etc.)

REMEMBER: Use a VARIETY of slide types, prioritizing visual elements over plain text slides.

For each slide, ONLY provide the required fields based on its type, as follows, and always include a "notes" field with 1-2 sentences of speaker notes:
- Welcome slides: title, subtitle, author
- Section slides: title
- Content slides: title, content (MUST be a JSON array of strings, each string a bullet point)
- ContentImage slides: title, subtitle, image, content (MUST be a JSON array of strings, each string a bullet point)
- ImageFull slides: title, image, explanation
- 3Images slides: title, image1, image2, image3, image1subtitle, image2subtitle, image3subtitle
- ContentWithLogos slides: title, content (MUST be a JSON array of strings), logo1, logo2 (optional), logo3 (optional)

When there are images, do not put placeholders, put the explanation what should be on the image.
For logos, simply put the company or product name (e.g., "AWS", "Microsoft", "Google") - the actual logo will be fetched.

DO NOT include any fields not specifically listed for each slide type. For example, Welcome slides should NOT have a content field.

Note: Include the "notes" field for each slide. Do not include any "visual_suggestions" field.

Format your response as a valid JSON object where:
1. The root object has "title", "author", and "slides" properties
2. Each slide has "type" and "fields" properties
3. The "fields" property contains only the fields allowed for that slide type, AND the "content" field, when present, MUST be a JSON array of strings."""
