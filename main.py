"""Punto de entrada de la fase 4: agentes especializados."""

import os

from agents import Runner
from dotenv import load_dotenv

from agent import analyst_agent, developer_agent, reviewer_agent


SPECIALISTS = {
    "1": ("Analyst Agent", analyst_agent),
    "2": ("Developer Agent", developer_agent),
    "3": ("Reviewer Agent", reviewer_agent),
}


def main() -> None:
    """Ejecuta manualmente uno de los agentes especializados."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Añádela al archivo .env antes de ejecutar el programa."
        )

    print("\nSelecciona un especialista:")
    print("1. Analyst Agent — analiza y estructura requisitos")
    print("2. Developer Agent — implementa requisitos en workspace/")
    print("3. Reviewer Agent — revisa una implementación en workspace/")
    selection = input("Opción: ").strip()

    specialist = SPECIALISTS.get(selection)
    if specialist is None:
        print("Opción no válida.")
        return

    agent_name, selected_agent = specialist
    request = input(
        f"\nContexto para {agent_name} "
        "(pega aquí requisitos, una petición o la ruta del proyecto): "
    ).strip()
    if not request:
        print("No se recibió ningún contexto.")
        return

    result = Runner.run_sync(
        selected_agent,
        request,
        max_turns=20,
    )

    print(f"\n--- Resultado de {agent_name} ---\n")
    print(result.final_output.model_dump_json(indent=2, by_alias=True))


if __name__ == "__main__":
    main()
