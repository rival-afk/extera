"""Анализ зависимостей между модулями проекта"""

from pathlib import Path
from typing import Dict, List, Set
import re


def find_py_files(root_dir: Path) -> List[Path]:
    """Возвращает список всех .py файлов в корневой папке (не рекурсивно)"""
    return [f for f in root_dir.glob('*.py') if f.is_file()]


def build_dependency_graph(main_file: Path, all_files: List[Path]) -> Dict[Path, List[Path]]:
    """
    Строит граф зависимостей между файлами проекта.
    Возвращает словарь {файл: [список_файлов_от_которых_зависит]}
    """
    # Создаём маппинг имени модуля на файл
    module_map = {f.stem: f for f in all_files}
    graph = {f: [] for f in all_files}
    
    for py_file in all_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем импорты локальных модулей
            patterns = [
                r'^import\s+(\w+)',
                r'^from\s+(\w+)\s+import',
                r'^from\s+\.(\w+)\s+import',
                r'^from\s+\.\.(\w+)\s+import',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if match in module_map and module_map[match] != py_file:
                        if module_map[match] not in graph[py_file]:
                            graph[py_file].append(module_map[match])
        except Exception:
            continue
    
    return graph


def resolve_dependencies(main_file: Path, graph: Dict[Path, List[Path]]) -> List[Path]:
    """
    Возвращает упорядоченный список файлов для вставки (топологическая сортировка).
    main_file исключается из результата (он будет последним).
    """
    visited = set()
    order = []
    
    def dfs(file: Path):
        if file in visited:
            return
        visited.add(file)
        for dep in graph.get(file, []):
            if dep != main_file:
                dfs(dep)
        if file != main_file:
            order.append(file)
    
    dfs(main_file)
    
    # Убираем дубликаты, сохраняя порядок
    seen = set()
    unique_order = []
    for f in order:
        if f not in seen:
            seen.add(f)
            unique_order.append(f)
    
    return unique_order
