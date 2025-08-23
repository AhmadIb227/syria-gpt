# Clean Architecture Reorganization Plan

## Current Structure Analysis

### ✅ Well-Organized Layers (Keep as-is)
- **Domain Layer**: `domain/` - Well structured with entities, interfaces, use cases
- **Infrastructure Layer**: `infrastructure/` - Good separation of database, services, external services
- **Presentation Layer**: `presentation/` - Proper API controllers and schemas
- **Application Layer**: `application/` - Application services well placed

### 📁 Files to Categorize and Reorganize

#### **1. Core Application Files (Root Level)**
```
📂 src/ (NEW - Main source code)
├── 📂 domain/           [EXISTING - KEEP]
├── 📂 application/      [EXISTING - KEEP] 
├── 📂 infrastructure/   [EXISTING - KEEP]
├── 📂 presentation/     [EXISTING - KEEP]
└── 📂 shared/          [NEW - Shared utilities]
```

#### **2. Configuration & Setup Files**
```
📂 config/ (Reorganize)
├── 📄 settings.py        [KEEP]
├── 📄 database.py        [KEEP]
├── 📄 logging_config.py  [KEEP]
├── 📄 exceptions.py      [KEEP]
└── 📄 __init__.py        [KEEP]

📂 deployment/
├── 📄 Dockerfile        [MOVE FROM ROOT]
├── 📄 docker-compose.yml [MOVE FROM ROOT]
├── 📂 docker/           [KEEP]
└── 📄 requirements.txt  [MOVE FROM ROOT]
```

#### **3. Database & Migrations**
```
📂 database/
├── 📂 migrations/       [MOVE alembic/]
│   ├── 📄 alembic.ini   [MOVE FROM ROOT]
│   ├── 📄 env.py
│   └── 📂 versions/
└── 📂 models/           [MOVE config/model.py]
```

#### **4. Tools & Scripts**
```
📂 scripts/
├── 📄 migrate.py        [MOVE FROM ROOT]
├── 📄 health_check.py   [MOVE FROM ROOT]
└── 📂 utils/            [KEEP]
    ├── 📄 migration_utility.py
    └── 📄 migration_helpers.py
```

#### **5. Testing**
```
📂 tests/               [KEEP - Well organized]
├── 📂 unit/
├── 📂 integration/
├── 📄 conftest.py
└── 📄 README.md

📂 tests-tools/         [NEW - Test utilities]
├── 📄 test_postgresql_integration.py [MOVE FROM ROOT]
├── 📄 test_comprehensive_stability.py [MOVE FROM ROOT]
├── 📄 verify_database.py [MOVE FROM ROOT]
└── 📄 run_tests.py     [MOVE FROM ROOT]
```

#### **6. Documentation**
```
📂 docs/               [KEEP]
├── 📄 ARCHITECTURE.md  [MOVE FROM ROOT]
├── 📄 README.md        [KEEP ROOT + COPY]
├── 📄 MIGRATION_UTILITY.md
└── 📄 TEST_SUMMARY_REPORT.md [MOVE FROM ROOT]
```

#### **7. Project Root (Minimal)**
```
📄 main.py             [KEEP - Entry point]
📄 setup.py            [KEEP - Package setup]
📄 pytest.ini          [KEEP - Test configuration]
📄 .env.example        [NEW - Environment template]
📄 README.md           [KEEP - Project overview]
```

## Clean Architecture Layers

### Domain Layer (Core Business Logic)
```
📂 domain/
├── 📂 entities/
│   ├── 📄 user.py           ✅ Core business entities
│   └── 📄 __init__.py
├── 📂 value_objects/        [NEW - Add if needed]
├── 📂 interfaces/           ✅ Repository interfaces
│   ├── 📄 user_repository.py
│   ├── 📄 auth_service.py
│   └── 📄 oauth_provider.py
├── 📂 use_cases/            ✅ Business logic
│   ├── 📄 auth_use_cases.py
│   └── 📄 __init__.py
└── 📂 exceptions/           [NEW - Domain exceptions]
    └── 📄 domain_exceptions.py
```

### Application Layer (Use Case Orchestration)
```
📂 application/
├── 📂 services/             ✅ Application services
│   ├── 📄 auth_application_service.py
│   └── 📄 __init__.py
├── 📂 dto/                  [NEW - Data Transfer Objects]
│   ├── 📄 auth_dto.py
│   └── 📄 __init__.py
└── 📂 commands/             [NEW - Command pattern]
    ├── 📄 auth_commands.py
    └── 📄 __init__.py
```

### Infrastructure Layer (External Dependencies)
```
📂 infrastructure/
├── 📂 database/             ✅ Database implementations
│   ├── 📂 repositories/     [REORGANIZE]
│   │   ├── 📄 user_repository_impl.py
│   │   ├── 📄 password_reset_repository.py
│   │   └── 📄 two_factor_auth_repository_impl.py
│   ├── 📂 models/           [MOVE FROM config/]
│   │   ├── 📄 database_models.py
│   │   └── 📄 __init__.py
│   └── 📄 __init__.py
├── 📂 services/             ✅ Infrastructure services
│   ├── 📄 email_service.py
│   ├── 📄 password_service.py
│   ├── 📄 token_service.py
│   └── 📄 __init__.py
├── 📂 external_services/    ✅ Third-party integrations
│   ├── 📄 google_oauth_provider.py
│   ├── 📄 facebook_oauth_provider.py
│   └── 📄 __init__.py
└── 📄 __init__.py
```

### Presentation Layer (API & UI)
```
📂 presentation/
├── 📂 api/                  ✅ REST API controllers
│   ├── 📂 controllers/      [REORGANIZE]
│   │   ├── 📄 auth_controller.py
│   │   └── 📄 __init__.py
│   ├── 📂 middleware/       [NEW]
│   │   ├── 📄 auth_middleware.py
│   │   ├── 📄 error_middleware.py
│   │   └── 📄 __init__.py
│   └── 📄 __init__.py
├── 📂 schemas/              ✅ Request/Response schemas
│   ├── 📄 auth_schemas.py
│   ├── 📄 common_schemas.py [NEW]
│   └── 📄 __init__.py
├── 📄 dependencies.py       ✅ Dependency injection
└── 📄 __init__.py
```

### Shared/Common Layer
```
📂 shared/                   [NEW]
├── 📂 constants/            [NEW]
│   ├── 📄 app_constants.py
│   └── 📄 __init__.py
├── 📂 utils/                [MOVE FROM ROOT]
│   ├── 📄 migration_utility.py
│   ├── 📄 migration_helpers.py
│   └── 📄 __init__.py
├── 📂 exceptions/           [NEW]
│   ├── 📄 base_exceptions.py
│   └── 📄 __init__.py
└── 📄 __init__.py
```

## Benefits of This Organization

### 1. **Dependency Flow** ✅
- Domain ← Application ← Infrastructure
- Domain ← Application ← Presentation
- No circular dependencies

### 2. **Testability** ✅
- Each layer can be tested in isolation
- Mock interfaces easily
- Clear test categories by layer

### 3. **Maintainability** ✅
- Related files grouped together
- Clear separation of concerns
- Easy to locate and modify features

### 4. **Scalability** ✅
- Easy to add new features
- Clear patterns to follow
- Minimal impact when changing layers

### 5. **Repository Pattern Preservation** ✅
- Interface definitions in domain
- Implementations in infrastructure
- Clear abstraction boundaries