"""Punto de entrada de la fase 6: corrección iterativa."""

import os

from dotenv import load_dotenv

from workflow import run_development_workflow


def main() -> None:
    """Ejecuta el ciclo de análisis, desarrollo, revisión y corrección."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Añádela al archivo .env antes de ejecutar el programa."
        )

    requirement = input("Describe el software que quieres crear: ").strip()
    if not requirement:
        print("No se recibió ningún requisito.")
        return

    result = run_development_workflow(requirement)

    print("\n--- Resultado del flujo de corrección ---\n")
    print(result.model_dump_json(indent=2, by_alias=True))


if __name__ == "__main__":
    main()
