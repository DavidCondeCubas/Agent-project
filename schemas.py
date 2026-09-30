"""Esquemas que definen los datos producidos por los agentes."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SoftwareRequirement(BaseModel):
    """Plan técnico generado a partir de un requisito de software."""

    model_config = ConfigDict(populate_by_name=True)

    project_name: str = Field(alias="projectName")
    description: str
    requirements: list[str]
    technology_stack: list[str] = Field(alias="technologyStack")
    architecture: str
    entities: list[str]
    endpoints: list[str]
    implementation_steps: list[str] = Field(alias="implementationSteps")


class TechnicalRequirements(BaseModel):
    """Requisitos analizados antes de implementar una solución."""

    model_config = ConfigDict(populate_by_name=True)

    project_name: str = Field(alias="projectName")
    functional_requirements: list[str] = Field(alias="functionalRequirements")
    technical_requirements: list[str] = Field(alias="technicalRequirements")
    architecture: str
    entities: list[str]
    assumptions: list[str]


class DevelopmentResult(BaseModel):
    """Resultado verificable del trabajo realizado por el Developer Agent."""

    model_config = ConfigDict(populate_by_name=True)

    summary: str
    files_created_or_updated: list[str] = Field(alias="filesCreatedOrUpdated")
    commands_executed: list[str] = Field(alias="commandsExecuted")
    test_result: str = Field(alias="testResult")
    remaining_issues: list[str] = Field(alias="remainingIssues")


class ReviewStatus(StrEnum):
    APPROVED = "APPROVED"
    CHANGES_REQUIRED = "CHANGES_REQUIRED"


class ReviewResult(BaseModel):
    """Resultado de la revisión independiente de una implementación."""

    model_config = ConfigDict(populate_by_name=True)

    status: ReviewStatus
    problems: list[str]
    architecture_notes: list[str] = Field(alias="architectureNotes")
    security_notes: list[str] = Field(alias="securityNotes")
    test_notes: list[str] = Field(alias="testNotes")
    recommendations: list[str]


class OrchestrationResult(BaseModel):
    """Resultado de una pasada coordinada de análisis, desarrollo y revisión."""

    analysis: TechnicalRequirements
    development: DevelopmentResult
    review: ReviewResult


class WorkflowStatus(StrEnum):
    APPROVED = "APPROVED"
    MAX_RETRIES_REACHED = "MAX_RETRIES_REACHED"
    ERROR = "ERROR"


class CorrectionAttempt(BaseModel):
    """Una implementación seguida de su revisión."""

    cycle: int
    development: DevelopmentResult
    review: ReviewResult


class WorkflowResult(BaseModel):
    """Resultado del flujo con correcciones acotadas."""

    status: WorkflowStatus
    analysis: TechnicalRequirements
    attempts: list[CorrectionAttempt]
    max_correction_cycles: int = Field(alias="maxCorrectionCycles")
    final_review: ReviewResult | None = Field(alias="finalReview")
    workflow_id: str | None = Field(default=None, alias="workflowId")
    state_file: str | None = Field(default=None, alias="stateFile")
    error: str | None = None


class WorkflowState(BaseModel):
    """Memoria persistente y estructurada de una ejecución del workflow."""

    model_config = ConfigDict(populate_by_name=True)

    workflow_id: str = Field(alias="workflowId")
    user_requirement: str = Field(alias="userRequirement")
    technical_requirements: TechnicalRequirements | None = Field(default=None, alias="technicalRequirements")
    architecture_decision: str | None = Field(default=None, alias="architectureDecision")
    generated_files: list[str] = Field(default_factory=list, alias="generatedFiles")
    development_results: list[DevelopmentResult] = Field(default_factory=list, alias="developmentResults")
    review_results: list[ReviewResult] = Field(default_factory=list, alias="reviewResults")
    corrections: list[ReviewResult] = Field(default_factory=list)
    final_status: WorkflowStatus | None = Field(default=None, alias="finalStatus")
    error: str | None = None
