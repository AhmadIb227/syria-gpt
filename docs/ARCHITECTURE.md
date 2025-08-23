# Clean Architecture Implementation

## Overview

This project implements Uncle Bob's Clean Architecture pattern for a robust, maintainable authentication system.

## Layers

### 1. Domain Layer (Innermost)
**Location**: `/domain/`

**Responsibilities**:
- Core business entities and rules
- Repository interfaces
- Service interfaces
- Business use cases

**Key Files**:
- `entities/user.py` - User domain entity with business logic
- `interfaces/user_repository.py` - Repository contract
- `interfaces/oauth_provider.py` - OAuth provider contract
- `use_cases/auth_use_cases.py` - Authentication business logic

### 2. Application Layer
**Location**: `/application/`

**Responsibilities**:
- Orchestrates use cases
- Application-specific business rules
- Coordinates between domain and infrastructure

**Key Files**:
- `auth_application_service.py` - Application service orchestrator

### 3. Infrastructure Layer
**Location**: `/infrastructure/`

**Responsibilities**:
- Database implementations
- External service integrations
- Framework-specific code

**Key Files**:
- `database/user_repository_impl.py` - SQLAlchemy repository implementation
- `external_services/google_oauth_provider.py` - Google OAuth implementation
- `external_services/facebook_oauth_provider.py` - Facebook OAuth implementation
- `services/` - Infrastructure services (password, token, email)

### 4. Presentation Layer (Outermost)
**Location**: `/presentation/`

**Responsibilities**:
- HTTP request/response handling
- Input validation
- Dependency injection

**Key Files**:
- `api/auth_controller.py` - HTTP controllers
- `schemas/auth_schemas.py` - Request/response models
- `dependencies.py` - Dependency injection

## Key Principles Applied

### 1. Dependency Rule
- Inner layers don't depend on outer layers
- Dependencies point inward
- Interfaces in inner layers, implementations in outer layers

### 2. Separation of Concerns
- Each layer has a single responsibility
- Business logic isolated from infrastructure
- Clean boundaries between layers

### 3. Repository Pattern
- Abstracts data access
- Domain defines interfaces
- Infrastructure provides implementations
- Easy to test and swap implementations

### 4. Dependency Injection
- Loose coupling between components
- Dependencies injected at runtime
- Easy to mock for testing

## Benefits

1. **Testability**: Easy unit testing of business logic
2. **Maintainability**: Clear structure and responsibilities
3. **Flexibility**: Easy to change implementations
4. **Independence**: Framework-agnostic business logic
5. **Scalability**: Clean structure supports growth

## Configuration
**Location**: `/config/`

Contains application configuration, database models, and cross-cutting concerns.