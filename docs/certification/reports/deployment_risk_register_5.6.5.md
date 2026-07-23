# Deployment Risk Register 5.6.5

## Deployment Risks
- **Risk**: Missed Alembic migrations across deployment environments.
- **Impact**: Application refuses to start.
- **Mitigation**: Startup validation prevents data corruption by halting on schema mismatch.
- **Blocks Certification**: No.

## Runtime Risks
- **Risk**: Ollama or Whisper inference latency spikes.
- **Impact**: Request timeouts.
- **Mitigation**: `ai_timeout_seconds` and `process_timeout` constraints.
- **Blocks Certification**: No.

## Infrastructure Risks
- **Risk**: FFmpeg binaries unavailable on host container.
- **Impact**: System cannot process media.
- **Mitigation**: Fail-fast validation on startup.
- **Blocks Certification**: No.

## Future Scaling Risks
- **Risk**: SQLite concurrent write contention under heavy load.
- **Impact**: Database locks.
- **Mitigation**: Migration to PostgreSQL in future sprints when load demands.
- **Blocks Certification**: No.

## Conclusion
No identified risk blocks production certification.
