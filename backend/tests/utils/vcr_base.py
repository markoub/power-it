"""Base VCR (Video Cassette Recorder) class for API mocking in tests."""

import json
import os
import hashlib
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from pathlib import Path


class BaseVCR(ABC):
    """
    Base class for VCR (Video Cassette Recorder) implementations.
    
    This class provides common functionality for recording and replaying API responses
    in tests, allowing tests to run without making actual API calls.
    """
    
    def __init__(self, api_name: str, fixtures_dir: Optional[str] = None):
        """
        Initialize BaseVCR.
        
        Args:
            api_name: Name of the API (e.g., 'gemini', 'openai')
            fixtures_dir: Directory to store fixtures (defaults to tests/fixtures/<api_name>)
        """
        self.api_name = api_name
        self.env_var = f"{api_name.upper()}_VCR_MODE"
        
        # Set up fixtures directory
        if fixtures_dir is None:
            tests_dir = Path(__file__).parent.parent
            self.fixtures_dir = tests_dir / "fixtures" / api_name.lower()
        else:
            self.fixtures_dir = Path(fixtures_dir)
        
        # Create fixtures directory if it doesn't exist
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine if we're in record or replay mode
        self.record_mode = os.environ.get(self.env_var, "replay") == "record"
        
        # Track recorded fixtures for debugging
        self._recorded_fixtures = []
        self._replayed_fixtures = []
    
    def get_fixture_path(self, name: str) -> Path:
        """Get the path for a fixture file."""
        return self.fixtures_dir / f"{name}.json"
    
    def generate_fixture_name(self, identifier: str, data: Any) -> str:
        """
        Generate a deterministic fixture name based on identifier and data.
        
        Args:
            identifier: Base identifier for the fixture
            data: Data to include in hash (will be converted to string)
            
        Returns:
            A deterministic fixture name
        """
        # Create a hash of the identifier and data
        combined = f"{identifier}_{str(data)}"
        hash_str = hashlib.md5(combined.encode()).hexdigest()
        
        # Create a readable prefix from the identifier
        prefix = ''.join(c for c in identifier.split()[0][:20] if c.isalnum()).lower()
        
        return f"{prefix}_{hash_str[:12]}"
    
    def save_recording(self, name: str, data: Dict[str, Any]) -> None:
        """
        Save a recording to a fixture file.
        
        Args:
            name: Name of the fixture
            data: Data to save
        """
        fixture_path = self.get_fixture_path(name)
        
        # Add metadata
        data["_metadata"] = {
            "api": self.api_name,
            "recorded_at": __import__("datetime").datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(fixture_path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        
        self._recorded_fixtures.append(str(fixture_path))
        
        if hasattr(self, '_debug') and self._debug:
            print(f"[VCR] Recorded fixture: {fixture_path}")
    
    def load_recording(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a recording from a fixture file.
        
        Args:
            name: Name of the fixture
            
        Returns:
            The loaded data or None if file doesn't exist
        """
        fixture_path = self.get_fixture_path(name)
        
        if not fixture_path.exists():
            return None
        
        try:
            with open(fixture_path, "r") as f:
                data = json.load(f)
            
            self._replayed_fixtures.append(str(fixture_path))
            
            if hasattr(self, '_debug') and self._debug:
                print(f"[VCR] Replayed fixture: {fixture_path}")
            
            return data
        except Exception as e:
            print(f"[VCR] Error loading fixture {fixture_path}: {e}")
            return None
    
    def record_or_replay(self, name: str, api_call: Callable, 
                        response_processor: Optional[Callable] = None) -> Any:
        """
        Record or replay an API call based on the current mode.
        
        Args:
            name: Name for the fixture
            api_call: Function that makes the actual API call
            response_processor: Optional function to process the response before saving
            
        Returns:
            The API response (either real or mocked)
        """
        if self.record_mode:
            # Make the actual API call
            response = api_call()
            
            # Process response if processor provided
            data_to_save = response_processor(response) if response_processor else response
            
            # Save the recording
            self.save_recording(name, data_to_save)
            
            return response
        else:
            # Load and return the recording
            recording = self.load_recording(name)
            
            if recording is None:
                raise FileNotFoundError(
                    f"No fixture found for '{name}' in {self.fixtures_dir}. "
                    f"Run with {self.env_var}=record to create it."
                )
            
            # Create mock response from recording
            return self.create_mock_response(recording)
    
    @abstractmethod
    def create_mock_response(self, recording: Dict[str, Any]) -> Any:
        """
        Create an API-specific mock response from a recording.
        
        This method must be implemented by subclasses to create the appropriate
        mock response object for their specific API.
        
        Args:
            recording: The loaded recording data
            
        Returns:
            A mock response object appropriate for the API
        """
        pass
    
    def cleanup_old_fixtures(self, days: int = 30) -> int:
        """
        Clean up fixtures older than the specified number of days.
        
        Args:
            days: Number of days to keep fixtures
            
        Returns:
            Number of fixtures deleted
        """
        import datetime
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        deleted_count = 0
        
        for fixture_path in self.fixtures_dir.glob("*.json"):
            try:
                # Check file modification time
                mtime = datetime.datetime.fromtimestamp(fixture_path.stat().st_mtime)
                if mtime < cutoff_date:
                    fixture_path.unlink()
                    deleted_count += 1
            except Exception as e:
                print(f"[VCR] Error checking/deleting {fixture_path}: {e}")
        
        return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about VCR usage."""
        return {
            "api": self.api_name,
            "mode": "record" if self.record_mode else "replay",
            "fixtures_dir": str(self.fixtures_dir),
            "recorded_fixtures": len(self._recorded_fixtures),
            "replayed_fixtures": len(self._replayed_fixtures),
            "total_fixtures": len(list(self.fixtures_dir.glob("*.json")))
        }