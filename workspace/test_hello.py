import unittest

from hello import greeting


class GreetingTestCase(unittest.TestCase):
    def test_greeting_returns_exact_text(self):
        self.assertEqual(greeting(), "Hola Mundo")


if __name__ == "__main__":
    unittest.main()
