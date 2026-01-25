    
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
    
    def _render_data_table_premium(self):
        """CP-UX-010 v3: Premium data table with toolbar and pagination"""
        df = st.session_state.df
        
        st.markdown("---")
        st.markdown(f"### 📦 Datos Cargados")
        st.caption(f"{len(df)} productos en total")
        
        # Toolbar
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            search = st.text_input(
                "Buscar",
                placeholder="🔎 Buscar productos...",
                key="search_products",
                label_visibility="collapsed"
            )
        
        with col2:
            filter_option = st.selectbox(
                "Filtros",
                ["Todos", "Con stock", "Sin stock"],
                key="filter_stock",
                label_visibility="collapsed"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Ordenar",
                ["Nombre", "Precio ↑", "Precio ↓", "Stock ↑", "Stock ↓"],
                key="sort_by",
                label_visibility="collapsed"
            )
        
        with col4:
            page_size = st.selectbox(
                "Filas",
                [20, 50, 100],
                key="page_size",
                label_visibility="collapsed"
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Search filter
        if search:
            mask = (
                filtered_df['Producto'].astype(str).str.contains(search, case=False, na=False) |
                filtered_df['Descripción'].astype(str).str.contains(search, case=False, na=False)
            )
            if 'Código' in filtered_df.columns:
                mask |= filtered_df['Código'].astype(str).str.contains(search, case=False, na=False)
            filtered_df = filtered_df[mask]
        
        # Stock filter
        if filter_option == "Con stock":
            filtered_df = filtered_df[filtered_df['Stock'] > 0]
        elif filter_option == "Sin stock":
            filtered_df = filtered_df[filtered_df['Stock'] == 0]
        
        # Sorting
        if sort_by == "Nombre":
            filtered_df = filtered_df.sort_values('Producto')
        elif sort_by == "Precio ↑":
            filtered_df = filtered_df.sort_values('Precio', ascending=True)
        elif sort_by == "Precio ↓":
            filtered_df = filtered_df.sort_values('Precio', ascending=False)
        elif sort_by == "Stock ↑":
            filtered_df = filtered_df.sort_values('Stock', ascending=True)
        elif sort_by == "Stock ↓":
            filtered_df = filtered_df.sort_values('Stock', ascending=False)
        
        # Pagination
        total_rows = len(filtered_df)
        total_pages = math.ceil(total_rows / page_size) if total_rows > 0 else 1
        
        # Page selector
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.button("← Anterior", disabled=st.session_state.current_page == 1, key="prev_page"):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col_page:
            st.caption(f"Página {st.session_state.current_page} de {total_pages}")
        
        with col_next:
            if st.button("Siguiente →", disabled=st.session_state.current_page >= total_pages, key="next_page"):
                st.session_state.current_page += 1
                st.rerun()
        
        # Calculate slice
        start_idx = (st.session_state.current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        # Display table
        if total_rows > 0:
            page_df = filtered_df.iloc[start_idx:end_idx]
            
            # Truncate descriptions for table view
            display_df = page_df.copy()
            if 'Descripción' in display_df.columns:
                display_df['Descripción'] = display_df['Descripción'].apply(
                    lambda x: str(x)[:80]+'...' if len(str(x)) > 80 else str(x)
                )
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600
            )
            
            # Footer
            st.caption(f"Mostrando {start_idx + 1}-{end_idx} de {total_rows} productos")
        else:
            st.info("No se encontraron productos con los filtros aplicados")
        
        # CP-UX-010 v3: Structure example in collapsible expander
        with st.expander("📘 ¿Qué estructura debe tener mi archivo?", expanded=False):
            st.caption("Tu archivo debe contener las siguientes columnas en este orden:")
            ex = pd.DataFrame({
                'Línea': ['ELECTRO'],
                'Familia': ['COMPUTO'],
                'Grupo': ['LAPTOPS'],
                'Marca': ['DELL'],
                'Código': ['DL-5520'],
                'Producto': ['Laptop Inspiron 15'],
                'Descripción': ['Core i5 8GB RAM'],
                'Unidad': ['UND'],
                'Precio': [1299.99],
                'Stock': [50],
                'ImagenURL': ['https://ejemplo.com/lapt.jpg']
            })
            st.dataframe(ex, use_container_width=True)
            st.caption("💡 **Tip:** Usa este ejemplo como plantilla para estructurar tu inventario")
