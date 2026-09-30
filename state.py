"""Persistencia local de la memoria estructurada del workflow."""

from pathlib import Path

from schemas import WorkflowState


DEFAULT_STATE_DIRECTORY = Path(".agent_state")


class WorkflowStateStore:
    """Guarda cada estado como JSON para poder inspeccionarlo o reanudarlo."""

    def __init__(self, directory: Path | str = DEFAULT_STATE_DIRECTORY) -> None:
        self.directory = Path(directory)

    def path_for(self, workflow_id: str) -> Path:
        return self.directory / f"{workflow_id}.json"

    def save(self, state: WorkflowState) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.path_for(state.workflow_id)
        temporary = target.with_suffix(".tmp")
        temporary.write_text(state.model_dump_json(indent=2, by_alias=True), encoding="utf-8")
        temporary.replace(target)
        return target

    def load(self, workflow_id: str) -> WorkflowState:
        return WorkflowState.model_validate_json(self.path_for(workflow_id).read_text(encoding="utf-8"))
