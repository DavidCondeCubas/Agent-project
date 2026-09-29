"""Punto de entrada de la fase 5: orquestación de agentes."""

import os

from agents import Runner
from dotenv import load_dotenv

from agent import orchestrator_agent


def main() -> None:
    """Coordina una pasada de análisis, desarrollo y revisión."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Añádela al archivo .env antes de ejecutar el programa."
        )

    requirement = input("Describe el software que quieres crear: ").strip()
    if not requirement:
        print("No se recibió ningún requisito.")
        return

    result = Runner.run_sync(
        orchestrator_agent,
        requirement,
        max_turns=20,
    )

    print("\n--- Resultado de la orquestación ---\n")
    print(result.final_output.model_dump_json(indent=2, by_alias=True))


if __name__ == "__main__":
    main()
