# Milestone 5.6 Operational Debt Register

## 1. Production Improvements
* **Debt:** Advanced metric aggregation (e.g., Prometheus metrics export) is not yet natively integrated into the core orchestration layer.
* **Impact:** Limits deep observability in high-scale environments.
* **Status:** Acceptable for current milestone. Scheduled for future operational enhancements.

## 2. Deployment Improvements
* **Debt:** Unified Docker Compose environment does not yet encapsulate complex local network proxying for the frontend/backend divide.
* **Impact:** Requires developers to run separate terminal processes.
* **Status:** Acceptable. Local workflow is documented and functional.

## 3. Operational Enhancements
* **Debt:** AI Provider fallback chaining is manual rather than automatic (e.g., failing over from Ollama to OpenAI automatically on failure).
* **Impact:** Service degradation if the primary provider drops.
* **Status:** Acceptable. Provider failure correctly propagates standard exceptions rather than crashing the system.

**Conclusion:**
There is **no critical operational debt**. The items logged represent non-blocking maturity enhancements, not fundamental flaws.
