#!/bin/bash

# Test the image generation API using curl

# Check if the API server is running on port 8000
if ! nc -z localhost 8000 &>/dev/null; then
    echo "ERROR: API server not running on port 8000."
    echo "Please start the API server with 'python run_api.py' first."
    exit 1
fi

# Create a test prompt
PROMPT="Create a professional business image showing data visualization and analytics for a presentation"

# Make the API request
echo "Sending request to generate image..."
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"size\": \"1024x1024\"}" \
    http://localhost:8000/images)

# Check if the request was successful
if [[ $RESPONSE == *"error"* ]]; then
    echo "Error in response:"
    echo $RESPONSE
    exit 1
fi

# Extract the base64 image from the response
echo "Extracting image data..."
IMAGE_DATA=$(echo $RESPONSE | python3 -c "import json, sys; print(json.load(sys.stdin)['image'])")

# Decode the base64 image and save to file
echo "Saving image to curl_test_image.png..."
echo $IMAGE_DATA | base64 -d > curl_test_image.png

echo "Image saved to curl_test_image.png"
echo "Test completed successfully." 