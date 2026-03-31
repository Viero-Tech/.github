---
applyTo: "**/*.prisma"
excludeAgent: "coding-agent"
---
# Viero Centralized Prisma Schema

## Stack
Prisma 6.19, PostgreSQL 16, TypeScript

## Schema Conventions
- IDs: Int @id @default(autoincrement()). Never UUID.
- Soft delete: isActive Boolean @default(true) on every model. Never hard delete.
- Timestamps: createdAt DateTime @default(now()) + updatedAt DateTime @updatedAt
- Bilingual: name + nameAr for user-facing fields where needed
- Relations: explicit @relation(fields: [...], references: [id])
- Enums: defined in schema, imported from @prisma/client
- Indexes: @@index on frequently queried fields

## Flag as CRITICAL
- Missing isActive field on any model
- Missing createdAt/updatedAt on any model
- UUID as primary key
- Hard delete patterns
- Missing @relation on foreign keys
- Circular relations without explicit naming

## Flag as IMPORTANT
- Missing @@index on foreign key fields
- Nullable fields that should have defaults
- Missing bilingual fields on user-facing models
- Enum values not in UPPER_SNAKE_CASE
