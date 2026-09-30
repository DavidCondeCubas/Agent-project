"""Integración Git de solo lectura para los proyectos creados en workspace/."""

from __future__ import annotations

import subprocess

from agents import function_tool

from tools import WORKSPACE_ROOT, _shorten_output


def _run_git(*arguments: str) -> str:
    """Ejecuta una consulta Git sin shell y devuelve una salida acotada."""
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=WORKSPACE_ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        output = (completed.stdout + completed.stderr).strip()
        if completed.returncode != 0:
            return _shorten_output(
                "No hay un repositorio Git disponible en workspace/. "
                f"Detalle: {output or 'comando Git fallido.'}"
            )
        return _shorten_output(output or "(sin cambios que informar)")
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"No se pudo consultar Git: {error}"


@function_tool
def git_repository_status() -> str:
    """Consulta rama y cambios locales del repositorio Git en workspace/."""
    return _run_git("status", "--short", "--branch")


@function_tool
def git_diff_summary() -> str:
    """Resume los cambios sin confirmar y detecta errores de espacios con Git."""
    whitespace_errors = _run_git("diff", "--check")
    summary = _run_git("diff", "--stat")
    return f"Comprobación de espacios:\n{whitespace_errors}\n\nResumen del diff:\n{summary}"


@function_tool
def git_remote_info() -> str:
    """Muestra los remotos configurados, por ejemplo un remoto de GitHub."""
    return _run_git("remote", "-v")
