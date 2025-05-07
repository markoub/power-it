#!/usr/bin/env python3

import unittest
import asyncio

# Import orchestrator only - we're not testing the individual tools directly
from orchestrator import create_presentation

class TestPresentationTools(unittest.TestCase):
    """Test suite for presentation tools"""

    def test_orchestrator(self):
        """
        Test that the create_presentation function can be imported.
        This is a basic 'smoke test' to ensure the code structure works.
        """
        # Just testing that we can import the function
        self.assertTrue(callable(create_presentation))
        
        # Verify the function has the expected signature
        import inspect
        sig = inspect.signature(create_presentation)
        parameters = list(sig.parameters.keys())
        self.assertEqual(parameters, ['topic', 'target_slides'])
        
        # Verify default value for target_slides
        self.assertEqual(sig.parameters['target_slides'].default, 10)

if __name__ == "__main__":
    unittest.main() 