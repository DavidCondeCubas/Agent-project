"""Herramientas locales disponibles para el agente de la fase 3.

Todas trabajan dentro de ``workspace/``. Este límite evita que una petición del
agente modifique el código que lo ejecuta, aunque no reemplaza un sandbox real.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

from agents import function_tool


WORKSPACE_ROOT = (Path(__file__).parent / "workspace").resolve()
MAX_OUTPUT_LENGTH = 12_000


def _workspace_path(relative_path: str) -> Path:
    """Devuelve una ruta segura dentro del directorio de trabajo del agente."""
    candidate = (WORKSPACE_ROOT / relative_path).resolve()
    if not candidate.is_relative_to(WORKSPACE_ROOT):
        raise ValueError("La ruta debe estar dentro del directorio workspace.")
    return candidate


def _shorten_output(output: str) -> str:
    if len(output) <= MAX_OUTPUT_LENGTH:
        return output
    return f"{output[:MAX_OUTPUT_LENGTH]}\n... salida truncada ..."


def _command_arguments(command: str) -> list[str]:
    """Convierte un comando en argumentos y conserva el entorno virtual activo."""
    arguments = shlex.split(command)
    if not arguments:
        raise ValueError("El comando no puede estar vacío.")
    if arguments[0] in {"python", "python3"}:
        arguments[0] = sys.executable
    elif arguments[0] in {"pip", "pip3"}:
        arguments = [sys.executable, "-m", "pip", *arguments[1:]]
    return arguments


@function_tool
def read_file(path: str) -> str:
    """Lee un archivo de texto existente dentro de workspace.

    Args:
        path: Ruta relativa al directorio workspace.
    """
    try:
        file_path = _workspace_path(path)
        if not file_path.is_file():
            return f"Error: no existe un archivo en {path!r}."
        return _shorten_output(file_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return f"Error al leer {path!r}: {error}"


@function_tool
def write_file(path: str, content: str) -> str:
    """Crea o reemplaza un archivo de texto dentro de workspace.

    El directorio padre debe existir; usa create_directory antes si es necesario.

    Args:
        path: Ruta relativa al directorio workspace.
        content: Contenido completo que se escribirá en el archivo.
    """
    try:
        file_path = _workspace_path(path)
        if not file_path.parent.is_dir():
            return f"Error: el directorio padre de {path!r} no existe."
        file_path.write_text(content, encoding="utf-8")
        return f"Archivo escrito: {path}"
    except (OSError, ValueError) as error:
        return f"Error al escribir {path!r}: {error}"


@function_tool
def create_directory(path: str) -> str:
    """Crea un directorio, incluidos sus directorios padre, dentro de workspace.

    Args:
        path: Ruta relativa al directorio workspace.
    """
    try:
        directory_path = _workspace_path(path)
        directory_path.mkdir(parents=True, exist_ok=True)
        return f"Directorio disponible: {path}"
    except (OSError, ValueError) as error:
        return f"Error al crear el directorio {path!r}: {error}"


@function_tool
def execute_command(command: str) -> str:
    """Ejecuta un comando sin shell desde workspace y devuelve su salida.

    Args:
        command: Comando y argumentos, por ejemplo ``python -m unittest``.
    """
    try:
        WORKSPACE_ROOT.mkdir(exist_ok=True)
        completed = subprocess.run(
            _command_arguments(command),
            cwd=WORKSPACE_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        output = (completed.stdout + completed.stderr).strip()
        return _shorten_output(
            f"Código de salida: {completed.returncode}\n{output or '(sin salida)'}"
        )
    except (OSError, ValueError) as error:
        return f"Error al ejecutar el comando: {error}"
    except subprocess.TimeoutExpired:
        return "Error: el comando superó el límite de 30 segundos."


@function_tool
def run_tests(path: str = ".") -> str:
    """Ejecuta los tests de un proyecto dentro de workspace.

    Si el proyecto declara pytest en requirements.txt, usa pytest; en otro caso,
    usa el descubrimiento estándar de unittest.

    Args:
        path: Directorio del proyecto relativo a workspace.
    """
    try:
        project_path = _workspace_path(path)
        if not project_path.is_dir():
            return f"Error: no existe un directorio de proyecto en {path!r}."

        requirements_path = project_path / "requirements.txt"
        uses_pytest = (
            requirements_path.is_file()
            and "pytest" in requirements_path.read_text(encoding="utf-8").lower()
        )
        command = (
            [sys.executable, "-m", "pytest"]
            if uses_pytest
            else [sys.executable, "-m", "unittest", "discover"]
        )
        completed = subprocess.run(
            command,
            cwd=project_path,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        output = (completed.stdout + completed.stderr).strip()
        if "Ran 0 tests" in output or "no tests ran" in output.lower():
            output += "\nAdvertencia: no se descubrieron tests."
        return _shorten_output(
            f"Código de salida: {completed.returncode}\n{output or '(sin salida)'}"
        )
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return f"Error al ejecutar los tests: {error}"
    except subprocess.TimeoutExpired:
        return "Error: los tests superaron el límite de 30 segundos."
