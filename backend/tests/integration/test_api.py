import requests
import json
import os

def test_run_pptx_step():
    """Test running the PPTX generation step for a presentation."""
    base_url = "http://localhost:8000"
    
    # First, get existing presentations to find one to generate
    response = requests.get(f"{base_url}/presentations")
    if not response.ok:
        print(f"Error getting presentations: {response.status_code}")
        print(response.text)
        return
    
    presentations = response.json()
    if not presentations:
        print("No presentations found")
        return
    
    # Use the first presentation or one with id 1
    presentation_id = None
    for p in presentations:
        if p.get("id") == 1:
            presentation_id = 1
            break
    
    if presentation_id is None and presentations:
        presentation_id = presentations[0].get("id")
    
    if presentation_id is None:
        print("Could not find a valid presentation ID")
        return
    
    print(f"Using presentation with ID: {presentation_id}")
    
    # Now trigger PowerPoint generation via the step endpoint
    step_name = "pptx"
    response = requests.post(f"{base_url}/presentations/{presentation_id}/steps/{step_name}/run")
    
    if not response.ok:
        print(f"Error running PPTX step: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    print(f"Step execution started:")
    print(json.dumps(result, indent=2))
    
    # Check the status of the step
    response = requests.get(f"{base_url}/presentations/{presentation_id}")
    if response.ok:
        pres_data = response.json()
        steps = pres_data.get("steps", [])
        pptx_step = next((s for s in steps if s.get("step") == "pptx"), None)
        
        if pptx_step:
            print(f"\nCurrent status of PPTX step: {pptx_step.get('status')}")
            if pptx_step.get("error_message"):
                print(f"Error message: {pptx_step.get('error_message')}")
        else:
            print("PPTX step not found in presentation data")

if __name__ == "__main__":
    test_run_pptx_step() 