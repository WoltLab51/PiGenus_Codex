"""Rate-limit extension point.

Phase 1 deploys behind a private network and token auth. This module exists so rate limiting can
be added without changing route contracts. A later milestone should implement per-token and
per-device buckets, with conservative defaults for public-facing deployments.
"""

