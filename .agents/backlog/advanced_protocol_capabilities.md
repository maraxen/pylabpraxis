# Advanced Protocol Capabilities

**Priority**: High (Value Add)
**Status**: Deferred / Future (Formerly Phases 5-6 of Capability Tracking)
**Created**: 2026-01-07

---

## Overview

These advanced capabilities were originally planned as Phases 5 & 6 of the Capability Tracking system. They represent significant value adds for protocol reliability and resource management.

---

## 1. Deep Protocol Inspection

### 1.1 Call Graph Analysis

- [ ] Extract function calls within protocol body
- [ ] Identify nested protocol function calls
- [ ] Build dependency DAG for protocol execution order

### 1.2 Resource Flow Analysis

- [ ] Track PLR resource usage through function body
- [ ] Identify resource allocation/deallocation patterns
- [ ] Detect potential resource conflicts

---

## 2. Resource Capability & Constraint Matching

### 2.1 Resource Requirement Extraction

- [ ] Extract specific resource constraints from protocols (e.g., `num_wells`, `well_volume`, `bottom_type`)
- [ ] Infer required resource capabilities (e.g., "must be pierceable", "must be stackable")

### 2.2 Inventory Matching Service

- [ ] Match extracted protocol resource requirements against available Lab Assets (inventory)
- [ ] Validate if physical assets assigned to a protocol run satisfy the technical constraints of the protocol

### 2.3 Placement Validation

- [ ] Real-time validation of resource placement on deck based on physical constraints and protocol needs
