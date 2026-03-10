# Nivora

Asistente virtual de escritorio desarrollado como Trabajo de Fin de Grado (TFG) del ciclo DAM. Combina un chat con IA local y un sistema de macros para automatizar tareas del sistema.

## Características

- Chat con IA usando modelos locales (sin conexión a internet)
- Sistema de macros para ejecutar acciones automatizadas
- Interfaz gráfica de escritorio
- Ejecutable standalone para Windows

## Tecnologías

- **Python**
- **PyQt / Qt** — interfaz gráfica (`.qss` para estilos)
- **Ollama** — modelo de IA local (necesario tener ollama instalado con el modelo gemma3:4b descargado `ollana pull gemma3:4b`)
- **PyInstaller** — empaquetado como ejecutable

## Requisitos

- Python 3.x
- [Ollama](https://ollama.com/) instalado y en ejecución

## Instalación

```bash
git clone https://github.com/Alowster/Nivora.git
cd Nivora
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

O descarga el ejecutable desde la sección [Releases](https://github.com/Alowster/Nivora/releases).

## Estructura

```
Nivora/
├── core/         # Lógica del asistente y macros
├── ui/           # Componentes de interfaz
├── config.py     # Configuración general
├── styles.qss    # Estilos visuales
└── main.py       # Punto de entrada
```

## Autor

[Alowster](https://github.com/Alowster)
