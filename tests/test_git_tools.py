from unittest import TestCase
from unittest.mock import patch

import git_tools


class GitToolTests(TestCase):
    @patch("git_tools.subprocess.run")
    def test_git_status_uses_workspace_without_a_shell(self, run) -> None:
        run.return_value.stdout = "## main\n M app.py\n"
        run.return_value.stderr = ""
        run.return_value.returncode = 0

        output = git_tools._run_git("status", "--short", "--branch")

        self.assertEqual(output, "## main\n M app.py")
        run.assert_called_once_with(
            ["git", "status", "--short", "--branch"],
            cwd=git_tools.WORKSPACE_ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )

    @patch("git_tools.subprocess.run")
    def test_missing_repository_returns_an_explanation(self, run) -> None:
        run.return_value.stdout = ""
        run.return_value.stderr = "fatal: not a git repository"
        run.return_value.returncode = 128

        output = git_tools._run_git("status", "--short", "--branch")

        self.assertIn("No hay un repositorio Git", output)
