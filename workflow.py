"""Flujo de corrección iterativa de la fase 6."""

from agents import Runner

from agent import analyst_agent, developer_agent, reviewer_agent
from schemas import (
    CorrectionAttempt,
    ReviewStatus,
    WorkflowResult,
    WorkflowStatus,
)


MAX_AGENT_TURNS = 20
DEFAULT_MAX_CORRECTION_CYCLES = 2


def _development_prompt(
    requirement: str,
    analysis_json: str,
    review_json: str | None,
) -> str:
    prompt = f"""Requisito original:
{requirement}

Requisitos técnicos del Analyst Agent:
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


def _review_prompt(requirement: str, analysis_json: str, development_json: str) -> str:
    return f"""Requisito original:
{requirement}

Requisitos técnicos que deben cumplirse:
{analysis_json}

Resultado informado por el Developer Agent:
{development_json}

Revisa la implementación real dentro de workspace/ frente a esos requisitos.
"""


def run_development_workflow(
    requirement: str,
    max_correction_cycles: int = DEFAULT_MAX_CORRECTION_CYCLES,
) -> WorkflowResult:
    """Analiza, implementa y revisa hasta aprobar o alcanzar el límite."""
    if max_correction_cycles < 0:
        raise ValueError("max_correction_cycles no puede ser negativo.")

    analysis = Runner.run_sync(
        analyst_agent,
        requirement,
        max_turns=MAX_AGENT_TURNS,
    ).final_output
    analysis_json = analysis.model_dump_json(by_alias=True)
    attempts: list[CorrectionAttempt] = []
    previous_review_json: str | None = None

    for cycle in range(max_correction_cycles + 1):
        try:
            development = Runner.run_sync(
                developer_agent,
                _development_prompt(requirement, analysis_json, previous_review_json),
                max_turns=MAX_AGENT_TURNS,
            ).final_output
            review = Runner.run_sync(
                reviewer_agent,
                _review_prompt(
                    requirement,
                    analysis_json,
                    development.model_dump_json(by_alias=True),
                ),
                max_turns=MAX_AGENT_TURNS,
            ).final_output
        except Exception as error:
            return WorkflowResult(
                status=WorkflowStatus.ERROR,
                analysis=analysis,
                attempts=attempts,
                maxCorrectionCycles=max_correction_cycles,
                finalReview=attempts[-1].review if attempts else None,
                error=str(error),
            )

        attempts.append(
            CorrectionAttempt(cycle=cycle, development=development, review=review)
        )
        if review.status is ReviewStatus.APPROVED:
            return WorkflowResult(
                status=WorkflowStatus.APPROVED,
                analysis=analysis,
                attempts=attempts,
                maxCorrectionCycles=max_correction_cycles,
                finalReview=review,
            )

        previous_review_json = review.model_dump_json(by_alias=True)

    return WorkflowResult(
        status=WorkflowStatus.MAX_RETRIES_REACHED,
        analysis=analysis,
        attempts=attempts,
        maxCorrectionCycles=max_correction_cycles,
        finalReview=attempts[-1].review,
    )
