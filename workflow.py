"""Workflow de la fase 7: correcciones con estado persistente y contexto selectivo."""

from uuid import uuid4

from agents import Runner

from agent import analyst_agent, developer_agent, reviewer_agent
from schemas import (
    CorrectionAttempt,
    ReviewResult,
    ReviewStatus,
    WorkflowResult,
    WorkflowState,
    WorkflowStatus,
)
from state import WorkflowStateStore


MAX_AGENT_TURNS = 20
DEFAULT_MAX_CORRECTION_CYCLES = 2


def _development_prompt(analysis_json: str, review_json: str | None) -> str:
    """Envía al Developer solo requisitos y, si procede, feedback accionable."""
    prompt = f"""Requisitos técnicos del Analyst Agent:
{analysis_json}
"""
    if review_json is None:
        return f"{prompt}\nImplementa la primera versión de la solución."
    return f"""{prompt}
Comentarios del Reviewer Agent de la iteración anterior:
{review_json}

Corrige todos los problemas concretos indicados por el revisor y vuelve a
ejecutar los tests. No elimines requisitos que ya estuvieran satisfechos.
"""


def _review_prompt(analysis_json: str, development_json: str) -> str:
    """Envía al Reviewer requisitos y la implementación actual, sin historial completo."""
    return f"""Requisitos técnicos que deben cumplirse:
{analysis_json}

Resultado informado por el Developer Agent:
{development_json}

Revisa la implementación real dentro de workspace/ frente a esos requisitos.
"""


def _result(
    status: WorkflowStatus,
    state: WorkflowState,
    state_file: str,
    attempts: list[CorrectionAttempt],
    max_correction_cycles: int,
    final_review: ReviewResult | None = None,
    error: str | None = None,
) -> WorkflowResult:
    return WorkflowResult(
        status=status,
        analysis=state.technical_requirements,
        attempts=attempts,
        maxCorrectionCycles=max_correction_cycles,
        finalReview=final_review,
        workflowId=state.workflow_id,
        stateFile=state_file,
        error=error,
    )


def run_development_workflow(
    requirement: str,
    max_correction_cycles: int = DEFAULT_MAX_CORRECTION_CYCLES,
    state_store: WorkflowStateStore | None = None,
) -> WorkflowResult:
    """Analiza, implementa y revisa guardando memoria tras cada transición."""
    if max_correction_cycles < 0:
        raise ValueError("max_correction_cycles no puede ser negativo.")

    store = state_store or WorkflowStateStore()
    state = WorkflowState(workflowId=uuid4().hex, userRequirement=requirement)
    state_file = str(store.save(state))

    try:
        analysis = Runner.run_sync(
            analyst_agent,
            requirement,
            max_turns=MAX_AGENT_TURNS,
        ).final_output
    except Exception as error:
        state.final_status = WorkflowStatus.ERROR
        state.error = str(error)
        store.save(state)
        raise RuntimeError(f"El Analyst Agent no pudo completar el análisis: {error}") from error

    state.technical_requirements = analysis
    state.architecture_decision = analysis.architecture
    state_file = str(store.save(state))
    analysis_json = analysis.model_dump_json(by_alias=True)
    attempts: list[CorrectionAttempt] = []
    previous_review_json: str | None = None

    for cycle in range(max_correction_cycles + 1):
        try:
            development = Runner.run_sync(
                developer_agent,
                _development_prompt(analysis_json, previous_review_json),
                max_turns=MAX_AGENT_TURNS,
            ).final_output
            state.development_results.append(development)
            state.generated_files = list(
                dict.fromkeys([*state.generated_files, *development.files_created_or_updated])
            )
            state_file = str(store.save(state))

            review = Runner.run_sync(
                reviewer_agent,
                _review_prompt(
                    analysis_json,
                    development.model_dump_json(by_alias=True),
                ),
                max_turns=MAX_AGENT_TURNS,
            ).final_output
        except Exception as error:
            state.final_status = WorkflowStatus.ERROR
            state.error = str(error)
            state_file = str(store.save(state))
            return _result(
                WorkflowStatus.ERROR,
                state,
                state_file,
                attempts,
                max_correction_cycles,
                attempts[-1].review if attempts else None,
                str(error),
            )

        attempts.append(CorrectionAttempt(cycle=cycle, development=development, review=review))
        state.review_results.append(review)
        if review.status is ReviewStatus.CHANGES_REQUIRED:
            state.corrections.append(review)
        state_file = str(store.save(state))

        if review.status is ReviewStatus.APPROVED:
            state.final_status = WorkflowStatus.APPROVED
            state_file = str(store.save(state))
            return _result(
                WorkflowStatus.APPROVED,
                state,
                state_file,
                attempts,
                max_correction_cycles,
                review,
            )

        previous_review_json = review.model_dump_json(by_alias=True)

    state.final_status = WorkflowStatus.MAX_RETRIES_REACHED
    state_file = str(store.save(state))
    return _result(
        WorkflowStatus.MAX_RETRIES_REACHED,
        state,
        state_file,
        attempts,
        max_correction_cycles,
        attempts[-1].review,
    )
