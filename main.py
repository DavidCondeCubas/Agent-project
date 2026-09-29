"""Punto de entrada de la fase 1: un agente que genera planes técnicos."""

import os

from agents import Runner
from dotenv import load_dotenv

from agent import software_engineering_agent


def main() -> None:
    """Pide un requisito al usuario y muestra el plan creado por el agente."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Añádela al archivo .env antes de ejecutar el programa."
        )

    requirement = input("Describe el software que quieres planificar: ").strip()
    if not requirement:
        print("No se recibió ningún requisito.")
        return

    result = Runner.run_sync(software_engineering_agent, requirement)

    print("\n--- Plan técnico ---\n")
    print(result.final_output)


if __name__ == "__main__":
    main()
