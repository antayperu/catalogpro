import pandas as pd
from main import DataHandler, DataCleaner, EnhancedPDFExporter
import streamlit as st

# Mock session state
if 'pdf_columns' not in st.session_state:
    st.session_state.pdf_columns = 2
if 'logo' not in st.session_state:
    st.session_state.logo = None
if 'pdf_custom_title' not in st.session_state:
    st.session_state.pdf_custom_title = "Catálogo Enterprise"
if 'pdf_custom_subtitle' not in st.session_state:
    st.session_state.pdf_custom_subtitle = "Test de Generación Jerárquica"

def test_pipeline():
    print("1. Loading Enterprise Sample...")
    handler = DataHandler()
    # We use valid columns including the new ones
    df = pd.read_excel('c:\\dev\\catalogpro\\ProductSample_Enterprise.xlsx')
    
    print("2. Cleaning Data...")
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean_data(df)
    
    print(f"   Rows: {len(cleaned_df)}")
    print(f"   Columns: {cleaned_df.columns.tolist()}")
    print("   Types:")
    print(cleaned_df.dtypes)
    
    print("3. Generating PDF...")
    exporter = EnhancedPDFExporter()
    pdf_bytes = exporter.generate_pdf_with_images(
        cleaned_df, 
        "Empresa Test", 
        "S/", 
        "999888777", 
        "test@empresa.com"
    )
    
    with open("test_output_enterprise.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    print(f"4. PDF Generated Successfully! Size: {len(pdf_bytes)} bytes")

if __name__ == "__main__":
    try:
        test_pipeline()
        print("✅ SUCCESS: Pipeline Verified")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
