from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from schemas import (
    DevelopmentResult,
    ReviewResult,
    ReviewStatus,
    TechnicalRequirements,
    WorkflowStatus,
)
from workflow import run_development_workflow
from state import WorkflowStateStore


def analysis() -> TechnicalRequirements:
    return TechnicalRequirements(
        projectName="Books API",
        functionalRequirements=["Crear libros"],
        technicalRequirements=["Incluir tests"],
        architecture="API Flask con almacenamiento en memoria.",
        entities=["Book"],
        assumptions=[],
    )


def development(summary: str) -> DevelopmentResult:
    return DevelopmentResult(
        summary=summary,
        filesCreatedOrUpdated=["books_api/app.py"],
        commandsExecuted=["python -m pytest"],
        testResult="tests ejecutados",
        remainingIssues=[],
    )


def review(status: ReviewStatus) -> ReviewResult:
    return ReviewResult(
        status=status,
        problems=[] if status is ReviewStatus.APPROVED else ["Falta validar el título"],
        architectureNotes=[],
        securityNotes=[],
        testNotes=[],
        recommendations=[],
    )


class WorkflowTests(TestCase):
    @patch("workflow.Runner.run_sync")
    def test_corrects_once_then_approves(self, run_sync) -> None:
        run_sync.side_effect = [
            SimpleNamespace(final_output=analysis()),
            SimpleNamespace(final_output=development("Primera versión")),
            SimpleNamespace(final_output=review(ReviewStatus.CHANGES_REQUIRED)),
            SimpleNamespace(final_output=development("Versión corregida")),
            SimpleNamespace(final_output=review(ReviewStatus.APPROVED)),
        ]

        with TemporaryDirectory() as directory:
            store = WorkflowStateStore(Path(directory))
            result = run_development_workflow("Crear una API de libros", state_store=store)
            saved_state = store.load(result.workflow_id)

        self.assertEqual(result.status, WorkflowStatus.APPROVED)
        self.assertEqual(len(result.attempts), 2)
        self.assertEqual(saved_state.final_status, WorkflowStatus.APPROVED)
        self.assertEqual(saved_state.architecture_decision, analysis().architecture)
        self.assertEqual(len(saved_state.corrections), 1)
        self.assertEqual(saved_state.generated_files, ["books_api/app.py"])
        second_developer_prompt = run_sync.call_args_list[3].args[1]
        self.assertIn("Comentarios del Reviewer Agent", second_developer_prompt)
        self.assertNotIn("Crear una API de libros", second_developer_prompt)

    @patch("workflow.Runner.run_sync")
    def test_stops_when_the_correction_limit_is_reached(self, run_sync) -> None:
        run_sync.side_effect = [
            SimpleNamespace(final_output=analysis()),
            SimpleNamespace(final_output=development("Primera versión")),
            SimpleNamespace(final_output=review(ReviewStatus.CHANGES_REQUIRED)),
            SimpleNamespace(final_output=development("Corrección")),
            SimpleNamespace(final_output=review(ReviewStatus.CHANGES_REQUIRED)),
        ]

        with TemporaryDirectory() as directory:
            result = run_development_workflow(
                "Crear una API de libros",
                max_correction_cycles=1,
                state_store=WorkflowStateStore(Path(directory)),
            )

        self.assertEqual(result.status, WorkflowStatus.MAX_RETRIES_REACHED)
        self.assertEqual(len(result.attempts), 2)
