---
name: graphql-architect
description: Design and review GraphQL schemas, resolvers, mutations, pagination, and data-loading patterns. Use when building or refactoring GraphQL APIs, adding fields, fixing resolver design, or improving GraphQL performance and safety.
metadata:
  version: "1.0.0"
  tags: "graphql, api-design, schema, resolvers"
---

# GraphQL Architect

Design GraphQL APIs that are explicit, stable, performant, and easy for clients to consume.

## Use This Skill For

- New GraphQL schemas or modules
- Resolver and mutation design
- Pagination, filtering, and search
- N+1 reduction and batching
- Authorization, validation, and error-shaping for GraphQL

## Workflow

### 1. Read the Existing GraphQL Shape

- Inspect schema files, resolver structure, and context setup
- Find at least 3 existing resolver or schema patterns before adding new ones
- Match the dominant conventions for naming, nullability, and error handling

### 2. Design the Contract Before Implementation

- Start from client use cases, not database tables
- Define the schema shape first: queries, mutations, input types, output types
- Keep types stable and explicit; avoid ambiguous fields or overloaded mutations

### 3. Implement Resolver Boundaries Cleanly

- Keep resolvers thin; push business logic into services
- Validate inputs at the API boundary
- Enforce authorization close to the entry point
- Avoid leaking database details directly into schema types

### 4. Control Performance Early

- Use batching/data loaders where related fields fan out
- Prefer cursor pagination over ad hoc offset pagination for large lists
- Avoid fields that trigger hidden expensive work without clear client intent
- Measure N+1 risk any time a list returns nested entities

### 5. Verify Client Ergonomics

- Field names should describe domain concepts, not storage details
- Nullability must reflect real guarantees
- Mutation results should return enough data for immediate UI updates
- Errors should be consistent and actionable

## Core Rules

- Queries read; mutations change state
- Input types and output types should be distinct
- Keep mutation names verb-first and specific
- Prefer explicit enums over magic strings
- Add deprecation before removal when evolving schemas

## Common Pitfalls

- Catch-all mutations like `updateThing`
- Returning giant nested objects by default
- Resolver logic that talks directly to the database and the network in one layer
- Hiding authorization failures behind nulls without a deliberate contract
- Adding fields without thinking through cache keys or client churn

## Output

When using this skill, produce:

- Proposed schema/resolver changes
- Notes on performance and authorization implications
- Any migration or client-impact risks
