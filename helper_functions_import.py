def _render_preview_workflow(self, df, source_name):
    """CP-UX-010 v3: Preview workflow before confirming import"""
    st.markdown("---")
    st.markdown("## 📊 Preview de Importación")
    st.caption(f"Fuente: {source_name}")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
            st.metric("Filas detectadas", len(df))
        
        with col2:
            st.metric("Columnas detectadas", len(df.columns))
        
        with col3:
            empty_count = df.isnull().sum().sum()
            st.metric(
                "Campos vacíos", 
                empty_count,
                delta="⚠ Revisar" if empty_count > 0 else "✓ OK",
                delta_color="inverse" if empty_count > 0 else "normal"
            )
        
        # Preview first 20 rows
        st.markdown("**Primeras 20 filas:**")
        preview_df = df.head(20).copy()
        
        # Truncate long descriptions for preview
        if 'Descripción' in preview_df.columns:
            preview_df['Descripción'] = preview_df['Descripción'].apply(
                lambda x: str(x)[:60]+'...' if len(str(x)) > 60 else str(x)
            )
        
        st.dataframe(preview_df, use_container_width=True, height=400)
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("← Cancelar", type="secondary", key="cancel_import"):
                st.session_state.import_stage = 'select'
                st.session_state.preview_data = None
                st.rerun()
        
        with col2:
            if st.button("✓ Confirmar Importación", type="primary", key="confirm_import"):
                try:
                    # Validate and clean
                    with st.spinner("Validando estructura..."):
                        cleaned = self.data_cleaner.clean_data(df)
                        self.render_data_loading_with_progress(df, cleaned, source_name)
                    
                    st.session_state.import_stage = 'confirmed'
                    st.success(f"✅ **{len(st.session_state.df)} productos importados exitosamente**")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"**Error en validación:** {str(e)}")
                    st.caption("Verifica que el archivo tenga la estructura correcta")
    
    # CP-UX-011: Removed _render_data_table_premium() - Not in FRD
    # Data preview is in Catalog tab (S-04), not in Load tab (S-02)
