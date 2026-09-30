"""Agentes especializados de la fase 4."""

from agents import Agent

from schemas import (
    DevelopmentResult,
    OrchestrationResult,
    ReviewResult,
    TechnicalRequirements,
)
from tools import (
    create_directory,
    execute_command,
    read_file,
    run_tests,
    write_file,
)


analyst_agent = Agent(
    name="Analyst Agent",
    instructions="""
    Analiza el requisito de software que proporciona el usuario y conviértelo
    en requisitos funcionales y técnicos claros. Define una decisión de
    arquitectura breve y proporcional al requisito, identifica las entidades y
    declara los supuestos necesarios. No escribas código, no crees archivos,
    no ejecutes comandos y no propongas una implementación detallada.
    """.strip(),
    output_type=TechnicalRequirements,
)


developer_agent = Agent(
    name="Developer Agent",
    instructions="""
    Implementa la solución a partir de los requisitos técnicos que te entrega
    el usuario (normalmente la salida del Analyst Agent). Usa las herramientas
    para crear la estructura, el código, la configuración, las dependencias y
    los tests. Trabaja solo en workspace/. Lee los archivos antes de
    reemplazarlos, crea directorios antes de escribir y ejecuta los tests en la
    ruta concreta del proyecto al finalizar. No revises tu propia solución:
    informa de los hechos y deja la revisión al Reviewer Agent.
    """.strip(),
    output_type=DevelopmentResult,
    tools=[
        read_file,
        write_file,
        create_directory,
        execute_command,
        run_tests,
    ],
)


reviewer_agent = Agent(
    name="Reviewer Agent",
    instructions="""
    Revisa de forma independiente una implementación dentro de workspace/ y
    compárala con los requisitos que te entregue el usuario. Lee el código y
    ejecuta los tests cuando sea posible. Busca requisitos ausentes, bugs,
    problemas de arquitectura, calidad, seguridad y cobertura de tests. No
    modifiques archivos ni corrijas problemas: devuelve APPROVED solo si no
    encuentras problemas relevantes; de lo contrario, CHANGES_REQUIRED con
    problemas concretos y accionables.
    """.strip(),
    output_type=ReviewResult,
    tools=[read_file, execute_command, run_tests],
)


orchestrator_agent = Agent(
    name="Orchestrator Agent",
    instructions="""
    Coordina una única pasada del flujo de desarrollo de software. Conservas la
    conversación con el usuario y debes delegar en este orden:

    1. Llama a analyze_requirement con la petición original para obtener los
       requisitos técnicos.
    2. Llama a implement_solution y pásale los requisitos obtenidos. El
       Developer Agent debe implementar el proyecto en workspace/.
    3. Llama a review_implementation y pásale tanto los requisitos como el
       resultado del desarrollo. El Reviewer Agent debe revisar el proyecto.

    Usa las salidas reales de cada especialista como contexto del siguiente.
    Devuelve un resultado estructurado que incluya las tres salidas, sin
    inventar archivos, comandos ni resultados de tests. Si el revisor devuelve
    CHANGES_REQUIRED, informa los hallazgos pero no pidas correcciones al
    desarrollador todavía: el ciclo de corrección se introducirá en la fase 6.
    """.strip(),
    output_type=OrchestrationResult,
    tools=[
        analyst_agent.as_tool(
            tool_name="analyze_requirement",
            tool_description="Analiza una petición y devuelve requisitos técnicos estructurados.",
        ),
        developer_agent.as_tool(
            tool_name="implement_solution",
            tool_description="Implementa requisitos técnicos dentro de workspace/.",
        ),
        reviewer_agent.as_tool(
            tool_name="review_implementation",
            tool_description="Revisa una implementación frente a sus requisitos técnicos.",
        ),
    ],
)
