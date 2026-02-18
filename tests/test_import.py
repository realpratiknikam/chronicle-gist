import unittest
from chronicle_gist import Chronicle

class TestChronicleImport(unittest.TestCase):
    def test_import_and_init(self):
        """Test that Chronicle can be imported and initialized with minimal args."""
        try:
            # Initialize with dummy internal components if possible, 
            # or just minimal args to pass validation.
            # Chronicle requires api_key (even if dummy) or handled by env.
            chronicle = Chronicle(api_key="dummy_key")
            self.assertIsInstance(chronicle, Chronicle)
        except Exception as e:
            self.fail(f"Chronicle instantiation failed: {e}")

if __name__ == '__main__':
    unittest.main()
