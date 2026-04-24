"""Очистка кода от синтаксических ошибок"""

import re
from typing import Set


def clean_code(content: str, available_modules: Set[str]) -> str:
    """
    Очищает код от синтаксических ошибок.
    НЕ удаляет импорты - это делает compiler.py
    """
    if not content:
        return ""
    
    # Удаляем BOM если есть
    if content.startswith('\ufeff'):
        content = content[1:]
    
    lines = content.split('\n')
    cleaned = []
    
    for line in lines:
        stripped = line.strip()
        
        # Исправляем ошибочные строки со списками имён
        if is_bad_standalone_list(stripped):
            cleaned.append(f'# [auto-fixed] {line}')
            continue
        
        cleaned.append(line)
    
    # Удаляем пустые строки в начале и конце
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    
    return '\n'.join(cleaned)


def is_bad_standalone_list(line: str) -> bool:
    """Проверяет, является ли строка ошибочным списком имён без присваивания"""
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        return False
    
    safe_keywords = ('=', '(', ')', ':', 'def', 'class', 'import', 'from',
                     'return', 'if', 'for', 'while', 'try', 'except', 'with',
                     'lambda', '[', ']', '{', '}', '@', 'async', 'await')
    
    if any(kw in stripped for kw in safe_keywords):
        return False
    
    if ',' in stripped and re.match(r'^[\w\s,]+$', stripped):
        return True
    
    return False
