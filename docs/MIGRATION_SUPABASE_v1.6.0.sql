-- SQL Migration Script for CatalogPro Enhanced v1.6.0
-- Run this in your Supabase SQL Editor to add missing configuration columns

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS columns_catalog INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS pdf_columns INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS brand_primary TEXT DEFAULT '#2c3e50',
ADD COLUMN IF NOT EXISTS brand_secondary TEXT DEFAULT '#e74c3c',
ADD COLUMN IF NOT EXISTS brand_accent TEXT DEFAULT '#3498db',
ADD COLUMN IF NOT EXISTS brand_text TEXT DEFAULT '#2c3e50',
ADD COLUMN IF NOT EXISTS pdf_layout TEXT DEFAULT 'Profesional (v2)';

-- Verification:
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'users';
