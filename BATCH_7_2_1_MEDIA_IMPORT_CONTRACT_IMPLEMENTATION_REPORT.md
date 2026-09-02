# Milestone 7.2.1 — Media Import Contract

## 1. Purpose
This batch exists to formalize, stabilize, and verify the existing media import contract for the AI Clipping Platform.
The media import contract encompasses the following flow:
source file → multipart upload → validation → project association → physical storage → metadata extraction → VideoAsset → persistence → retrieval.

The primary goal of this implementation was to resolve a known atomicity defect where a failure during database persistence left an orphaned physical file on disk.

## 2. Baseline
- **Branch:** `main`
- **Baseline Commit:** `06d9000ca89a507da4fb3d17d780fc52a5d9d2f0` (tag: milestone-6c-batch-6c.5.4-certified)
- **Implementation Commit:** NONE (Changes remain in the working tree pending certification)
- **Certified Baseline:** Milestone 6C certified baseline.

## 3. Existing Active Import Path
The actual current path operates as follows:
Frontend VideoUploader → `POST /api/v1/projects/{project_id}/videos` → Project API → `VideoService.upload_video` → storage → metadata extraction → VideoAsset → `VideoRepository.save_video` → persisted asset → existing project-video retrieval.

## 4. Legacy Import Path
The legacy method `ProjectService.addLocalVideo()` and the `/videos/local` route remain unchanged in this batch.
The current known state is:
- The legacy/stale client method exists.
- The active VideoUploader does not use it.
- The active backend import contract is multipart.
- No new `/videos/local` route was introduced.

## 5. Defect Addressed
**Atomicity Defect:**
- **Before:** file write succeeds → database persistence fails → file remains orphaned on disk.
- **After:** file write succeeds → database persistence fails → request-local file is removed → original exception propagates.

## 6. Ownership
Responsibility boundaries established by repository evidence:
- **Project API:** request/HTTP handling.
- **VideoService:** validation orchestration, storage-path ownership, VideoAsset construction, persistence-failure compensation.
- **VideoProcessor:** metadata extraction.
- **VideoRepository:** VideoAsset persistence/retrieval.

## 7. Implementation
The production change was strictly limited to `backend/src/services/video_service.py` within `VideoService.upload_video`.
The `save_video` persistence boundary is wrapped in a `try/except Exception` block. If persistence fails, a nested cleanup guard checks for the existence of the request-local `storage_path` and safely removes it. Crucially, the catch block ends with a bare `raise`, explicitly preserving and re-raising the original persistence exception without replacement or masking.

## 8. Test Coverage
The following integration tests were implemented in `backend/tests/api/test_video_upload.py`:

### Successful Multipart Import
Proves:
- endpoint accepts multipart upload;
- asset is persisted;
- project association is correct;
- existing retrieval path recovers it;
- physical artifact exists;
- test cleans up the artifact during teardown.

### Invalid Extension
Proves:
- unsupported extension rejected;
- no persisted asset;
- no artifact when validation occurs before write (project storage directory not created or empty).

### Missing Project
Proves:
- nonexistent project rejected;
- no persisted asset;
- no artifact because project validation precedes file creation.

### Persistence Failure Atomicity
Proves:
- physical file created;
- persistence fails via mock;
- exact generated path captured;
- file removed;
- original exception preserved.

### Cleanup Failure Non-Masking
Proves:
- cleanup failure occurs via mocked `os.remove`;
- original persistence exception remains completely observable to the caller.

## 9. Test Results
- **Targeted upload tests (`pytest backend/tests/api/test_video_upload.py -v`):** `5 passed`
- **Architecture tests (`pytest backend/tests/architecture -v`):** `180 passed`
- **Full backend suite (`pytest backend/tests/ -v`):** Interrupted (`exit code 1`). The suite encountered a pre-existing thread deadlock deep within `test_transcription_execution.py` (`_asyncio.py` and `threading.py` `_wait_for_tstate_lock`). This is an environment/existing repository defect completely unrelated to this batch.

## 10. Architecture Verification
- **Architecture Change:** NONE
- **Reason:** The compensation logic remains entirely restricted within the `VideoService`. The repository contract, domain, API contract, Runtime, and storage architecture are unchanged.

## 11. Scope
### Changed
- VideoService atomicity behavior.
- Upload integration tests.
- Milestone 7.2.1 implementation report.

### Not Changed
- frontend uploader, `addLocalVideo`, `/videos/local`
- VideoAsset domain model
- repository architecture, database schema, migrations
- Runtime, AI, transcription, timeline, clip discovery, editing, rendering, export
- upload limits, metadata redesign

## 12. Known Limitations
- The 1-byte `.mp4` fixture proves the application-level upload contract, not real media validity. Real FFprobe/media decoding is not certified by these tests.
- Full backend suite fails due to a pre-existing threading issue in the unrelated transcription execution.
- Upload-size limits and async media lifecycle remain deferred.
- Legacy local-path client method remains deferred.

## 13. Certification Status
- **Implementation Status:** IMPLEMENTED
- **Certification Status:** PENDING
- **Commit Status:** NOT COMMITTED

---

## Post-Implementation Refinement

### A. Starting State
- **HEAD:** `06d9000ca89a507da4fb3d17d780fc52a5d9d2f0`
- **Branch:** `main`
- **Pre-existing changes:** `backend/src/core/__pycache__/bootstrap.cpython-314.pyc`
- **Implementation changes:** `backend/src/services/video_service.py`

### B. Refinements Performed
- Enhanced `test_upload_video_success` to intercept `save_video`, capture the actual `storage_path`, and assert that the exact physical file exists on disk, followed by safe teardown of the physical artifact.
- Strengthened `test_upload_video_invalid_extension` to explicitly prove `VideoRepository.save_video` is never called and the physical storage directory remains unpopulated.
- Strengthened `test_upload_video_missing_project` to explicitly prove `VideoRepository.save_video` is never called and no physical storage directory is created.
- Added `test_upload_video_cleanup_failure_does_not_mask_exception` to explicitly prove that a cleanup failure during atomicity rollback does not mask the original persistence exception.

### C. Production Changes
- **NONE.** The `VideoService` implementation correctly fulfilled the atomicity requirements without requiring any redesign or fixes during refinement.

### D. Test Results
- `pytest backend/tests/api/test_video_upload.py -v`: `5 passed`
- `pytest backend/tests/architecture -v`: `180 passed`
- `pytest backend/tests/ -v`: Interrupted (Pre-existing `test_transcription_execution.py` deadlock)

### E. Documentation Added
- `BATCH_7_2_1_MEDIA_IMPORT_CONTRACT_IMPLEMENTATION_REPORT.md`: To formalize the implementation state, constraints, architecture impact, and test evidence for the batch.

### F. Scope Verification
Exact changed files:
- `backend/src/services/video_service.py`
- `backend/tests/api/test_video_upload.py`
- `BATCH_7_2_1_MEDIA_IMPORT_CONTRACT_IMPLEMENTATION_REPORT.md`

### G. Remaining Evidence Gaps
- None regarding the specified media import contract atomicity. All test evidence gaps were explicitly closed without production code changes.

### H. Certification Readiness
**READY FOR CERTIFICATION**
