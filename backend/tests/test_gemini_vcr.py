import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import google.generativeai as genai
from typing import Dict, Any, Optional, Callable
from dotenv import load_dotenv
import traceback

class GeminiVCR:
    """
    A VCR-like class for recording and replaying Gemini API responses.
    This allows integration tests to run without actually calling the Gemini API.
    """
    def __init__(self, fixtures_dir: str = None):
        # Use absolute path for fixtures directory
        if fixtures_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.fixtures_dir = os.path.join(current_dir, "fixtures")
        else:
            self.fixtures_dir = fixtures_dir
            
        self.recordings: Dict[str, Any] = {}
        self.record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
        
        # Create fixtures directory if it doesn't exist
        print(f"Fixtures directory: {self.fixtures_dir}")
        print(f"Record mode: {self.record_mode}")
        os.makedirs(self.fixtures_dir, exist_ok=True)
    
    def get_fixture_path(self, name: str) -> str:
        """Get the path to a fixture file."""
        path = os.path.join(self.fixtures_dir, f"{name}.json")
        return path
    
    def save_recording(self, name: str, data: Dict[str, Any]) -> None:
        """Save a recording to a fixture file."""
        fixture_path = self.get_fixture_path(name)
        print(f"Attempting to save fixture to: {fixture_path}")
        try:
            with open(fixture_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Successfully saved fixture to: {fixture_path}")
            # Verify the file was created
            if os.path.exists(fixture_path):
                print(f"Verified file exists: {fixture_path}")
                print(f"File size: {os.path.getsize(fixture_path)} bytes")
            else:
                print(f"ERROR: File was not created: {fixture_path}")
        except Exception as e:
            print(f"ERROR saving fixture: {str(e)}")
            traceback.print_exc()
    
    def load_recording(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a recording from a fixture file."""
        fixture_path = self.get_fixture_path(name)
        if os.path.exists(fixture_path):
            print(f"Loading fixture from: {fixture_path}")
            with open(fixture_path, "r") as f:
                return json.load(f)
        return None
    
    def generate_fixture_name(self, args: Any, kwargs: Dict[str, Any]) -> str:
        """Generate a unique fixture name based on the function arguments."""
        # Create a deterministic fixture name based on the content of the arguments
        # This is a simple implementation that takes the first 50 chars of the first argument
        # and creates an MD5 hash of the full arguments
        import hashlib
        
        # Convert args and kwargs to a stable string representation
        args_str = str(args)
        kwargs_str = str(sorted(kwargs.items()))
        combined = args_str + kwargs_str
        
        # Generate a hash of the combined string
        hash_obj = hashlib.md5(combined.encode())
        hash_str = hash_obj.hexdigest()
        
        # Extract the first string argument (usually the prompt) if available
        prompt_prefix = ""
        if args and len(args) > 0:
            first_arg = args[0]
            if isinstance(first_arg, str) and first_arg:
                # Take first 30 chars of first word, removing special chars
                first_word = ''.join(c for c in first_arg.split()[0][:30] if c.isalnum())
                prompt_prefix = first_word.lower() + "_"
            elif isinstance(first_arg, list) and first_arg and isinstance(first_arg[0], dict) and "parts" in first_arg[0]:
                # Handle the case where the prompt is in a more complex structure
                for part in first_arg[0].get("parts", []):
                    if isinstance(part, dict) and "text" in part and part["text"]:
                        first_word = ''.join(c for c in part["text"].split()[0][:30] if c.isalnum())
                        prompt_prefix = first_word.lower() + "_"
                        break
        
        fixture_name = f"{prompt_prefix}{hash_str[:12]}"
        print(f"Generated fixture name: {fixture_name}")
        return fixture_name
    
    def mock_generate_content(self, original_func):
        """Create a mock for generate_content that records or replays responses."""
        def mock_wrapper(*args, **kwargs):
            # Debug print what we received
            print(f"DEBUG: generate_content called with args: {args} and kwargs: {kwargs}")
            
            # Handle different invocation patterns
            model_instance = None
            contents = None
            
            # Case 1: Standard case, args[0] is model instance, args[1] is contents
            if args and isinstance(args[0], genai.GenerativeModel):
                model_instance = args[0]
                if len(args) > 1:
                    contents = args[1]
                    print(f"DEBUG: Standard call pattern with model and contents")
            
            # Case 2: args[0] is a list of messages (happens in research_topic)
            elif args and isinstance(args[0], list) and all(isinstance(x, dict) for x in args[0]):
                model_instance = None  # not used in this case
                contents = args[0]
                print(f"DEBUG: Detected research_topic call pattern with message list")
            
            # Case 3: args[0] is a string (happens in slides.py)
            elif args and isinstance(args[0], str):
                model_instance = None  # not used in this case
                contents = args[0]
                print(f"DEBUG: Detected slides.py call pattern with string prompt")
            
            # Case 4: Using kwargs
            elif 'contents' in kwargs:
                model_instance = args[0] if args else None
                contents = kwargs['contents']
                print(f"DEBUG: Found contents in kwargs")
            
            # If still no contents, we have a problem
            if contents is None:
                print(f"DEBUG: Failed to find contents parameter. Args: {args}, Kwargs: {kwargs}")
                raise TypeError("No 'contents' parameter found in generate_content call")
                
            fixture_name = self.generate_fixture_name([contents], kwargs)
            
            # If we're in record mode, call the original function and save the response
            if self.record_mode:
                print(f"Recording Gemini API response to fixture: {fixture_name}")
                try:
                    # Call the original method with the appropriate arguments based on pattern
                    if model_instance is not None:
                        # Case 1: Standard pattern
                        if len(args) > 1:
                            response = original_func(model_instance, contents, **kwargs)
                        else:
                            response = original_func(model_instance, contents=contents, **kwargs)
                    elif isinstance(contents, str):
                        # Case 3: slides.py pattern - need to get the model from the frame
                        real_model = None
                        frame = sys._getframe(1)
                        while frame:
                            if 'model' in frame.f_locals and isinstance(frame.f_locals['model'], genai.GenerativeModel):
                                real_model = frame.f_locals['model']
                                break
                            frame = frame.f_back
                            
                        if real_model:
                            print(f"DEBUG: Found real model instance for string prompt")
                            response = original_func(real_model, contents, **kwargs)
                        else:
                            print(f"DEBUG: Creating new model for string prompt")
                            api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-testing")
                            genai.configure(api_key=api_key)
                            temp_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                            response = original_func(temp_model, contents, **kwargs)
                    else:
                        # Case 2: research_topic pattern
                        real_model = None
                        frame = sys._getframe(1)
                        while frame:
                            if 'model' in frame.f_locals and isinstance(frame.f_locals['model'], genai.GenerativeModel):
                                real_model = frame.f_locals['model']
                                break
                            frame = frame.f_back
                            
                        if real_model:
                            print(f"DEBUG: Found real model instance: {real_model}")
                            response = original_func(real_model, contents=contents, **kwargs)
                        else:
                            print(f"DEBUG: Creating new model for research_topic pattern")
                            api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-testing")
                            genai.configure(api_key=api_key)
                            temp_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                            response = original_func(temp_model, contents=contents, **kwargs)
                    
                    # Debug response
                    print(f"Response received, text length: {len(response.text)}")
                    
                    # Save the response text and attributes we care about
                    recording = {
                        "text": response.text,
                        "prompt": str(contents)
                    }
                    
                    self.save_recording(fixture_name, recording)
                    return response
                except Exception as e:
                    print(f"ERROR in API call: {str(e)}")
                    traceback.print_exc()
                    raise
            
            # If we're in replay mode, load the response from a fixture
            recording = self.load_recording(fixture_name)
            if recording:
                print(f"Replaying Gemini API response from fixture: {fixture_name}")
                mock_response = MagicMock()
                mock_response.text = recording["text"]
                return mock_response
            
            # If no fixture found, raise an error
            raise ValueError(
                f"No fixture found for Gemini API call: {fixture_name}\n"
                "Run tests with GEMINI_VCR_MODE=record to create fixtures."
            )
        
        return mock_wrapper
    
    def mock_generate_content_async(self, original_func):
        """Create a mock for generate_content_async that records or replays responses."""
        async def mock_wrapper(*args, **kwargs):
            # Debug print what we received
            print(f"DEBUG: generate_content_async called with args: {args} and kwargs: {kwargs}")
            
            # Handle different invocation patterns
            model_instance = None
            contents = None
            
            # Case 1: Standard case, args[0] is model instance, args[1] is contents
            if args and isinstance(args[0], genai.GenerativeModel):
                model_instance = args[0]
                if len(args) > 1:
                    contents = args[1]
                    print(f"DEBUG: Standard call pattern with model and contents")
            
            # Case 2: args[0] is a list of messages (happens in research_topic)
            elif args and isinstance(args[0], list) and all(isinstance(x, dict) for x in args[0]):
                model_instance = None  # not used in this case
                contents = args[0]
                print(f"DEBUG: Detected research_topic call pattern with message list")
            
            # Case 3: args[0] is a string (happens in slides.py)
            elif args and isinstance(args[0], str):
                model_instance = None  # not used in this case
                contents = args[0]
                print(f"DEBUG: Detected slides.py call pattern with string prompt")
            
            # Case 4: Using kwargs
            elif 'contents' in kwargs:
                model_instance = args[0] if args else None
                contents = kwargs['contents']
                print(f"DEBUG: Found contents in kwargs")
            
            # If still no contents, we have a problem
            if contents is None:
                print(f"DEBUG: Failed to find contents parameter. Args: {args}, Kwargs: {kwargs}")
                raise TypeError("No 'contents' parameter found in generate_content_async call")
                
            fixture_name = self.generate_fixture_name([contents], kwargs)
            
            # If we're in record mode, call the original function and save the response
            if self.record_mode:
                print(f"Recording Gemini API response to fixture: {fixture_name}")
                try:
                    # Call the original method with the appropriate arguments based on pattern
                    if model_instance is not None:
                        # Case 1: Standard pattern
                        if len(args) > 1:
                            response = await original_func(model_instance, contents, **kwargs)
                        else:
                            response = await original_func(model_instance, contents=contents, **kwargs)
                    elif isinstance(contents, str):
                        # Case 3: slides.py pattern - need to get the model from the frame
                        real_model = None
                        frame = sys._getframe(1)
                        while frame:
                            if 'model' in frame.f_locals and isinstance(frame.f_locals['model'], genai.GenerativeModel):
                                real_model = frame.f_locals['model']
                                break
                            frame = frame.f_back
                            
                        if real_model:
                            print(f"DEBUG: Found real model instance for string prompt")
                            response = await original_func(real_model, contents, **kwargs)
                        else:
                            print(f"DEBUG: Creating new model for string prompt")
                            api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-testing")
                            genai.configure(api_key=api_key)
                            temp_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                            response = await original_func(temp_model, contents, **kwargs)
                    else:
                        # Case 2: research_topic pattern
                        real_model = None
                        frame = sys._getframe(1)
                        while frame:
                            if 'model' in frame.f_locals and isinstance(frame.f_locals['model'], genai.GenerativeModel):
                                real_model = frame.f_locals['model']
                                break
                            frame = frame.f_back
                            
                        if real_model:
                            print(f"DEBUG: Found real model instance: {real_model}")
                            response = await original_func(real_model, contents=contents, **kwargs)
                        else:
                            print(f"DEBUG: Creating new model for research_topic pattern")
                            api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-testing")
                            genai.configure(api_key=api_key)
                            temp_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                            response = await original_func(temp_model, contents=contents, **kwargs)
                    
                    # Debug response
                    print(f"Response received, text length: {len(response.text)}")
                    
                    # Save the response text and attributes we care about
                    recording = {
                        "text": response.text,
                        "prompt": str(contents)
                    }
                    
                    self.save_recording(fixture_name, recording)
                    return response
                except Exception as e:
                    print(f"ERROR in API call: {str(e)}")
                    traceback.print_exc()
                    raise
            
            # If we're in replay mode, load the response from a fixture
            recording = self.load_recording(fixture_name)
            if recording:
                print(f"Replaying Gemini API response from fixture: {fixture_name}")
                mock_response = MagicMock()
                mock_response.text = recording["text"]
                return mock_response
            
            # If no fixture found, raise an error
            raise ValueError(
                f"No fixture found for Gemini API call: {fixture_name}\n"
                "Run tests with GEMINI_VCR_MODE=record to create fixtures."
            )
        
        return mock_wrapper


@pytest.fixture
def gemini_vcr():
    """Pytest fixture that provides a GeminiVCR instance."""
    vcr = GeminiVCR()
    # Make sure methods are directly accessible on the returned object
    vcr.mock_generate_content_async = vcr.mock_generate_content_async
    vcr.mock_generate_content = vcr.mock_generate_content
    return vcr


@pytest.fixture
def mock_gemini_api():
    """
    Patch the Gemini API key and config for testing.
    This avoids the need for a real API key in test environments.
    """
    # Create environment patch for API key if not in recording mode
    record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
    print(f"mock_gemini_api: record_mode = {record_mode}")
    
    if record_mode:
        # In record mode, we need the real API key
        # If GEMINI_API_KEY isn't explicitly set, try to load from .env file
        if not os.environ.get("GEMINI_API_KEY"):
            print("Loading API key from .env file for recording mode")
            load_dotenv()
            
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is required for recording mode")
            
        # No patching, just configure with the real API key
        key = os.environ.get("GEMINI_API_KEY")
        print(f"Configuring Gemini with API key (length: {len(key)})")
        genai.configure(api_key=key)
        yield
    else:
        # In replay mode, use fake key and mock the configure function
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-api-key-for-testing"}):
            with patch('google.generativeai.configure') as mock_configure:
                mock_configure.return_value = None
                yield


@pytest.fixture
def mock_gemini_responses(gemini_vcr, mock_gemini_api):
    """
    Pytest fixture that patches genai.GenerativeModel.generate_content_async
    and generate_content to record or replay responses.
    """
    record_mode = os.environ.get("GEMINI_VCR_MODE", "replay") == "record"
    print(f"mock_gemini_responses: record_mode = {record_mode}")
    
    # Create patchers for both methods
    async_patcher = patch.object(
        genai.GenerativeModel,
        'generate_content_async',
        side_effect=gemini_vcr.mock_generate_content_async(
            genai.GenerativeModel.generate_content_async
        )
    )
    
    sync_patcher = patch.object(
        genai.GenerativeModel,
        'generate_content',
        side_effect=gemini_vcr.mock_generate_content(
            genai.GenerativeModel.generate_content
        )
    )
    
    # Start the patchers
    async_patcher.start()
    sync_patcher.start()
    
    # Yield control back to the test
    yield gemini_vcr
    
    # Stop the patchers
    async_patcher.stop()
    sync_patcher.stop() 