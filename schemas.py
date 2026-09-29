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
