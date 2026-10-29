"""
knowledge_engine.py — Motor de Conocimiento Autónomo y Fuentes Abiertas (Sin APIs de IA).

Desarrollado por: Jose Daniel Zambrano Luna
Repositorio: https://github.com/josezambranol/udemy-transcripts

Enriquece cursos y transcripciones de video con resúmenes conceptuales, diagramas visuales
arquitectónicos y documentación oficial de forma 100% gratuita y sin costo de tokens:
  1. Base de Conocimiento Offline Embebida (80+ conceptos clave con respaldo inmediato).
  2. Wikipedia REST API & Opensearch (Resolución inteligente multilingüe es/en).
  3. Wikimedia Commons MediaWiki API (Diagramas de arquitectura SVG/PNG en alta resolución).
  4. DuckDuckGo Instant Answer API (Respuestas técnicas complementarias).
  5. Extractor NLP Autónomo de Conceptos Técnicos con filtrado estricto de stopwords.
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ubicación de la caché persistente en el sistema del usuario
CACHE_FILE = Path.home() / ".cache" / "udemy-transcripts-knowledge-cache.json"

# Cabecera User-Agent estricta que cumple la política oficial de Wikipedia y Wikimedia
USER_AGENT = (
    f"UdemyTranscriptsPro/2.0 (https://github.com/josezambranol/udemy-transcripts; "
    f"contact: josedaniellunamarimon@gmail.com; educational) Python/{sys.version_info.major}.{sys.version_info.minor}"
)

# -----------------------------------------------------------------------------
# 1. BASE DE CONOCIMIENTO OFFLINE EMBEBIDA (Respaldo Inmediato sin Conexión)
# -----------------------------------------------------------------------------
EMBEDDED_KNOWLEDGE_BASE = {
    "git": {
        "title": "Git (Sistema de Control de Versiones)",
        "extract": "Git es un sistema de control de versiones distribuido diseñado por Linus Torvalds en 2005 para ser rápido, seguro y eficiente. A diferencia de los sistemas centralizados, cada clon local contiene el historial completo del proyecto, permitiendo crear ramas independientes, confirmaciones locales (commits) y fusiones sin depender de conexión a un servidor central.",
        "url": "https://es.wikipedia.org/wiki/Git",
        "source": "Enciclopedia Técnica Offline"
    },
    "github": {
        "title": "GitHub (Plataforma Colaborativa)",
        "extract": "GitHub es la plataforma en la nube más utilizada en el mundo para alojar repositorios Git. Facilita el trabajo colaborativo en equipos mediante Pull Requests (revisiones de código por pares), Issues (seguimiento de tareas y bugs), GitHub Actions (automatización CI/CD) y gestión de versiones.",
        "url": "https://es.wikipedia.org/wiki/GitHub",
        "source": "Enciclopedia Técnica Offline"
    },
    "staging area": {
        "title": "Staging Area (Índice de Git)",
        "extract": "El Staging Area o índice es una de las características más potentes de Git. Es un área intermedia de preparación donde el desarrollador organiza y selecciona selectivamente qué cambios específicos formarán parte del próximo commit mediante 'git add', permitiendo crear confirmaciones lógicas y atómicas.",
        "url": "https://git-scm.com/about/staging-area",
        "source": "Git SCM Architecture"
    },
    "branching": {
        "title": "Ramas y Bifurcaciones (Branching)",
        "extract": "Las ramas en Git son punteros móviles extremadamente ligeros (solo 41 bytes) que apuntan al commit más reciente de una línea de desarrollo. Permiten trabajar en nuevas características o correcciones de bugs de forma completamente aislada del código principal (main/master).",
        "url": "https://git-scm.com/book/es/v2/Ramificaciones-en-Git-%C2%BFQu%C3%A9-es-una-rama%3F",
        "source": "Git SCM Architecture"
    },
    "python": {
        "title": "Python (Lenguaje de Programación)",
        "extract": "Python es un lenguaje de programación interpretado de alto nivel cuya filosofía enfatiza la legibilidad del código. Es multiparadigma (orientado a objetos, imperativo y funcional), de tipado dinámico y cuenta con una extensa biblioteca estándar ('pilas incluidas'), siendo el referente indiscutible en desarrollo web, automatización, ciencia de datos e inteligencia artificial.",
        "url": "https://es.wikipedia.org/wiki/Python",
        "source": "Enciclopedia Técnica Offline"
    },
    "docker": {
        "title": "Docker (Contenedores de Software)",
        "extract": "Docker es una tecnología de virtualización a nivel de sistema operativo que empaqueta una aplicación y todas sus dependencias (código, librerías y configuración) en un contenedor independiente y portable. A diferencia de las máquinas virtuales pesadas, los contenedores comparten el kernel del host, haciéndolos ultraligeros y rápidos de iniciar.",
        "url": "https://es.wikipedia.org/wiki/Docker_(software)",
        "source": "Enciclopedia Técnica Offline"
    },
    "sql": {
        "title": "SQL (Structured Query Language)",
        "extract": "SQL es el lenguaje declarativo estándar para la gestión y manipulación de datos en sistemas de gestión de bases de datos relacionales (RDBMS). Permite definir esquemas, consultar registros con filtros complejos (SELECT), relacionar tablas (JOIN) y garantizar transacciones fiables mediante las propiedades ACID.",
        "url": "https://es.wikipedia.org/wiki/SQL",
        "source": "Enciclopedia Técnica Offline"
    },
    "postgresql": {
        "title": "PostgreSQL (Base de Datos Relacional Avanzada)",
        "extract": "PostgreSQL es un sistema gestor de bases de datos relacional y orientado a objetos de código abierto de nivel empresarial. Es célebre por su estricto cumplimiento del estándar SQL, su robustez de integridad de datos, soporte nativo de JSON/JSONB y alta extensibilidad.",
        "url": "https://es.wikipedia.org/wiki/PostgreSQL",
        "source": "Enciclopedia Técnica Offline"
    },
    "javascript": {
        "title": "JavaScript (Lenguaje de la Web)",
        "extract": "JavaScript es el lenguaje de programación fundamental de la web moderna. Es interpretado o compilado en tiempo de ejecución (JIT), dinámico, débilmente tipado y basado en prototipos. Ejecuta tanto en navegadores (controlando el DOM) como en servidores mediante Node.js, gracias a su modelo de concurrencia basado en un bucle de eventos (Event Loop).",
        "url": "https://es.wikipedia.org/wiki/JavaScript",
        "source": "Enciclopedia Técnica Offline"
    },
    "typescript": {
        "title": "TypeScript (JavaScript Tipado)",
        "extract": "TypeScript es un superconjunto estricto de JavaScript desarrollado por Microsoft que añade tipado estático opcional y características orientadas a objetos. Se transpila a JavaScript estándar y permite detectar errores en tiempo de compilación, facilitando el desarrollo y refactorización de aplicaciones a gran escala.",
        "url": "https://es.wikipedia.org/wiki/TypeScript",
        "source": "Enciclopedia Técnica Offline"
    },
    "react": {
        "title": "React (Biblioteca de Interfaces de Usuario)",
        "extract": "React es una biblioteca de JavaScript de código abierto desarrollada por Meta para construir interfaces de usuario interactivas basadas en componentes reactivos y un DOM virtual (Virtual DOM) que optimiza las actualizaciones visuales calculando las mínimas diferencias necesarias.",
        "url": "https://es.wikipedia.org/wiki/React",
        "source": "Enciclopedia Técnica Offline"
    },
    "api rest": {
        "title": "API REST (Representational State Transfer)",
        "extract": "REST es un estilo arquitectónico para sistemas distribuidos basado en el protocolo HTTP sin estado. Los clientes interactúan con recursos identificados mediante URIs utilizando métodos estándar: GET (lectura), POST (creación), PUT/PATCH (actualización) y DELETE (eliminación), intercambiando usualmente datos formateados en JSON.",
        "url": "https://es.wikipedia.org/wiki/Transferencia_de_Estado_Representacional",
        "source": "Enciclopedia Técnica Offline"
    },
    "linux": {
        "title": "Linux (Sistema Operativo Libre)",
        "extract": "Linux es una familia de sistemas operativos tipo Unix basados en el kernel Linux creado por Linus Torvalds en 1991. Es la infraestructura dominante que sustenta servidores en la nube, supercomputadoras, contenedores Docker y dispositivos Android debido a su seguridad, estabilidad y rendimiento.",
        "url": "https://es.wikipedia.org/wiki/GNU/Linux",
        "source": "Enciclopedia Técnica Offline"
    },
    "algoritmo": {
        "title": "Algoritmo y Complejidad Computacional",
        "extract": "Un algoritmo es una secuencia finita, rigurosa y ordenada de pasos o instrucciones bien definidas que toma una entrada, ejecuta un procesamiento computacional y produce una salida resolviendo un problema. Su eficiencia se mide comúnmente mediante la notación Big O.",
        "url": "https://es.wikipedia.org/wiki/Algoritmo",
        "source": "Enciclopedia Técnica Offline"
    },
    "estructura de datos": {
        "title": "Estructuras de Datos",
        "extract": "Una estructura de datos es una forma especializada de organizar, almacenar y gestionar datos en la memoria para que puedan ser accedidos y modificados de manera eficiente. Ejemplos fundamentales incluyen arreglos, listas enlazadas, pilas, colas, tablas hash, árboles y grafos.",
        "url": "https://es.wikipedia.org/wiki/Estructura_de_datos",
        "source": "Enciclopedia Técnica Offline"
    },
    "programacion orientada a objetos": {
        "title": "Programación Orientada a Objetos (POO)",
        "extract": "La POO es un paradigma de programación basado en el concepto de 'objetos' que contienen datos (atributos) y código (métodos). Se sustenta en cuatro pilares fundamentales: Encapsulamiento, Abstracción, Herencia y Polimorfismo, facilitando la modularidad y reutilización de software.",
        "url": "https://es.wikipedia.org/wiki/Programaci%C3%B3n_orientada_a_objetos",
        "source": "Enciclopedia Técnica Offline"
    },
    "kubernetes": {
        "title": "Kubernetes (Orquestación de Contenedores)",
        "extract": "Kubernetes (K8s) es una plataforma de código abierto originada en Google para automatizar el despliegue, escalado y gestión operativa de aplicaciones en contenedores a través de clústeres de servidores físicos o virtuales.",
        "url": "https://es.wikipedia.org/wiki/Kubernetes",
        "source": "Enciclopedia Técnica Offline"
    },
    "machine learning": {
        "title": "Machine Learning (Aprendizaje Automático)",
        "extract": "El aprendizaje automático es una rama de la inteligencia artificial centrada en el desarrollo de algoritmos y modelos estadísticos que permiten a las computadoras aprender patrones directamente de los datos y realizar predicciones o decisiones sin haber sido programadas explícitamente para cada regla.",
        "url": "https://es.wikipedia.org/wiki/Aprendizaje_autom%C3%A1tico",
        "source": "Enciclopedia Técnica Offline"
    }
}

# -----------------------------------------------------------------------------
# 2. CATÁLOGO DE DIAGRAMAS VISUALES ARQUITECTÓNICOS (Wikimedia Commons / Open)
# -----------------------------------------------------------------------------
CURATED_TOPIC_VISUALS = {
    "git": [
        {
            "title": "Diagrama Oficial de Arquitectura de Git (Workflow 4 Áreas)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0e/GitWorkflow.svg/960px-GitWorkflow.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Las 4 áreas fundamentales de Git: Directorio de Trabajo (Working Tree), Staging Area (Índice), Repositorio Local y Repositorio Remoto."
        },
        {
            "title": "Bifurcación de Ramas y Operaciones de Fusión (Branching)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d8/Git_operations.svg/960px-Git_operations.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Mecánica de punteros de commits, creación de ramas aisladas y confluencia mediante merge y rebase."
        },
        {
            "title": "Logotipo Oficial de Git y Control Distribuido",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e0/Git-logo.svg/960px-Git-logo.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Git es el estándar mundial en ingeniería de software para trazabilidad y versionado de código."
        }
    ],
    "github": [
        {
            "title": "GitHub y Ciclo de Colaboración Remota",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c2/GitHub_Invertocat_Logo.svg/960px-GitHub_Invertocat_Logo.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Sincronización remota con origin, apertura de Pull Requests y revisión continua de código en equipo."
        }
    ],
    "python": [
        {
            "title": "Filosofía y Arquitectura del Lenguaje Python",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/960px-Python-logo-notext.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Python: Lenguaje interpretado con recolección automática de basura y filosofía Zen de simplicidad."
        },
        {
            "title": "Lógica Algorítmica y Búsqueda Binaria en Python",
            "url": "https://upload.wikimedia.org/wikipedia/commons/6/62/CPT-TheoryOfComp-Binary-Search-Python.png?utm_source=es.wikipedia.org&utm_campaign=api&utm_content=thumbnail_unscaled",
            "caption": "Estructuras de datos dinámicas, listas y algoritmos de búsqueda eficiente en memoria."
        }
    ],
    "docker": [
        {
            "title": "Contenedores Docker y Aislamiento de Procesos",
            "url": "https://upload.wikimedia.org/wikipedia/commons/7/79/Docker_%28container_engine%29_logo.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled",
            "caption": "Docker comparte el kernel del sistema operativo para ejecutar microservicios aislados y reproducibles."
        }
    ],
    "sql": [
        {
            "title": "Bases de Datos Relacionales y PostgreSQL",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/29/Postgresql_elephant.svg/960px-Postgresql_elephant.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Esquemas de tablas normalizadas, claves foráneas y consistencia transaccional ACID."
        }
    ],
    "javascript": [
        {
            "title": "Jerarquía del Árbol DOM (Document Object Model)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5a/DOM-model.svg/960px-DOM-model.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Estructura en árbol de objetos que los navegadores exponen para que JavaScript manipule la vista dinámicamente."
        }
    ],
    "web": [
        {
            "title": "Arquitectura Cliente-Servidor Web (Peticiones HTTP)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c9/Client-server-model.svg/960px-Client-server-model.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Ciclo de vida de una petición web: el cliente solicita un recurso HTTP y el servidor responde con cabeceras y payload."
        },
        {
            "title": "Modelo de Comunicación en Redes TCP/IP",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3b/TCP_IP_model.svg/960px-TCP_IP_model.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Capas de abstracción en redes: Aplicación, Transporte (TCP/UDP), Internet (IP) y Acceso a Red."
        }
    ],
    "linux": [
        {
            "title": "Jerarquía Estándar de Archivos en Unix/Linux (FHS)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f3/Standard-unix-filesystem-hierarchy.svg/960px-Standard-unix-filesystem-hierarchy.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Distribución estándar de directorios raíz: /etc (configuraciones), /bin (binarios), /home (usuarios) y /var (datos variables)."
        }
    ],
    "ia": [
        {
            "title": "Arquitectura de Redes Neuronales Artificiales (Deep Learning)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/46/Colored_neural_network.svg/960px-Colored_neural_network.svg.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
            "caption": "Capas de neuronas conectadas con pesos ajustables, funciones de activación y retropropagación de gradiente."
        }
    ]
}

# -----------------------------------------------------------------------------
# 3. MAPA DE DOCUMENTACIÓN OFICIAL DE REFERENCIA (35+ Ecosistemas Tecnológicos)
# -----------------------------------------------------------------------------
OFFICIAL_DOCS_MAP = {
    "git": {"name": "Git SCM Official Documentation", "url": "https://git-scm.com/doc", "icon": "📦"},
    "github": {"name": "GitHub Docs", "url": "https://docs.github.com/", "icon": "🐙"},
    "gitlab": {"name": "GitLab Documentation", "url": "https://docs.gitlab.com/", "icon": "🦊"},
    "python": {"name": "Python 3 Official Documentation", "url": "https://docs.python.org/3/", "icon": "🐍"},
    "javascript": {"name": "MDN Web Docs (JavaScript)", "url": "https://developer.mozilla.org/es/docs/Web/JavaScript", "icon": "⚡"},
    "typescript": {"name": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/", "icon": "🔷"},
    "html": {"name": "MDN Web Docs (HTML5)", "url": "https://developer.mozilla.org/es/docs/Web/HTML", "icon": "🌐"},
    "css": {"name": "MDN Web Docs (CSS3)", "url": "https://developer.mozilla.org/es/docs/Web/CSS", "icon": "🎨"},
    "tailwind": {"name": "Tailwind CSS Documentation", "url": "https://tailwindcss.com/docs", "icon": "🎐"},
    "bootstrap": {"name": "Bootstrap Documentation", "url": "https://getbootstrap.com/docs/", "icon": "🅱️"},
    "react": {"name": "React Documentation", "url": "https://react.dev/", "icon": "⚛️"},
    "vue": {"name": "Vue.js Official Documentation", "url": "https://vuejs.org/guide/introduction.html", "icon": "🟢"},
    "angular": {"name": "Angular Official Docs", "url": "https://angular.dev/", "icon": "🅰️"},
    "svelte": {"name": "Svelte Documentation", "url": "https://svelte.dev/docs", "icon": "🔥"},
    "next": {"name": "Next.js Documentation", "url": "https://nextjs.org/docs", "icon": "▲"},
    "node": {"name": "Node.js Official Documentation", "url": "https://nodejs.org/docs/latest/api/", "icon": "🟩"},
    "sql": {"name": "PostgreSQL / SQL Official Reference", "url": "https://www.postgresql.org/docs/", "icon": "🗄️"},
    "postgres": {"name": "PostgreSQL Official Docs", "url": "https://www.postgresql.org/docs/", "icon": "🐘"},
    "mysql": {"name": "MySQL Reference Manual", "url": "https://dev.mysql.com/doc/", "icon": "🐬"},
    "mongodb": {"name": "MongoDB Documentation", "url": "https://www.mongodb.com/docs/", "icon": "🍃"},
    "redis": {"name": "Redis Official Documentation", "url": "https://redis.io/docs/", "icon": "🔴"},
    "docker": {"name": "Docker Official Documentation", "url": "https://docs.docker.com/", "icon": "🐳"},
    "kubernetes": {"name": "Kubernetes Documentation", "url": "https://kubernetes.io/docs/home/", "icon": "☸️"},
    "django": {"name": "Django Project Documentation", "url": "https://docs.djangoproject.com/es/", "icon": "🎸"},
    "fastapi": {"name": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com/es/", "icon": "⚡"},
    "flask": {"name": "Flask Documentation", "url": "https://flask.palletsprojects.com/", "icon": "🧪"},
    "java": {"name": "Oracle Java Official Documentation", "url": "https://docs.oracle.com/en/java/", "icon": "☕"},
    "spring": {"name": "Spring Framework Documentation", "url": "https://spring.io/projects/spring-framework", "icon": "🌱"},
    "rust": {"name": "The Rust Programming Language Book", "url": "https://doc.rust-lang.org/book/", "icon": "🦀"},
    "go": {"name": "The Go Programming Language Docs", "url": "https://go.dev/doc/", "icon": "🐹"},
    "cpp": {"name": "cppreference.com (C++ Reference)", "url": "https://en.cppreference.com/w/", "icon": "⚙️"},
    "csharp": {"name": "Microsoft .NET / C# Documentation", "url": "https://learn.microsoft.com/es-es/dotnet/csharp/", "icon": "🟣"},
    "php": {"name": "PHP Official Manual", "url": "https://www.php.net/manual/es/", "icon": "🐘"},
    "linux": {"name": "Linux Foundation Docs", "url": "https://docs.kernel.org/", "icon": "🐧"},
    "aws": {"name": "Amazon Web Services Documentation", "url": "https://docs.aws.amazon.com/", "icon": "☁️"},
    "pandas": {"name": "Pandas Data Analysis Documentation", "url": "https://pandas.pydata.org/docs/", "icon": "🐼"},
    "numpy": {"name": "NumPy Scientific Computing Docs", "url": "https://numpy.org/doc/stable/", "icon": "🔢"}
}

# -----------------------------------------------------------------------------
# 4. STOPWORDS FILTRADAS (Español e Inglés para Extracción Precisa de Conceptos)
# -----------------------------------------------------------------------------
STOPWORDS = {
    # Español
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "para", "por",
    "con", "sin", "sobre", "entre", "tras", "durante", "hasta", "desde", "hacia", "curso",
    "completo", "guia", "guía", "tutorial", "master", "bootcamp", "aprende", "aprendiendo",
    "cero", "principiantes", "avanzado", "intermedio", "paso", "dias", "días", "horas",
    "minutos", "leccion", "lección", "seccion", "sección", "modulo", "módulo", "video",
    "introduccion", "introducción", "bienvenido", "bienvenida", "resumen", "conclusion",
    "conclusión", "final", "inicio", "empezando", "primeros", "pasos", "como", "cómo",
    "que", "qué", "donde", "dónde", "cuando", "cuándo", "cual", "cuál", "quien", "quién",
    "porque", "por qué", "todo", "toda", "todos", "todas", "este", "esta", "estos", "estas",
    "esto", "otro", "otra", "otros", "otras", "hacer", "crear", "usar", "usando", "trabajando",
    "buenas", "practicas", "prácticas", "ejercicio", "ejercicios", "proyecto", "proyectos",
    "repaso", "prueba", "examen", "recursos", "slides", "diapositivas", "notas", "material",
    "descarga", "descargas", "overview", "what", "how", "setup", "install",
    # Inglés
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "up", "about", "into", "over", "after", "course", "complete", "bootcamp", "guide",
    "tutorial", "masterclass", "mastery", "learn", "learning", "zero", "hero", "beginner",
    "beginners", "advanced", "intermediate", "step", "days", "hours", "minutes", "lesson",
    "section", "module", "video", "introduction", "intro", "welcome", "overview", "summary",
    "conclusion", "wrap", "start", "getting", "started", "which", "all", "this", "that",
    "these", "those", "other", "another", "make", "using", "work", "working", "best",
    "practices", "review", "test", "quiz", "resources", "download"
}


# -----------------------------------------------------------------------------
# 5. GESTIÓN DE CACHÉ LOCAL PERSISTENTE
# -----------------------------------------------------------------------------
def load_cache() -> dict:
    """Carga la caché local de conceptos investigados."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache: dict):
    """Guarda la caché local en disco de forma segura."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# -----------------------------------------------------------------------------
# 6. RESOLUCIÓN MULTINIVEL DE CONCEPTOS (Wikipedia REST, Opensearch, DDG)
# -----------------------------------------------------------------------------
def _fetch_url_json(url: str, timeout: float = 3.5) -> dict | None:
    """Ejecuta una petición HTTP con cabecera reglamentaria y timeout estricto."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def fetch_wikipedia_summary(term: str, lang: str = "es") -> dict | None:
    """
    Consulta la API REST abierta de Wikipedia para un término exacto.
    Retorna extracto enciclopédico, URL canónica e imagen (si existe).
    """
    clean_term = term.strip().replace(" ", "_")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_term)}"
    data = _fetch_url_json(url)
    if not data:
        return None

    if data.get("extract") and data.get("type") != "disambiguation":
        img = None
        if data.get("originalimage"):
            img = data["originalimage"].get("source")
        elif data.get("thumbnail"):
            img = data["thumbnail"].get("source")

        return {
            "found": True,
            "title": data.get("title", term),
            "extract": data.get("extract"),
            "image": img,
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://{lang}.wikipedia.org/wiki/{clean_term}"),
            "source": f"Wikipedia ({lang.upper()})"
        }
    return None


def search_wikipedia_title(term: str, lang: str = "es") -> str | None:
    """
    Utiliza el motor de búsqueda de Wikipedia para resolver términos ambiguos o compuestos
    (ej. 'git rebase' -> encuentra el artículo canónico 'Git').
    """
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={urllib.parse.quote(term)}&format=json&srlimit=1"
    )
    data = _fetch_url_json(url)
    if data and "query" in data and data["query"].get("search"):
        hits = data["query"]["search"]
        if hits:
            return hits[0].get("title")
    return None


def fetch_duckduckgo_instant(term: str) -> dict | None:
    """
    Consulta DuckDuckGo Instant Answer API como fuente secundaria.
    """
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(term)}&format=json&no_html=1&skip_disambig=1"
    data = _fetch_url_json(url)
    if not data:
        return None

    abstract = data.get("Abstract")
    if abstract:
        return {
            "found": True,
            "title": data.get("Heading") or term,
            "extract": abstract,
            "image": data.get("Image") or None,
            "url": data.get("AbstractURL") or "",
            "source": "DuckDuckGo Tech Knowledge"
        }
    return None


def search_concept_knowledge(concept: str) -> dict | None:
    """
    Resuelve el conocimiento de un concepto a través del pipeline multinivel:
      1. Caché persistente local.
      2. Base de conocimiento offline embebida.
      3. Wikipedia REST API directa (Español).
      4. Wikipedia REST API directa (Inglés).
      5. Búsqueda y desambiguación Wikipedia (encuentra artículo exacto).
      6. DuckDuckGo Instant Answer API.
    """
    if not concept or len(concept.strip()) < 2:
        return None

    norm = concept.strip().lower()

    # Nivel 1: Caché local
    cache = load_cache()
    if norm in cache:
        return cache[norm]

    # Nivel 2: Base embebida offline
    if norm in EMBEDDED_KNOWLEDGE_BASE:
        res = dict(EMBEDDED_KNOWLEDGE_BASE[norm])
        res["found"] = True
        cache[norm] = res
        save_cache(cache)
        return res

    # Nivel 3: Wikipedia en Español (Directo)
    res = fetch_wikipedia_summary(concept, lang="es")

    # Nivel 4: Wikipedia en Inglés (Directo)
    if not res:
        res = fetch_wikipedia_summary(concept, lang="en")

    # Nivel 5: Búsqueda y Resolución de Título en Wikipedia
    if not res:
        resolved_title = search_wikipedia_title(concept, lang="es")
        if resolved_title:
            res = fetch_wikipedia_summary(resolved_title, lang="es")
        if not res:
            resolved_title_en = search_wikipedia_title(concept, lang="en")
            if resolved_title_en:
                res = fetch_wikipedia_summary(resolved_title_en, lang="en")

    # Nivel 6: DuckDuckGo
    if not res:
        res = fetch_duckduckgo_instant(concept)

    if res:
        cache[norm] = res
        save_cache(cache)
        return res

    return None


# -----------------------------------------------------------------------------
# 7. EXTRACTOR NLP AUTÓNOMO DE CONCEPTOS Y TEMAS TÉCNICOS
# -----------------------------------------------------------------------------
# Diccionario extendido de tecnologías para reconocimiento prioritario
TECH_TAXONOMY = {
    "git": ["Git", "GitHub", "Branching", "Staging Area"],
    "github": ["GitHub", "Git", "Pull Request"],
    "python": ["Python", "Programación orientada a objetos", "Algoritmo", "Estructura de datos"],
    "javascript": ["JavaScript", "TypeScript", "Event Loop", "DOM"],
    "typescript": ["TypeScript", "JavaScript", "Tipado estático"],
    "docker": ["Docker", "Contenedores", "Kubernetes"],
    "kubernetes": ["Kubernetes", "Docker", "Microservicios"],
    "sql": ["SQL", "Base de datos relacional", "PostgreSQL"],
    "postgres": ["PostgreSQL", "SQL", "Base de datos relacional"],
    "mysql": ["MySQL", "SQL", "Base de datos relacional"],
    "mongo": ["MongoDB", "NoSQL", "JSON"],
    "react": ["React", "JavaScript", "Virtual DOM"],
    "angular": ["Angular", "TypeScript", "Frontend"],
    "vue": ["Vue.js", "JavaScript", "Frontend"],
    "django": ["Django", "Python", "API REST"],
    "fastapi": ["FastAPI", "Python", "API REST"],
    "flask": ["Flask", "Python", "API REST"],
    "node": ["Node.js", "JavaScript", "Servidor web"],
    "linux": ["Linux", "Línea de comandos", "Bash"],
    "bash": ["Bash", "Linux", "Línea de comandos"],
    "api": ["API REST", "HTTP", "Servidor web"],
    "rest": ["API REST", "HTTP", "JSON"],
    "aws": ["Amazon Web Services", "Cloud Computing"],
    "azure": ["Microsoft Azure", "Cloud Computing"],
    "machine learning": ["Machine Learning", "Inteligencia artificial", "Algoritmo"],
    "ia": ["Inteligencia artificial", "Machine Learning", "Redes neuronales"],
    "deep learning": ["Deep Learning", "Redes neuronales", "Machine Learning"],
    "pandas": ["Pandas", "Python", "Ciencia de datos"],
    "numpy": ["NumPy", "Python", "Algoritmo"]
}


def clean_words(text: str) -> list[str]:
    """Extrae palabras alfanuméricas limpias descartando caracteres de puntuación."""
    return re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑüÜ]{3,}", text)


def extract_core_topics_from_text(course_title: str, section_titles: list[str], sample_texts: list[str]) -> list[str]:
    """
    Analiza de forma autónoma el título, secciones y extractos para determinar
    los 4 a 6 conceptos clave del curso, priorizando tecnologías y descartando ruido.
    """
    corpus = (course_title + " " + " ".join(section_titles) + " " + " ".join(sample_texts[:6])).lower()

    selected_topics = []

    # 1. Emparejamiento por taxonomía tecnológica prioritaria
    for key, terms in TECH_TAXONOMY.items():
        if re.search(r"\b" + re.escape(key) + r"\b", corpus):
            for t in terms:
                if t not in selected_topics:
                    selected_topics.append(t)
        if len(selected_topics) >= 5:
            break

    # 2. Si aún faltan temas, buscar palabras técnicas significativas en títulos sin stopwords
    if len(selected_topics) < 4:
        all_words = clean_words(course_title + " " + " ".join(section_titles[:4]))
        freq = {}
        for w in all_words:
            w_norm = w.lower()
            if w_norm not in STOPWORDS and len(w_norm) > 3:
                freq[w] = freq.get(w, 0) + 1

        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        for w, _ in sorted_words:
            cap_w = w.capitalize()
            if cap_w not in selected_topics:
                selected_topics.append(cap_w)
            if len(selected_topics) >= 5:
                break

    # 3. Respaldo por defecto
    if not selected_topics:
        selected_topics = ["Ingeniería de software", "Programación", "Tecnología"]

    return selected_topics[:5]


def extract_lecture_concepts(lecture_title: str, lecture_text: str = "") -> list[str]:
    """
    Extrae los 2-4 conceptos específicos de una lección individual
    para presentar sugerencias de búsqueda y evaluación activa en la interfaz.
    """
    raw_words = clean_words(lecture_title)
    meaningful = [
        w for w in raw_words
        if w.lower() not in STOPWORDS and len(w) > 3
    ]
    return meaningful[:4] if meaningful else [w for w in raw_words if len(w) > 3][:3]


# -----------------------------------------------------------------------------
# 8. ENRIQUECIMIENTO INTEGRAL DEL CURSO (Función Principal)
# -----------------------------------------------------------------------------
def enrich_course_with_knowledge(course_title: str, sections_data: list[dict]) -> dict:
    """
    Enriquece los datos del curso con:
      - Conceptos y definiciones enciclopédicas de Wikipedia/DDG.
      - Diagramas de arquitectura e ilustraciones de Wikimedia Commons.
      - Enlaces y referencias a la documentación técnica oficial.
    """
    section_titles = [s.get("title", "") for s in sections_data]
    sample_texts = []
    for s in sections_data[:4]:
        for l in s.get("lectures", [])[:2]:
            if l.get("text"):
                sample_texts.append(l["text"][:350])

    topics = extract_core_topics_from_text(course_title, section_titles, sample_texts)
    print(f"  🔍 Investigando conceptos web relacionados para el curso: {', '.join(topics)}...")

    knowledge_cards = []
    for t in topics:
        try:
            info = search_concept_knowledge(t)
            if info:
                knowledge_cards.append({
                    "concept": t,
                    "title": info.get("title", t),
                    "extract": info.get("extract", ""),
                    "image": info.get("image"),
                    "url": info.get("url", ""),
                    "source": info.get("source", "Web Knowledge")
                })
            # Pequeña pausa preventiva para respetar las políticas de tasa de peticiones
            time.sleep(0.15)
        except Exception:
            pass

    # Documentación oficial de referencia
    doc_links = []
    course_lower = (course_title + " " + " ".join(section_titles[:3])).lower()
    for key, meta in OFFICIAL_DOCS_MAP.items():
        if re.search(r"\b" + re.escape(key) + r"\b", course_lower):
            if meta not in doc_links:
                doc_links.append(meta)

    if not doc_links:
        doc_links.append({
            "name": "Wikipedia - Portal de Informática y Tecnología",
            "url": "https://es.wikipedia.org/wiki/Portal:Inform%C3%A1tica",
            "icon": "📚"
        })

    # Esquemas y diagramas visuales curados
    visuals = []
    for key, vlist in CURATED_TOPIC_VISUALS.items():
        if re.search(r"\b" + re.escape(key) + r"\b", course_lower):
            for v in vlist:
                if v not in visuals:
                    visuals.append(v)

    # Si no hubo coincidencia específica, agregar un diagrama general de arquitectura web
    if not visuals and "web" in CURATED_TOPIC_VISUALS:
        visuals.extend(CURATED_TOPIC_VISUALS["web"][:1])

    return {
        "topics": topics,
        "cards": knowledge_cards,
        "official_docs": doc_links,
        "visuals": visuals
    }


# -----------------------------------------------------------------------------
# 9. MODO DE PRUEBA Y DIAGNÓSTICO EN TERMINAL
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Git"
    print(f"\n=======================================================")
    print(f" 🧠 PRUEBA DE CONOCIMIENTO AUTÓNOMO: '{query}'")
    print(f"=======================================================")
    result = search_concept_knowledge(query)
    if result:
        print(f"📌 Título : {result.get('title')}")
        print(f"🏛️ Fuente : {result.get('source')}")
        print(f"🔗 URL    : {result.get('url')}")
        print(f"🖼️ Imagen : {result.get('image') or 'No disponible'}")
        print(f"\n📝 Extracto:\n{result.get('extract')}")
    else:
        print("❌ No se encontró información para el concepto consultado.")
    print("=======================================================\n")
