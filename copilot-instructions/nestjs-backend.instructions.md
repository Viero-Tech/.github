---
applyTo: "**/*.ts"
excludeAgent: "coding-agent"
---
# Viero NestJS Backend

## Stack
NestJS 11, Prisma 6.19, PostgreSQL 16, TypeScript, class-validator, Swagger

## Module Structure
src/app/<module>/ with: module.ts, controller.ts, service.ts, dto/, responses/

## Required Patterns
- Auth: @HasPermissions(['permName'], 'or') on every endpoint
- User context: @User() user: UserMeta decorator
- Params: @Param('id', new ParseIntPipe()) id: number
- DTOs: class-validator decorators + @ApiProperty() for Swagger
- Prisma: injected as private prisma: PrismaService
- Pagination: PaginationDto (skip/take), response { data: T[], rows, take, skip }
- Errors: throw new HttpErrorByCode[400]({ error: 'message' })
- Swagger: @ApiTags, @ApiOkResponse, @ApiCreatedResponse on every endpoint
- Logger: private readonly logger = new Logger(ServiceName.name)
- New modules must be imported in app.module.ts
- Env vars must be validated at startup via ConfigModule

## Flag as CRITICAL
- Missing @HasPermissions on any endpoint
- Raw SQL without parameterization
- Hard delete instead of soft delete (isActive = false)
- Missing ParseIntPipe on ID params
- Logging passwords, tokens, API keys, PII
- eval() or new Function() with any input
- Concurrent writes to same entity without $transaction or optimistic locking
- Read-then-write patterns without proper transaction isolation

## Flag as IMPORTANT
- Missing error handling on external API/service calls
- Missing Swagger decorators on endpoints
- Environment variables accessed without validation or defaults
