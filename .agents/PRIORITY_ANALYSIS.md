# Priority Analysis - Dec 13, 2025

**Generated**: 2025-12-13
**Purpose**: Analyze all .agents documentation to determine highest priority next steps

---

## 🎯 Executive Summary

**Current State**:
- ✅ Test Infrastructure: EXCELLENT (98.6% pass rate, 1373/1393 tests passing)
- ⚠️ Code Coverage: NEEDS WORK (40-42% actual, target: 80%)
- ✅ Frontend Auth: COMPLETE (JWT-based, production-ready)
- ⚠️ Frontend Testing: MINIMAL (5% coverage)

**Highest Priority Focus**: **Backend Code Coverage** - Critical modules need testing before production

---

## 🔥 CRITICAL PRIORITY (Do These First)

### 1. **Complete Protocol Decorator Test Coverage** ⭐⭐⭐⭐⭐
**Module**: `praxis/backend/core/decorators/protocol_decorator.py`
- **Current**: 24% coverage + partial control command coverage
- **Target**: 80%+
- **Impact**: **CRITICAL** - This wraps ALL protocol execution. Every protocol run goes through this code.
- **Status**: Foundation laid (13/23 tests passing)
- **Blocker**: Decorator registration and context mocking complexity
- **Estimated Effort**: 4-6 hours (need to fix 10 failing wrapper tests)
- **Why Critical**: Without this, protocol execution errors may go undetected in production

**Action Items**:
- [ ] Fix the 10 failing wrapper execution tests
- [ ] Test async/sync function execution paths
- [ ] Test error serialization (Pydantic, Resource, Dict, etc.)
- [ ] Test state parameter injection
- [ ] Achieve 80%+ coverage

### 2. **Orchestrator Execution Coverage** ⭐⭐⭐⭐⭐
**Module**: `praxis/backend/core/orchestrator/execution.py`
- **Current**: 21% coverage
- **Target**: 80%+
- **Size**: 175 lines
- **Impact**: **CRITICAL** - Main protocol execution engine
- **Current Gaps**: Error handling, state management, step execution
- **Estimated Effort**: 6-8 hours

**Why Critical**: This is the heart of the system - executes every protocol step. Bugs here affect all protocol runs.

**Action Items**:
- [ ] Test `execute_protocol_step` function
- [ ] Test error handling and recovery
- [ ] Test state updates during execution
- [ ] Test cancellation handling
- [ ] Test resource cleanup

---

## 🚨 HIGH PRIORITY (Essential for Production)

### 3. **Scheduler Service Coverage** ⭐⭐⭐⭐
**Module**: `praxis/backend/services/scheduler.py`
- **Current**: 22% coverage
- **Target**: 80%+
- **Size**: 176 lines
- **Impact**: HIGH - Job scheduling, queue management
- **Estimated Effort**: 4-6 hours

**Why High**: Scheduling failures can cause protocol runs to be lost or delayed.

### 4. **User Service Coverage** ⭐⭐⭐⭐
**Module**: `praxis/backend/services/user.py`
- **Current**: 28% coverage
- **Target**: 80%+
- **Size**: 116 lines
- **Impact**: HIGH - Authentication, authorization, password hashing
- **Estimated Effort**: 3-4 hours

**Why High**: Security-critical code - auth bugs can expose the entire system.

### 5. **Auth API Coverage** ⭐⭐⭐⭐
**Module**: `praxis/backend/api/auth.py`
- **Current**: 57% coverage
- **Target**: 80%+
- **Size**: 49 lines
- **Impact**: HIGH - Login/logout flows, token refresh
- **Estimated Effort**: 2-3 hours

**Why High**: Entry point for all authenticated requests.

---

## 🟡 MEDIUM PRIORITY (Should Do Soon)

### 6. **Fix Remaining 20 Test Failures**
- **Current**: 98.6% pass rate (acceptable, but not perfect)
- **Categories**:
  - 6 scheduler API tests (redirect/validation)
  - 9 well_outputs tests (IntegrityError/ValidationError)
  - 5 misc tests
- **Estimated Effort**: 4-6 hours
- **Impact**: Increases confidence, may reveal edge case bugs

### 7. **Frontend Unit Testing** ⭐⭐⭐
- **Current**: 5% coverage (116 tests created but minimal overall coverage)
- **Target**: 60%+ (reasonable for Angular)
- **Impact**: MEDIUM - Catches UI bugs early, enables refactoring
- **Estimated Effort**: 8-12 hours (need comprehensive component tests)

**Areas Needing Tests**:
- Asset management components
- Protocol library components
- Settings components
- All guards and interceptors (some done)

---

## 🟢 LOWER PRIORITY (Can Wait)

### 8. **Medium Coverage Services**
- `services/deck.py` (26%)
- `services/protocol_definition.py` (21%)
- `services/protocols.py` (20%)
- `services/discovery_service.py` (21%)
- `services/entity_linking.py` (18%)

### 9. **Frontend Features**
- F2.1: Asset definitions tab
- F2.2: Protocol details view
- F2.3: Dynamic protocol parameters
- F3.1: Visualizer feature

### 10. **Utility Coverage**
- `utils/sanitation.py` (13%)
- `utils/plr_inspection.py` (22%)

---

## 📊 Recommended Action Plan

### Week 1 Focus: **Backend Coverage - Critical Modules**
**Goal**: Get production-critical modules to 80% coverage

**Day 1-2**: Protocol Decorator (CRITICAL)
- Fix 10 failing wrapper tests
- Add missing coverage for error serialization
- Target: 80%+ coverage

**Day 3-4**: Orchestrator Execution (CRITICAL)
- Test protocol step execution
- Test error handling paths
- Target: 80%+ coverage

**Day 5**: Scheduler Service (HIGH)
- Test job scheduling
- Test queue management
- Target: 80%+ coverage

### Week 2 Focus: **Auth & User Management**
**Goal**: Secure authentication layer

**Day 1-2**: User Service
- Test password hashing
- Test token generation
- Test permissions

**Day 3**: Auth API
- Test login/logout
- Test token refresh

**Day 4-5**: Test Failures
- Fix remaining 20 test failures
- Achieve 100% pass rate

### Week 3+: **Medium Priority**
- Additional service coverage
- Frontend unit testing
- Feature development

---

## 🎯 Success Metrics

### Immediate Goals (Next 2 Weeks)
- [ ] Protocol decorator: 80%+ coverage
- [ ] Orchestrator execution: 80%+ coverage
- [ ] Scheduler: 80%+ coverage
- [ ] User service: 80%+ coverage
- [ ] Auth API: 80%+ coverage
- [ ] Test pass rate: 100% (fix 20 failures)

### Medium-Term Goals (1 Month)
- [ ] Overall backend coverage: 65%+
- [ ] All critical modules: 80%+
- [ ] All high-priority modules: 70%+
- [ ] Frontend coverage: 40%+

### Long-Term Goals (2-3 Months)
- [ ] Overall backend coverage: 80%+
- [ ] Frontend coverage: 60%+
- [ ] E2E test suite established
- [ ] All features complete

---

## 💡 Key Insights from Documentation Review

### What's Working Well ✅
1. **Test Infrastructure**: 98.6% pass rate is excellent
2. **WebSocket Coverage**: 87% achieved (great example to follow)
3. **Test Performance**: Parallelization and optimization working
4. **Frontend Auth**: Production-ready JWT implementation

### What Needs Attention ⚠️
1. **Protocol Decorator**: Most critical module, only 24% covered
2. **Orchestrator Execution**: Heart of system, only 21% covered
3. **Security Modules**: User/Auth services need better coverage
4. **Overall Coverage**: 40% is too low for production (target: 80%)

### Strategic Decisions 🎯
1. **Focus on Backend First**: Critical path for production
2. **Test Critical Modules**: Protocol execution > Nice-to-have features
3. **Incremental Progress**: WebSocket showed good methodology (direct function testing, mocking complexity away)
4. **Don't Chase 100%**: 80% is a good target, focus on critical paths

---

## 📝 Recommendations

### For Next Session
**STRONGLY RECOMMEND**: Start with Protocol Decorator wrapper tests
- These are partially done (13/23 passing)
- Most critical module
- Foundation already laid
- Can achieve quick win by fixing the 10 failing tests

**Alternative** (if decorator too complex): Orchestrator Execution
- Also critical
- May be easier to test (less mocking complexity)
- Clear test patterns from existing orchestrator tests

### Testing Strategy
Based on WebSocket success:
1. **Direct function testing** (avoid full app integration when possible)
2. **Mock external dependencies** aggressively
3. **Patch slow operations** (asyncio.sleep, etc.)
4. **Focus on critical paths** first (happy path, then errors)

### Don't Do (Low ROI)
- ❌ Chase 100% coverage on utils
- ❌ Fix all 20 test failures immediately (98.6% is fine)
- ❌ Start new features before critical modules tested
- ❌ E2E testing before unit coverage improved

---

**Bottom Line**:
**Focus on Protocol Decorator → Orchestrator Execution → Scheduler/User/Auth**
These 5 modules are critical for production stability. Everything else can wait.
