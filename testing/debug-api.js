// Simple script to test the presentations API

const testCreate = async () => {
  try {
    const backendPresentationData = {
      name: "Test Presentation from Debug",
      author: "Debug User",
      research_type: "research", 
      topic: "API Testing with JavaScript"
    };
    
    console.log('Sending presentation data to API:', JSON.stringify(backendPresentationData));
    
    const response = await fetch('http://localhost:8000/presentations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendPresentationData),
    });
    
    const responseText = await response.text();
    
    if (!response.ok) {
      console.error(`Server error ${response.status}: ${responseText}`);
      return;
    }
    
    try {
      const responseData = JSON.parse(responseText);
      console.log('Received response:', responseData);
    } catch (e) {
      console.log('Received non-JSON response:', responseText);
    }
  } catch (error) {
    console.error('Error in test:', error);
  }
};

// Run the test
testCreate(); 