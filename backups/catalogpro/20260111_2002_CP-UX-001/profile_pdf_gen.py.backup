import time
import pandas as pd
from main import ImageManager, EnhancedPDFExporter
import io
from reportlab.lib.pagesizes import A4
# Mock streamlit session state for context
import streamlit as st
if 'pdf_columns' not in st.session_state:
    st.session_state.pdf_columns = 2
if 'logo' not in st.session_state:
    st.session_state.logo = None
if 'pdf_custom_title' not in st.session_state:
    st.session_state.pdf_custom_title = "Benchmark"
if 'pdf_custom_subtitle' not in st.session_state:
    st.session_state.pdf_custom_subtitle = "Performance Test"

# Subclassing to inject timing without modifying main.py yet
class InstrumentedPDFExporter(EnhancedPDFExporter):
    def generate_pdf_with_images_timed(self, df, business_name, currency, phone_number, user_email):
        start_total = time.time()
        
        self.business_name_for_footer = business_name
        self.phone_number_for_footer = phone_number
        self.email_for_footer = user_email
        buffer = io.BytesIO()
        
        # We need to measure how long _create_enhanced_product_cards takes
        # But _create_enhanced_product_cards internally calls image_manager.download_image
        # So we better wrap image_manager.download_image in a timer
        
        return start_total

def profiler():
    print("1. Loading Data...")
    # Use full dataset for real benchmark or sticking to subset if user wants quick feedback?
    # User asked for "Compare with 800 products".
    try:
        df = pd.read_excel('c:\\dev\\catalogpro\\ProductSample_Large.xlsx')
        print(f"   Rows: {len(df)}")
    except:
        print("   Generating sample data first...")
        import generate_large_sample
        df = pd.read_excel('c:\\dev\\catalogpro\\ProductSample_Large.xlsx')
    
    exporter = MediaInstrumentedPDFExporter()
    
    print("\n--- BENCHMARK: 800 ITEMS ---")
    
    # Run Optimized (Cold Cache) FIRST - CRITICAL TEST
    print("\n[Optimized Engine] Starting (Cold Cache - 800 items)...")
    if 'image_cache_persistent' in st.session_state:
        st.session_state['image_cache_persistent'] = {}
        exporter.image_manager.image_cache = st.session_state['image_cache_persistent']
        
    t2 = time.time()
    pdf_opt, stats_opt = exporter.generate_pdf_optimized(
        df, "Benchmark Inc", "S/", "123", "a@b.com", 
        progress_callback=lambda c, t, m: print(f"   Opt Progress: {c}%", end='\r')
    )
    t3 = time.time()
    opt_time = t3 - t2
    print(f"\n✅ Optimized Time (800 items): {opt_time:.2f}s")
    print(f"   Stats: {stats_opt}")

    # Run Legacy (Subset for comparison)
    subset_size = 20
    print(f"\n[Legacy Engine] Starting (Subset {subset_size} items)...")
    df_small = df.head(subset_size)
    
    t0 = time.time()
    try:
        pdf_legacy = exporter.generate_pdf_with_images(df_small, "Benchmark Inc", "S/", "123", "a@b.com")
    except Exception as e:
        print(f"Legacy failed: {e}")
    t1 = time.time()
    legacy_time_small = t1 - t0
    legacy_projected = legacy_time_small * (len(df) / subset_size)
    
    print(f"Legacy Time ({subset_size} items): {legacy_time_small:.2f}s")
    print(f"⚠️ Legacy Projected (800 items): {legacy_projected:.2f}s ({legacy_projected/60:.1f} min)")
    
    print(f"\n--- RESULTS SUMMARY ---")
    print(f"Optimized (800 items): {opt_time:.2f}s")
    print(f"Legacy (Projected): {legacy_projected:.2f}s")
    print(f"Speedup Factor: {legacy_projected/opt_time:.1f}x")
    
    # Run Optimized (Warm Cache)
    print("\n[Optimized Engine] Starting (Warm Cache)...")
    
    # Run Optimized (Warm Cache)
    print("\n[Optimized Engine] Starting (Warm Cache)...")
    t4 = time.time()
    pdf_opt_warm, stats_warm = exporter.generate_pdf_optimized(
        df, "Benchmark Inc", "S/", "123", "a@b.com"
    )
    t5 = time.time()
    opt_warm_time = t5 - t4
    print(f"Optimized Warm Time: {opt_warm_time:.2f}s")
    
    print(f"\n--- RESULTS SUMMARY ---")
    print(f"Legacy: {legacy_time:.2f}s")
    print(f"Optimized (Cold): {opt_time:.2f}s (Speedup: {legacy_time/opt_time:.1f}x)")
    print(f"Optimized (Warm): {opt_warm_time:.2f}s")
    
class MediaInstrumentedPDFExporter(EnhancedPDFExporter):
    # Helper to avoid altering main class methods, just inherits
    pass

if __name__ == "__main__":
    if 'image_cache_persistent' not in st.session_state:
        st.session_state['image_cache_persistent'] = {}
    profiler()
