"""
Script para integrar FRD validation en main.py
Este script agrega las funciones necesarias al EnhancedCatalogApp class
"""

# Funciones a agregar a la clase EnhancedCatalogApp en main.py

FUNCTIONS_TO_ADD = '''
    def _render_frd_schema(self, method='excel'):
        """CP-UX-010 v4: Muestra esquema FRD con badges REQUIRED/OPTIONAL"""
        st.markdown("### 📋 Esquema de Datos Requerido")
        st.caption("Tu archivo debe contener las siguientes columnas:")
        
        # Tabla de esquema
        schema_data = []
        for col_name, spec in FRD_SCHEMA.items():
            badge = "🔴 REQUIRED" if spec['required'] else "🟡 OPTIONAL"
            schema_data.append({
                'Columna': col_name,
                'Estado': badge,
                'Tipo': spec['type'],
                'Ejemplo': str(spec['example']),
                'Descripción': spec['description']
            })
        
        df_schema = pd.DataFrame(schema_data)
        st.dataframe(df_schema, use_container_width=True, height=400)
        
        # CTAs según método
        if method == 'excel':
            col1, col2 = st.columns([1, 3])
            with col1:
                # Generar Excel de plantilla
                template_df = pd.DataFrame({col: [spec['example']] 
                                           for col, spec in FRD_SCHEMA.items()})
                csv = template_df.to_csv(index=False)
                st.download_button(
                    "📥 Descargar Plantilla",
                    csv,
                    "plantilla_catalogpro.csv",
                    "text/csv",
                    type="primary"
                )
            with col2:
                st.caption("💡 Descarga esta plantilla y úsala como base para tu inventario")
        else:  # sheets
            st.info("""
            **📊 Para Google Sheets:**
            1. Crea una hoja con las columnas listadas arriba
            2. La primera fila debe contener los nombres exactos de las columnas
            3. Respeta el orden de las columnas
            4. Asegúrate de que el documento sea público o compartido como lector
            """)
    
    def _render_reset_modal(self):
        """CP-UX-010 v4: Modal de confirmación para reset"""
        if st.session_state.get('show_reset_modal', False):
            st.markdown("---")
            st.warning("### ⚠️ Confirmar Reinicio")
            st.markdown("""
            **¿Estás seguro de que deseas reiniciar la importación?**
            
            Esto eliminará:
            - ✗ Todos los datos cargados
            - ✗ Configuración de validación
            - ✗ Preview y métricas
            - ✗ Resultados de búsqueda y filtros
            
            ⚠️ Esta acción no se puede deshacer.
            """)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Cancelar", type="secondary", key="cancel_reset"):
                    st.session_state.show_reset_modal = False
                    st.rerun()
            
            with col2:
                if st.button("🔄 Sí, Reiniciar", type="primary", key="confirm_reset"):
                    # Reset COMPLETO
                    st.session_state.df = None
                    st.session_state.data_sources = []
                    st.session_state.import_stage = 'select'
                    st.session_state.preview_data = None
                    st.session_state.validation_result = None
                    st.session_state.validation_status = 'idle'
                    st.session_state.current_page = 1
                    st.session_state.show_reset_modal = False
                    
                    st.success("**✅ Importación reiniciada exitosamente**")
                    st.rerun()
'''

print("Funciones FRD listas para integrar")
print("Agregar estas funciones a la clase EnhancedCatalogApp en main.py")
print("\nArchivos creados:")
print("- frd_schema.py")
print("- frd_validator.py")
print("- frd_helpers.py")
