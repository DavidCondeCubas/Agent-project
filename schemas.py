"""Esquemas que definen los datos producidos por los agentes."""

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
