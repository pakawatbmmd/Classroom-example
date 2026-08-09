# Role
Act as an expert software architect and technical writer. 

# Context
I am building a "Diabetes Risk Scoring System" implemented using a strict 4-Tier Architecture consisting of:
1. Data Access Layer
2. Business Logic Layer
3. Orchestration Layer 
4. Presentation Layer 

# Task
Generate a clean, highly structured Technical Design Document (TDD) optimized for both developers and non-technical domain stakeholders. Do not write any actual Python or implementation code. Instead, provide the structural blueprint.

# Deliverables

## 1. System Architecture Overview
For each core workflow listed below, show the exact flow of class and method calls using clean text-based sequence diagrams. 
- Use vertical lines to represent active classes/components.
- Structure the horizontal sequence order exactly as follows from left to right: [User] -> [Presentation Layer] -> [Orchestration Layer] -> [Business Logic Layer] -> [Data Access Layer].

## 2. Method Specification
Create a comprehensive method specification section written in plain, accessible language so non-coding domain experts can easily cross-reference it with the final codebase. 
- Separate this section cleanly by Layer.
- For each layer, list the relevant Class(es).
- For every class, break down its functions/methods using a simple markdown Input-Process-Output (IPO) table with these 4 columns: | Method Name | Inputs (What it needs) | Process (What it does inside) | Outputs (What it delivers) |.

# Reference files to Map
- Attached SRS.md file: Software requirement specification document
- Attached app.py file: Python implementation
