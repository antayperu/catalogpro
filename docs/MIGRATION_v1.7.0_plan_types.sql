-- SQL Migration for CatalogPro v1.7.0
-- Adds support for date-based Free and Premium plans
-- Run this in your Supabase SQL Editor

-- First, we need to drop the existing CHECK constraint
-- Then add a new one that includes the new plan types

-- Step 1: Drop the old constraint
ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_plan_type;

-- Step 2: Add new constraint that includes date-based plans
ALTER TABLE users
ADD CONSTRAINT valid_plan_type CHECK (
  plan_type IN (
    'Free',
    'Free (Cantidad)',
    'Free (Fecha)',
    'Premium',
    'Premium (Cantidad)',
    'Premium (Fecha)',
    'Cantidad',
    'Tiempo'
  )
);

-- Verification query:
-- SELECT column_name, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'users' AND column_name = 'plan_type';
