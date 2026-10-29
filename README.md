# 🎓 Udemy Transcripts Pro

> Centro de transcripción y estudio interactivo autónomo para cursos de Udemy. Convierte subtítulos y transcripciones de video en **Dashboards Web Interactivos (HTML autónomo con diagramas visuales y flashcards)**, **Markdown enriquecido (TOC interactivo)** y **Texto limpio**.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-chromium-green.svg)](https://playwright.dev/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security Audited](https://img.shields.io/badge/security-audited-success.svg)](https://github.com/)

---

## 🌟 Experiencia de Estudio Interactiva & Visual

A diferencia de las carpetas tradicionales con aburridos bloques de texto plano que fatigan al estudiante, **Udemy Transcripts Pro** transforma cada curso en una **plataforma de aprendizaje multimedia 100% offline**:

- 🌐 **Dashboard HTML Interactivo Autónomo (`index.html`):**
  - Funciona con doble clic en cualquier navegador (Chrome, Edge, Firefox, Safari) mediante `file://` **sin necesidad de levantar ningún servidor**.
  - 🎨 **Diseño Ergonómico Moderno:** Sin barras flotantes molestas; la navegación se integra fluidamente al final de cada lectura con tarjetas de siguiente/anterior y un botón de marcado de lección.
  - 🌐 **Investigación Autónoma en Fuentes Web (Sin APIs de IA):** Consulta Wikipedia REST API, DuckDuckGo y documentación oficial (MDN, Git SCM, Python Docs) trayendo resúmenes enciclopédicos, diagramas e imágenes reales de Wikimedia Commons de forma 100% gratuita y sin costo de tokens.
  - **📊 Diagramas Visuales y Mapas Conceptuales SVG:** Genera diagramas arquitectónicos y mapas de flujo automáticos según el tema de la lección (Git, Python, REST APIs, bases de datos SQL o pipelines de trabajo).
  - **💻 Detección Inteligente de Código y Comandos:** Extrae snippets de terminal (`git`, `docker`, `python`, `sql`) en cajas estilizadas de código con botón de 1-clic para copiar al portapapeles.
  - **🎯 Flashcards de Autoevaluación (Repaso Activo):** Tarjetas interactivas al final de cada lección para poner a prueba tu retención antes de pasar al siguiente tema.
  - **🎧 Lector de Voz Offline (TTS integrado):** Utiliza la API nativa de síntesis de voz de tu navegador con controles de reproducción, pausa y selector de velocidad para estudiar escuchando.
  - **🧘 Modo Enfoque (Zen Mode):** Presiona `F` para ocultar distracciones y centrar la lectura con un ancho óptimo de línea.
  - **⭐ Marcadores & Favoritos:** Guarda lecciones clave para repasarlas antes de entrevistas o proyectos.
  - **📝 Cuaderno de Notas Privado:** Bloc de notas por lección que se guarda en tu navegador y permite **exportar todas tus notas en un archivo Markdown**.
  - **🔍 Buscador en Tiempo Real con Debounce:** Encuentra cualquier lección o concepto al instante por palabra clave.

- 📝 **Markdown Enriquecido (`FULL_COURSE.md`):**
  - Índice con **Tabla de Contenidos interactiva** con anclas universales.
  - Tiempos de lectura estimados y conteo de palabras por lección.
  - Compatible con Obsidian, Notion, GitHub y editores Markdown.

- 🔄 **Conversor Local Inteligente (`--convert-local`):**
  - ¿Ya tenías cursos descargados en `.txt`? El conversor lee la carpeta con ordenación numérica natural y genera el **Dashboard HTML y Markdown en segundos**.

- 🔒 **Seguridad y Privacidad Garantizada:**
  - Sesiones y cookies se aíslan estrictamente en el perfil local de Chromium del sistema (`~/.cache`).
  - `.gitignore` blindado para evitar la filtración accidental de credenciales, tokens o material de cursos a repositorios públicos.
  - Protección XSS y saneamiento HTML en todas las vistas interactivas.

---

## 🚀 Instalación y Puesta en Marcha

### 1. Dependencias
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Ejecución

**Modo Interactivo (Recomendado):**
```bash
python udemy_transcripts.py
```
*(O doble clic en `run.bat` o en el acceso directo de escritorio).*

**Modo CLI Directo:**
```bash
# Descargar un curso por su URL o ID
udemy "https://www.udemy.com/course/mi-curso/"

# Listar tus cursos inscritos
udemy --list

# Convertir una carpeta de curso ya descargada a HTML interactivo y Markdown
udemy --convert-local "C:/Ruta/A/Mi-Curso"
```

---

## 🗂️ Estructura de Salida de un Curso

```text
Udemy-Transcripts/
└── The Git & Github Bootcamp/
    ├── index.html            # 🌐 Dashboard de Estudio Web Interactivo (Abrir en navegador)
    ├── course_data.js        # 📦 Base de datos estructurada local del curso
    ├── FULL_COURSE.md        # 📝 Markdown completo con Tabla de Contenidos navegable
    ├── 01 - Course Orientation/
    │   ├── 001 - Welcome To The Course!.txt
    │   └── ...
    └── 02 - Introducing...Git!/
        ├── 002 - What is Git.txt
        └── ...
```

---

## ⌨️ Opciones de Línea de Comandos

| Comando | Descripción |
| :--- | :--- |
| `udemy` | Abre el menú interactivo con tu lista de cursos inscritos |
| `udemy <URL o ID>` | Descarga el curso completo con HTML, Markdown y TXT |
| `--list` | Muestra la lista de cursos suscritos y sus IDs |
| `--convert-local <DIR>` | Convierte una carpeta existente a HTML interactivo y Markdown |
| `--txt` | Genera todo el curso en un único archivo `.txt` |
| `--timestamps` | Mantiene marcas de tiempo `[MM:SS]` en el texto |
| `--lang es,en` | Idiomas preferidos para subtítulos (default `es,en`) |
| `--out <DIR>` | Carpeta personalizada de salida |

---

## 🛡️ Uso Responsable y Legal

Este proyecto está diseñado exclusivamente para fines de **estudio e investigación personal**. Solo debes procesar cursos a los que tengas acceso legítimo en tu cuenta de Udemy. Respeta los derechos de autor de los instructores y las condiciones de servicio de las plataformas educativas.
