"""
FRD Validator for CatalogPro
Validates imported data against FRD schema
"""
import pandas as pd
from frd_schema import FRD_SCHEMA, get_required_columns, get_optional_columns

class FRDValidator:
    """Valida datos contra FRD schema"""
    
    def __init__(self, df):
        self.df = df
        self.schema = FRD_SCHEMA
        self.errors = []
        self.warnings = []
    
    def validate(self):
        """Ejecuta todas las validaciones y retorna resultado"""
        self._validate_required_columns()
        self._validate_required_values()
        self._validate_optional_values()
        self._validate_data_types()
        
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def _validate_required_columns(self):
        """Verifica que todas las columnas REQUIRED estén presentes"""
        required = get_required_columns()
        missing = [col for col in required if col not in self.df.columns]
        
        if missing:
            self.errors.append({
                'type': 'MISSING_REQUIRED_COLUMN',
                'severity': 'ERROR',
                'message': f"Faltan columnas obligatorias: {', '.join(missing)}",
                'columns': missing,
                'affected_rows': []
            })
    
    def _validate_required_values(self):
        """Verifica que columnas REQUIRED no tengan vacíos"""
        required = get_required_columns()
        
        for col in required:
            if col in self.df.columns:
                null_mask = self.df[col].isnull()
                null_count = null_mask.sum()
                
                if null_count > 0:
                    # Obtener índices de filas con valores nulos (1-indexed para usuario)
                    null_rows = [idx + 2 for idx in self.df[null_mask].index.tolist()]  # +2 porque Excel empieza en 1 y tiene header
                    
                    self.errors.append({
                        'type': 'NULL_IN_REQUIRED',
                        'severity': 'ERROR',
                        'column': col,
                        'message': f"Columna '{col}' (REQUIRED) tiene {null_count} valores vacíos",
                        'affected_rows': null_rows[:10],  # Primeras 10 filas
                        'total_affected': null_count
                    })
    
    def _validate_optional_values(self):
        """Advierte sobre vacíos en columnas OPTIONAL"""
        optional = get_optional_columns()
        
        for col in optional:
            if col in self.df.columns:
                null_count = self.df[col].isnull().sum()
                
                if null_count > 0:
                    self.warnings.append({
                        'type': 'NULL_IN_OPTIONAL',
                        'severity': 'WARNING',
                        'column': col,
                        'message': f"Columna '{col}' (OPTIONAL) tiene {null_count} valores vacíos",
                        'null_count': null_count
                    })
    
    def _validate_data_types(self):
        """Valida tipos de datos básicos"""
        for col, spec in self.schema.items():
            if col not in self.df.columns:
                continue
            
            expected_type = spec['type']
            
            # Validación de tipos numéricos
            if expected_type in ['float', 'int']:
                # Intentar convertir a numérico
                numeric_series = pd.to_numeric(self.df[col], errors='coerce')
                invalid_count = numeric_series.isnull().sum() - self.df[col].isnull().sum()
                
                if invalid_count > 0:
                    self.errors.append({
                        'type': 'INVALID_TYPE',
                        'severity': 'ERROR',
                        'column': col,
                        'message': f"Columna '{col}' debe ser numérica. {invalid_count} valores inválidos encontrados",
                        'affected_rows': [],
                        'total_affected': invalid_count
                    })
    
    def get_validation_report(self):
        """Genera reporte de validación en formato DataFrame"""
        report_data = []
        
        for error in self.errors:
            rows_str = ', '.join(map(str, error.get('affected_rows', [])[:5]))
            if error.get('total_affected', 0) > 5:
                rows_str += f" ... (+{error.get('total_affected') - 5} más)"
            
            report_data.append({
                'Tipo': 'Error',
                'Columna': error.get('column', 'General'),
                'Mensaje': error['message'],
                'Filas Afectadas': rows_str if rows_str else 'N/A'
            })
        
        for warning in self.warnings:
            report_data.append({
                'Tipo': 'Observación',
                'Columna': warning.get('column', 'General'),
                'Mensaje': warning['message'],
                'Filas Afectadas': f"{warning.get('null_count', 0)} filas"
            })
        
        return pd.DataFrame(report_data) if report_data else pd.DataFrame()
