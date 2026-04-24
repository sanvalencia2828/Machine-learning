#!/usr/bin/env python3
"""
prepare_docs.py
===============
Pre-procesador de notebooks Jupytext → Markdown limpio para MkDocs.

Detecta y convierte cuatro variantes encontradas en notebooks/:

  Formato A — Markdown nativo con YAML frontmatter
              (empieza con "---", e.g. notebook_ch02_monty_hall.md)
              → Elimina el bloque YAML y lo sirve directamente.

  Formato B — Percent format encadenado (#-commented YAML + # %% markers)
              (empieza con "# ---", e.g. notebook_ch02c_bsm.md)
              → Elimina el header comentado y convierte células.

  Formato C — Light format puro (# comentarios como markdown + código desnudo)
              (e.g. notebook_ch01_forward_inverse.md, notebook_ch02_ltcm.md)
              → Convierte bloques de comentarios a MD y código a fenced blocks.

  Formato D — Markdown puro sin frontmatter
              (e.g. notebook_ch08_kelly_capital_allocation.md)
              → Copia directamente sin modificaciones.

Salida: docs-processed/  (docs_dir para mkdocs.yml)
"""

import re
import shutil
from pathlib import Path

# ── Directorios ────────────────────────────────────────────────────────────
NOTEBOOKS_DIR   = Path("notebooks")
OUTPUT_DIR      = Path("docs-processed")
ASSETS_SRC      = Path("docs")   # javascripts/ y stylesheets/

# ── Expresiones regulares ──────────────────────────────────────────────────
RE_CELL_SEP        = re.compile(r"^# %%(?:\s.*)?$", re.MULTILINE)
RE_MARKDOWN_CELL   = re.compile(r"^# %% \[markdown\]$", re.MULTILINE)
RE_YAML_FENCE      = re.compile(r"^---\s*\n.*?^---\s*\n", re.DOTALL | re.MULTILINE)
RE_HASH_YAML       = re.compile(r"^# ---\s*\n(?:# .*\n)*# ---\s*\n", re.MULTILINE)
RE_COMMENT_LINE    = re.compile(r"^# ?", re.MULTILINE)


# ══════════════════════════════════════════════════════════════════════════
# Detección de formato
# ══════════════════════════════════════════════════════════════════════════

def detect_format(content: str) -> str:
    """
    Devuelve: 'markdown_yaml' | 'hash_yaml_percent' | 'light_percent' | 'pure_markdown'
    """
    stripped = content.lstrip()

    # Formato A: YAML frontmatter real (---)
    if stripped.startswith("---"):
        return "markdown_yaml"

    # Formato B: YAML comentado con # ---
    if stripped.startswith("# ---"):
        return "hash_yaml_percent"

    # Formato C: Light percent — tiene separadores # %% pero sin YAML
    if RE_CELL_SEP.search(content):
        return "light_percent"

    # Formato D: Markdown puro
    return "pure_markdown"


# ══════════════════════════════════════════════════════════════════════════
# Conversores por formato
# ══════════════════════════════════════════════════════════════════════════

def convert_markdown_yaml(content: str, stem: str) -> str:
    """Formato A: elimina el bloque YAML frontmatter."""
    # Eliminar frontmatter jupyter/kernelspec
    content = RE_YAML_FENCE.sub("", content, count=1)
    return content.strip() + "\n"


def convert_hash_yaml_percent(content: str, stem: str) -> str:
    """
    Formato B: # --- ... # --- (YAML comentado) + # %% [markdown] / # %% cells.
    Pasos:
      1. Eliminar bloque YAML comentado.
      2. Convertir células markdown (# %% [markdown] → contenido sin #).
      3. Envolver células de código en ```python```.
    """
    # 1. Eliminar bloque # --- ... # ---
    content = RE_HASH_YAML.sub("", content, count=1)

    # 2. Dividir por cualquier separador # %%...
    parts = RE_CELL_SEP.split(content)
    # El separador original nos dice si era [markdown] o código:
    # Como split() pierde la info del separador, re-procesamos con finditer
    cells = _split_with_types(content)

    return _render_cells(cells)


def convert_light_percent(content: str, stem: str) -> str:
    """
    Formato C: células de código Python mezcladas con comentarios markdown.
    Sin YAML. Cada línea que empieza con # es markdown o separador.
    """
    cells = _split_with_types(content)
    return _render_cells(cells)


def convert_pure_markdown(content: str, stem: str) -> str:
    """Formato D: sin transformaciones."""
    return content


# ══════════════════════════════════════════════════════════════════════════
# Helpers de conversión de células
# ══════════════════════════════════════════════════════════════════════════

def _split_with_types(content: str) -> list[dict]:
    """
    Divide el contenido en células tipadas: {'type': 'markdown'|'code', 'lines': [...]}
    Maneja # %% [markdown] y # %% (código puro).
    """
    # Encontrar todos los separadores y sus posiciones
    sep_pattern = re.compile(r"^(# %%(?:\s*.*)?)$", re.MULTILINE)
    
    boundaries = [m for m in sep_pattern.finditer(content)]
    
    if not boundaries:
        # Sin separadores: analizar línea a línea
        return [_analyze_raw_block(content)]
    
    cells = []
    
    # Contenido antes del primer separador
    if boundaries[0].start() > 0:
        pre = content[:boundaries[0].start()]
        if pre.strip():
            cells.append(_analyze_raw_block(pre))
    
    for i, sep in enumerate(boundaries):
        sep_text = sep.group(1)
        # Determinar si es célula markdown explícita
        is_explicit_md = "[markdown]" in sep_text.lower()
        
        # Contenido de la célula: desde el fin del separador hasta el inicio del próximo
        start = sep.end() + 1  # +1 para saltar el \n del separador
        end = boundaries[i + 1].start() if i + 1 < len(boundaries) else len(content)
        cell_content = content[start:end]
        
        if not cell_content.strip():
            continue
        
        if is_explicit_md:
            # Célula markdown explícita: strip # de cada línea
            md_lines = []
            for line in cell_content.splitlines():
                if line.startswith("# "):
                    md_lines.append(line[2:])
                elif line == "#":
                    md_lines.append("")
                else:
                    md_lines.append(line)
            cells.append({"type": "markdown", "lines": md_lines})
        else:
            cells.append(_analyze_raw_block(cell_content))
    
    return cells


def _analyze_raw_block(content: str) -> dict:
    """
    Heurística: si TODAS las líneas no-vacías empiezan con #, es markdown.
    Si hay mezcla, separar prefijo-markdown del código.
    """
    lines = content.splitlines()
    non_empty = [l for l in lines if l.strip()]
    
    if not non_empty:
        return {"type": "markdown", "lines": []}
    
    all_comments = all(l.startswith("#") for l in non_empty)
    
    if all_comments:
        # Markdown puro — strip #
        md_lines = []
        for line in lines:
            if line.startswith("# "):
                md_lines.append(line[2:])
            elif line == "#":
                md_lines.append("")
            elif line.startswith("#"):
                md_lines.append(line[1:])  # e.g. #texto → texto
            else:
                md_lines.append(line)
        return {"type": "markdown", "lines": md_lines}
    else:
        return {"type": "code", "lines": lines}


def _render_cells(cells: list[dict]) -> str:
    """Convierte lista de células a texto Markdown final."""
    parts = []
    
    for cell in cells:
        ctype  = cell["type"]
        lines  = cell["lines"]
        
        # Eliminar líneas vacías al inicio y fin
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            continue
        
        if ctype == "markdown":
            parts.append("\n".join(lines))
        else:
            # Detectar si ya tiene fenced block
            joined = "\n".join(lines)
            if joined.strip().startswith("```"):
                parts.append(joined)
            else:
                # Filtrar líneas que son el separador %matplotlib inline (magic commands)
                code_lines = []
                for l in lines:
                    if l.strip().startswith("%") or l.strip().startswith("!"):
                        code_lines.append("# " + l.strip() + "  # magic/shell command")
                    else:
                        code_lines.append(l)
                parts.append("```python\n" + "\n".join(code_lines) + "\n```")
    
    return "\n\n".join(parts) + "\n"


# ══════════════════════════════════════════════════════════════════════════
# Orquestador principal
# ══════════════════════════════════════════════════════════════════════════

CONVERTERS = {
    "markdown_yaml":     convert_markdown_yaml,
    "hash_yaml_percent": convert_hash_yaml_percent,
    "light_percent":     convert_light_percent,
    "pure_markdown":     convert_pure_markdown,
}

FORMAT_ICONS = {
    "markdown_yaml":     "[MD-YAML]",
    "hash_yaml_percent": "[CONVERT]",
    "light_percent":     "[CONVERT]",
    "pure_markdown":     "[COPY   ]",
}


def process_file(src: Path, dst: Path) -> str:
    content = src.read_text(encoding="utf-8", errors="replace")
    fmt = detect_format(content)
    converter = CONVERTERS[fmt]
    processed = converter(content, src.stem)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(processed, encoding="utf-8")
    return fmt


def main():
    print("\n[OK] prepare_docs.py -- Procesando notebooks para MkDocs\n")
    print(f"   Fuente : {NOTEBOOKS_DIR}/")
    print(f"   Destino: {OUTPUT_DIR}/\n")

    # Limpiar directorio de salida
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    # Copiar assets (JS, CSS) desde docs/ al directorio de salida
    # MkDocs necesita que custom_dir exista y apunte al override del tema
    # Los assets (javascripts/, stylesheets/) van a docs/ separado
    # No tocar docs/ — sigue siendo custom_dir en mkdocs.yml

    # Procesar archivos .md
    stats = {"markdown_yaml": 0, "hash_yaml_percent": 0,
             "light_percent": 0, "pure_markdown": 0}

    md_files = sorted(NOTEBOOKS_DIR.glob("*.md"))
    if not md_files:
        print("❌ No se encontraron archivos .md en notebooks/")
        return

    for src_file in md_files:
        dst_file = OUTPUT_DIR / src_file.name
        fmt = process_file(src_file, dst_file)
        icon = FORMAT_ICONS[fmt]
        stats[fmt] += 1
        print(f"  {icon} [{fmt:20s}] {src_file.name}")

    total = sum(stats.values())
    converted = stats["hash_yaml_percent"] + stats["light_percent"]
    copied    = stats["markdown_yaml"] + stats["pure_markdown"]

    sep = "-" * 60
    print(f"\n  {sep}")
    print(f"  [OK] Total procesados : {total} archivos")
    print(f"  [>>] Convertidos      : {converted}  (Jupytext -> Markdown)")
    print(f"  [CP] Copiados/limpios : {copied}  (ya eran Markdown)")
    print(f"\n  Salida: {OUTPUT_DIR}/")
    print(f"  {sep}\n")


if __name__ == "__main__":
    main()
