"""Aplicación CLI mínima para mostrar un saludo."""


def greeting() -> str:
    """Devuelve el saludo fijo de la aplicación."""
    return "Hola Mundo"


def main() -> None:
    """Muestra el saludo en la salida estándar."""
    print(greeting())


if __name__ == "__main__":
    main()
