"""
knowledge_engine.py — Motor de Investigación Autónoma y Fuentes Web (Sin APIs de IA).
Extrae conceptos técnicos clave de cursos y transcripciones, y consulta fuentes
enciclopédicas y documentación oficial (Wikipedia REST API, DuckDuckGo, Wikimedia Commons,
MDN, Git SCM y Python Docs) de forma 100% gratuita, sin tokens ni costes.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CACHE_FILE = Path.home() / ".cache" / "udemy-transcripts-knowledge-cache.json"

# Biblioteca de esquemas y diagramas educativos de alta resolución (Wikimedia Commons / Creative Commons)
CURATED_TOPIC_VISUALS = {
    "git": [
        {
            "title": "Diagrama Oficial de Arquitectura de Git (Workflow)",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0e/GitWorkflow.svg/960px-GitWorkflow.svg.png",
            "caption": "Esquema de las 4 áreas clave de Git: Directorio de Trabajo, Staging Area (Índice), Repositorio Local y Repositorio Remoto."
        },
        {
            "title": "Logotipo de Git y Control Distribuido",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e0/Git-logo.svg/langes-960px-Git-logo.svg.png",
            "caption": "Git es el sistema de control de versiones distribuido estándar en la industria del software."
        }
    ],
    "github": [
        {
            "title": "GitHub y Colaboración Remota",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c2/GitHub_Invertocat_Logo.svg/langes-800px-GitHub_Invertocat_Logo.svg.png",
            "caption": "GitHub permite sincronizar commits, abrir Pull Requests y colaborar en equipos globales."
        }
    ],
    "python": [
        {
            "title": "Arquitectura y Filosofía de Python",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/800px-Python-logo-notext.svg.png",
            "caption": "Python: Lenguaje de programación interpretado multiparadigma con tipado dinámico y sintaxis limpia."
        },
        {
            "title": "Algoritmos y Flujo Lógico en Python",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/62/CPT-TheoryOfComp-Binary-Search-Python.png/800px-CPT-TheoryOfComp-Binary-Search-Python.png",
            "caption": "Estructuras de datos, bucles y lógica computacional aplicadas en Python."
        }
    ],
    "docker": [
        {
            "title": "Contenedores Docker y Aislamiento de Entornos",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4e/Docker_%28container_engine%29_logo.svg/800px-Docker_%28container_engine%29_logo.svg.png",
            "caption": "Docker empaqueta código y dependencias en contenedores ligeros e independientes del sistema anfitrión."
        }
    ],
    "sql": [
        {
            "title": "Bases de Datos Relacionales y SQL",
            "url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/29/Postgresql_elephant.svg/800px-Postgresql_elephant.svg.png",
            "caption": "Estructura de tablas, claves primarias/foráneas y persistencia mediante lenguaje SQL."
        }
    ]
}

OFFICIAL_DOCS_MAP = {
    "git": {
        "name": "Git SCM Official Documentation",
        "url": "https://git-scm.com/doc",
        "icon": "📦"
    },
    "github": {
        "name": "GitHub Docs",
        "url": "https://docs.github.com/",
        "icon": "🐙"
    },
    "python": {
        "name": "Python 3 Official Documentation",
        "url": "https://docs.python.org/3/",
        "icon": "🐍"
    },
    "javascript": {
        "name": "MDN Web Docs (JavaScript)",
        "url": "https://developer.mozilla.org/es/docs/Web/JavaScript",
        "icon": "⚡"
    },
    "html": {
        "name": "MDN Web Docs (HTML5)",
        "url": "https://developer.mozilla.org/es/docs/Web/HTML",
        "icon": "🌐"
    },
    "css": {
        "name": "MDN Web Docs (CSS3)",
        "url": "https://developer.mozilla.org/es/docs/Web/CSS",
        "icon": "🎨"
    },
    "sql": {
        "name": "PostgreSQL / SQL Official Reference",
        "url": "https://www.postgresql.org/docs/",
        "icon": "🗄️"
    },
    "docker": {
        "name": "Docker Official Documentation",
        "url": "https://docs.docker.com/",
        "icon": "🐳"
    },
    "angular": {
        "name": "Angular Official Docs",
        "url": "https://angular.dev/",
        "icon": "🅰️"
    },
    "react": {
        "name": "React Documentation",
        "url": "https://react.dev/",
        "icon": "⚛️"
    },
    "java": {
        "name": "Oracle Java Official Documentation",
        "url": "https://docs.oracle.com/en/java/",
        "icon": "☕"
    }
}


def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache):
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def fetch_wikipedia_summary(term, lang="es"):
    """
    Consulta la API REST abierta de Wikipedia (con soporte de imágenes y extracto).
    """
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(term)}"
    req = urllib.request.Request(url, headers={"User-Agent": "UdemyTranscriptsPro/2.0 (Educational Tool)"})
    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("extract") and data.get("type") != "disambiguation":
                img = None
                if data.get("originalimage"):
                    img = data["originalimage"].get("source")
                elif data.get("thumbnail"):
                    img = data["thumbnail"].get("source")

                return {
                    "found": True,
                    "title": data.get("title"),
                    "extract": data.get("extract"),
                    "image": img,
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "source": f"Wikipedia ({lang.upper()})"
                }
    except Exception:
        pass
    return None


def fetch_duckduckgo_instant(term):
    """
    Consulta Instant Answer API de DuckDuckGo para definiciones técnicas directas.
    """
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(term)}&format=json&no_html=1&skip_disambig=1"
    req = urllib.request.Request(url, headers={"User-Agent": "UdemyTranscriptsPro/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
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
    except Exception:
        pass
    return None


def search_concept_knowledge(concept):
    """
    Investiga un concepto en múltiples fuentes públicas con caché local.
    """
    cache = load_cache()
    norm = concept.strip().lower()
    if norm in cache:
        return cache[norm]

    res = fetch_wikipedia_summary(concept, lang="es")
    if not res:
        res = fetch_wikipedia_summary(concept, lang="en")
    if not res:
        res = fetch_duckduckgo_instant(concept)

    if res:
        cache[norm] = res
        save_cache(cache)
        return res

    return None


def extract_core_topics_from_text(course_title, section_titles, sample_texts):
    corpus = (course_title + " " + " ".join(section_titles) + " " + " ".join(sample_texts[:5])).lower()
    candidate_terms = [
        ("git", ["Git", "GitHub", "Control de versiones", "Branching (software)"]),
        ("python", ["Python", "Programación orientada a objetos", "Algoritmo", "Estructura de datos"]),
        ("docker", ["Docker (software)", "Contenedor (informática)", "Kubernetes"]),
        ("sql", ["SQL", "Base de datos relacional", "PostgreSQL"]),
        ("backend", ["API REST", "Servidor web", "HTTP"]),
        ("frontend", ["JavaScript", "HTML5", "CSS"]),
        ("java", ["Java (lenguaje de programación)", "Máquina virtual Java", "Spring Framework"]),
        ("angular", ["Angular (framework)", "TypeScript"]),
        ("react", ["React (biblioteca de JavaScript)", "JSX"]),
        ("linux", ["Linux", "Línea de comandos", "Bash (shell)"])
    ]

    selected_topics = []
    for key, terms in candidate_terms:
        if key in corpus:
            for t in terms:
                if t not in selected_topics:
                    selected_topics.append(t)
        if len(selected_topics) >= 5:
            break

    if not selected_topics:
        words = re.findall(r'[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}', course_title)
        selected_topics = words[:4]

    return selected_topics[:5]


def enrich_course_with_knowledge(course_title, sections_data):
    """
    Enriquece los datos del curso con resúmenes, diagramas/fotos y referencias oficiales.
    """
    section_titles = [s.get("title", "") for s in sections_data]
    sample_texts = []
    for s in sections_data[:3]:
        for l in s.get("lectures", [])[:2]:
            if l.get("text"):
                sample_texts.append(l["text"][:300])

    topics = extract_core_topics_from_text(course_title, section_titles, sample_texts)
    print(f"  🔍 Investigando conceptos web relacionados para el curso: {', '.join(topics)}...")

    knowledge_cards = []
    for t in topics:
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

    # Referencias de documentación oficial sugeridas
    doc_links = []
    course_lower = course_title.lower()
    for key, meta in OFFICIAL_DOCS_MAP.items():
        if key in course_lower:
            doc_links.append(meta)

    if not doc_links:
        doc_links.append({
            "name": "Wikipedia - Portal de Informática y Tecnología",
            "url": "https://es.wikipedia.org/wiki/Portal:Inform%C3%A1tica",
            "icon": "📚"
        })

    # Esquemas visuales curados para el tema del curso
    visuals = []
    for key, vlist in CURATED_TOPIC_VISUALS.items():
        if key in course_lower:
            visuals.extend(vlist)

    return {
        "topics": topics,
        "cards": knowledge_cards,
        "official_docs": doc_links,
        "visuals": visuals
    }
