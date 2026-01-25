# CP-UX-010 v4: Helper functions for FRD validation and reset

def _render_frd_schema(self, method='excel'):
    """Muestra esquema FRD con badges REQUIRED/OPTIONAL"""
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

def _render_reset_button(self):
    """Botón de reset con modal de confirmación"""
    if 'df' in st.session_state and st.session_state.df is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📊 **{len(st.session_state.df)} productos** cargados")
        with col2:
            if st.button("🔄 Reiniciar importación", type="secondary", key="reset_btn"):
                st.session_state.show_reset_modal = True
                st.rerun()
    
    # Modal de confirmación
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

def _render_preview_with_validation(self, df, source_name):
    """CP-UX-010 v4: Preview con validación FRD y resaltado de errores"""
    st.markdown("---")
    st.markdown("## 📊 Preview de Importación")
    st.caption(f"Fuente: {source_name}")
    
    # Ejecutar validación
    validator = FRDValidator(df)
    validation_result = validator.validate()
    
    # Resumen ejecutivo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filas detectadas", len(df))
    
    with col2:
        st.metric("Columnas detectadas", len(df.columns))
    
    with col3:
        error_count = validation_result['error_count']
        st.metric(
            "Errores (REQUIRED)", 
            error_count,
            delta="🔴 Bloquea" if error_count > 0 else "✓ OK",
            delta_color="inverse" if error_count > 0 else "normal"
        )
    
    with col4:
        warning_count = validation_result['warning_count']
        st.metric(
            "Warnings (OPTIONAL)", 
            warning_count,
            delta="🟡 Revisar" if warning_count > 0 else "✓ OK",
            delta_color="off"
        )
    
    # Mostrar errores y warnings
    if not validation_result['is_valid']:
        st.error("**❌ Importación bloqueada:** Se encontraron errores en campos obligatorios")
        
        with st.expander("🔍 Ver detalle de errores", expanded=True):
            for error in validation_result['errors']:
                st.markdown(f"**{error['type']}:** {error['message']}")
                if error.get('affected_rows'):
                    rows_str = ', '.join(map(str, error['affected_rows'][:5]))
                    if error.get('total_affected', 0) > 5:
                        rows_str += f" ... (+{error['total_affected'] - 5} más)"
                    st.caption(f"Filas afectadas: {rows_str}")
    
    if validation_result['warnings']:
        st.warning("**⚠️ Advertencias encontradas:** Campos opcionales con valores vacíos")
        
        with st.expander("🔍 Ver detalle de warnings", expanded=False):
            for warning in validation_result['warnings']:
                st.markdown(f"**{warning['type']}:** {warning['message']}")
    
    # Botón para descargar reporte
    if validation_result['errors'] or validation_result['warnings']:
        report_df = validator.get_validation_report()
        if not report_df.empty:
            csv = report_df.to_csv(index=False)
            st.download_button(
                "📥 Descargar Reporte de Validación",
                csv,
                "validation_report.csv",
                "text/csv",
                key='download_validation'
            )
    
    # Preview de 20 filas
    st.markdown("**Primeras 20 filas:**")
    st.caption("🔴 = Columnas REQUIRED | 🟡 = Columnas OPTIONAL")
    
    preview_df = df.head(20).copy()
    
    # Truncate long descriptions for preview
    if 'Descripción' in preview_df.columns:
        preview_df['Descripción'] = preview_df['Descripción'].apply(
            lambda x: str(x)[:60]+'...' if len(str(x)) > 60 else str(x)
        )
    
    st.dataframe(preview_df, use_container_width=True, height=400)
    
    # Guardar resultado de validación en session state
    st.session_state.validation_result = validation_result
    
    # Botones de acción
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Cancelar", type="secondary", key="cancel_import"):
            st.session_state.import_stage = 'select'
            st.session_state.preview_data = None
            st.session_state.validation_result = None
            st.rerun()
    
    with col2:
        # Deshabilitar si hay errores
        can_import = validation_result['is_valid']
        
        button_label = "✓ Confirmar Importación" if can_import else "❌ Importación Bloqueada"
        
        if st.button(
            button_label, 
            type="primary" if can_import else "secondary",
            key="confirm_import",
            disabled=not can_import
        ):
            if can_import:
                try:
                    with st.spinner("Validando estructura..."):
                        cleaned = self.data_cleaner.clean_data(df)
                        self.render_data_loading_with_progress(df, cleaned, source_name)
                    
                    st.session_state.import_stage = 'confirmed'
                    
                    # Mostrar warnings si los hay
                    if validation_result['warnings']:
                        st.warning(f"⚠️ Importación exitosa con {len(validation_result['warnings'])} advertencias")
                    else:
                        st.success(f"✅ **{len(st.session_state.df)} productos importados exitosamente**")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"**Error en validación:** {str(e)}")
                    st.caption("Verifica que el archivo tenga la estructura correcta")
