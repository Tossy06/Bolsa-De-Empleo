"""
Sistema de validación de lenguaje inclusivo
"""
import re
from typing import Dict, List, Tuple


class InclusiveLanguageValidator:
    """Valida términos no inclusivos en ofertas de empleo"""
    
    # Diccionario de términos no inclusivos
    NON_INCLUSIVE_TERMS = {
        'inválido': 'persona con discapacidad',
        'inválida': 'persona con discapacidad',
        'minusválido': 'persona con discapacidad',
        'minusválida': 'persona con discapacidad',
        'discapacitado': 'persona con discapacidad',
        'discapacitada': 'persona con discapacidad',
        'impedido': 'persona con movilidad reducida',
        'impedida': 'persona con movilidad reducida',
        'lisiado': 'persona con discapacidad física',
        'lisiada': 'persona con discapacidad física',
        'cojo': 'persona con movilidad reducida',
        'coja': 'persona con movilidad reducida',
        'paralítico': 'persona con parálisis',
        'paralítica': 'persona con parálisis',
        'persona normal': 'persona sin discapacidad',
        'personas normales': 'personas sin discapacidad',
        'gente normal': 'personas sin discapacidad',
        'sufre de': 'tiene/vive con',
        'padece de': 'tiene/vive con',
        'aquejado por': 'persona con',
        'víctima de': 'persona con',
        'afectado por': 'persona con',
        'confinado a silla de ruedas': 'usuario de silla de ruedas',
        'atado a silla de ruedas': 'usuario de silla de ruedas',
        'postrado': 'usuario de silla de ruedas',
        'ciego': 'persona con discapacidad visual',
        'ciega': 'persona con discapacidad visual',
        'invidente': 'persona con discapacidad visual',
        'sordo': 'persona sorda',
        'sorda': 'persona sorda',
        'sordomudo': 'persona sorda',
        'sordomuda': 'persona sorda',
        'mudo': 'persona con limitación en el habla',
        'muda': 'persona con limitación en el habla',
        'retrasado mental': 'persona con discapacidad intelectual',
        'retrasada mental': 'persona con discapacidad intelectual',
        'deficiente mental': 'persona con discapacidad intelectual',
        'mongólico': 'persona con síndrome de Down',
        'mongólica': 'persona con síndrome de Down',
        'demente': 'persona con condición de salud mental',
        'loco': 'persona con condición de salud mental',
        'loca': 'persona con condición de salud mental',
        'enfermo mental': 'persona con condición de salud mental',
        'enferma mental': 'persona con condición de salud mental',
        'necesidades especiales': 'necesidades específicas',
        'capacidades especiales': 'necesidades específicas',
        'capacidades diferentes': 'necesidades específicas',
        'personas especiales': 'personas con discapacidad',
    }
    
    # Campos a validar
    FIELDS_TO_CHECK = {
        'title': 'Título',
        'description': 'Descripción',
        'responsibilities': 'Responsabilidades',
        'requirements': 'Requisitos',
        'accessibility_features': 'Características de Accesibilidad',
        'benefits': 'Beneficios',
        'reasonable_accommodations': 'Ajustes Razonables',
        'workplace_accessibility': 'Accesibilidad del Lugar',
        'non_discrimination_statement': 'Declaración de No Discriminación'
    }
    
    @classmethod
    def _extract_context(cls, text: str, start: int, end: int, length: int = 30) -> str:
        """Extrae contexto alrededor de un término"""
        context_start = max(0, start - length)
        context_end = min(len(text), end + length)
        return f"...{text[context_start:context_end]}..."
    
    @classmethod
    def scan_text(cls, text: str) -> List[Dict]:
        """
        Escanea texto y retorna términos no inclusivos
        
        Returns:
            Lista de diccionarios con term, suggestion, position, context, severity, type
        """
        if not text:
            return []
        
        issues = []
        text_lower = text.lower()
        
        for term, suggestion in cls.NON_INCLUSIVE_TERMS.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                issues.append({
                    'term': text[match.start():match.end()],
                    'suggestion': suggestion,
                    'position': match.start(),
                    'context': cls._extract_context(text, match.start(), match.end()),
                    'severity': 'high',
                    'type': 'non_inclusive_term'
                })
        
        issues.sort(key=lambda x: x['position'])
        return issues
    
    @classmethod
    def validate_job_fields(cls, job_data: Dict) -> Tuple[bool, Dict[str, List[Dict]]]:
        """
        Valida campos de oferta de trabajo
        
        Returns:
            (es_válido, {campo: [issues]})
        """
        all_issues = {}
        
        for field in cls.FIELDS_TO_CHECK:
            if job_data.get(field):
                issues = cls.scan_text(str(job_data.get(field, '')))
                if issues:
                    all_issues[field] = issues
        
        return (not all_issues, all_issues)
    
    @classmethod
    def get_field_label(cls, field_name: str) -> str:
        """Retorna label legible del campo"""
        return cls.FIELDS_TO_CHECK.get(field_name, field_name)