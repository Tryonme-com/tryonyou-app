#!/usr/bin/env python3
# -------------------------------------------------------------------------
# Proyecto: TryOnYou V10 OMEGA
# Patente: PCT/EP2025/067317
# Arquitecto: Rubén Espinar
# Estado: PRODUCTION_STABLE | Soberanía: tryonyou.pro
# -------------------------------------------------------------------------
"""
Script de inyección automática de headers de soberanía.

Este script recorre todos los archivos .py en el repositorio e inyecta
automáticamente el header oficial de la patente PCT/EP2025/067317 en la
primera línea de cada archivo que no lo tenga.

Uso:
    python3 scripts/apply_sovereignty_header.py [--dry-run] [--path /ruta/custom]

Flags:
    --dry-run       Muestra qué archivos serían modificados sin hacer cambios
    --path          Especifica ruta personalizada (por defecto: ./)
    --exclude       Patrones a excluir (por defecto: venv, .git, __pycache__)
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# Header oficial de soberanía
SOVEREIGNTY_HEADER = """# -------------------------------------------------------------------------
# Proyecto: TryOnYou V10 OMEGA
# Patente: PCT/EP2025/067317
# Arquitecto: Rubén Espinar
# Estado: PRODUCTION_STABLE | Soberanía: tryonyou.pro
# -------------------------------------------------------------------------
"""

EXCLUDED_DIRS = {
    'venv', '.venv', 'env', '.env',
    '.git', '.github',
    '__pycache__', '.pytest_cache',
    'node_modules', 'dist', 'build',
    '.cursor', '__SOVEREIGN_PATCHES__'
}

EXCLUDED_FILES = {
    'apply_sovereignty_header.py',  # Este script mismo
}


def has_sovereignty_header(file_path: Path) -> bool:
    """Verifica si un archivo ya tiene el header de soberanía."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = f.read(200)
            return 'PCT/EP2025/067317' in first_lines
    except (UnicodeDecodeError, IOError):
        return False


def inject_header(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Inyecta el header de soberanía en un archivo Python.
    
    Retorna: (success: bool, mensaje: str)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene el header
        if 'PCT/EP2025/067317' in content:
            return True, f"✅ Ya tiene header: {file_path.relative_to(Path.cwd())}"
        
        # Inyectar header
        new_content = SOVEREIGNTY_HEADER + "\n" + content
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, f"✏️  Header inyectado: {file_path.relative_to(Path.cwd())}"
        else:
            return True, f"🔍 (DRY-RUN) Sería modificado: {file_path.relative_to(Path.cwd())}"
    
    except Exception as e:
        return False, f"❌ Error en {file_path}: {str(e)}"


def scan_repository(root_path: Path, dry_run: bool = False) -> dict:
    """
    Escanea el repositorio y aplica el header a todos los archivos .py.
    
    Retorna: dict con estadísticas
    """
    stats = {
        'total': 0,
        'modified': 0,
        'skipped': 0,
        'errors': 0,
        'messages': []
    }
    
    print(f"\n{'='*70}")
    print(f"🔱 SOBERANÍA HEADER INJECTOR — Fase 1: GOBERNANZA")
    print(f"{'='*70}")
    print(f"📂 Escaneando: {root_path}")
    print(f"🏷️  Patente: PCT/EP2025/067317")
    print(f"{'='*70}\n")
    
    if dry_run:
        print("⚠️  MODO DRY-RUN: No se realizarán cambios\n")
    
    for py_file in root_path.rglob('*.py'):
        # Saltar directorios excluidos
        if any(excluded in py_file.parts for excluded in EXCLUDED_DIRS):
            continue
        
        # Saltar archivos excluidos
        if py_file.name in EXCLUDED_FILES:
            continue
        
        stats['total'] += 1
        success, message = inject_header(py_file, dry_run)
        
        print(message)
        stats['messages'].append(message)
        
        if success:
            if 'Ya tiene' in message or 'DRY-RUN' in message:
                stats['skipped'] += 1
            else:
                stats['modified'] += 1
        else:
            stats['errors'] += 1
    
    return stats


def print_summary(stats: dict, dry_run: bool = False):
    """Imprime resumen de la operación."""
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN DE OPERACIÓN")
    print(f"{'='*70}")
    print(f"📁 Total de archivos .py analizados: {stats['total']}")
    print(f"✏️  Archivos modificados: {stats['modified']}")
    print(f"⏭️  Archivos sin cambios: {stats['skipped']}")
    print(f"❌ Errores: {stats['errors']}")
    
    if dry_run:
        print(f"\n💡 Para aplicar cambios, ejecuta sin --dry-run:")
        print(f"   python3 scripts/apply_sovereignty_header.py")
    else:
        if stats['modified'] > 0:
            print(f"\n✅ {stats['modified']} archivos han sido inyectados con el header de soberanía.")
            print(f"🔐 Tu repositorio ahora cumple con PCT/EP2025/067317")
    
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Inyector automático de headers de soberanía (PCT/EP2025/067317)"
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Modo preview: muestra cambios sin aplicarlos')
    parser.add_argument('--path', type=str, default='./',
                        help='Ruta raíz del escaneo (default: ./)')
    parser.add_argument('--exclude', type=str, default=None,
                        help='Patrones adicionales a excluir (separados por coma)')
    
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    
    if not root_path.exists():
        print(f"❌ Ruta no existe: {root_path}")
        sys.exit(1)
    
    if args.exclude:
        extra_excluded = set(args.exclude.split(','))
        EXCLUDED_DIRS.update(extra_excluded)
    
    stats = scan_repository(root_path, dry_run=args.dry_run)
    print_summary(stats, dry_run=args.dry_run)
    
    sys.exit(0 if stats['errors'] == 0 else 1)


if __name__ == '__main__':
    main()
