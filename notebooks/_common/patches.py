"""One-time runtime patches for MAF notebooks.

Currently only the gzip workaround (MAF issue #2457). Import + call once
near the top of any notebook that uses agent-framework.
"""

from __future__ import annotations

_gzip_patched = False


def apply_maf_gzip_workaround() -> None:
    """Force Accept-Encoding: identity on outgoing httpx requests.

    Fixes an MAF streaming/gzip interaction (issue #2457). Idempotent.
    """
    global _gzip_patched
    if _gzip_patched:
        return
    try:
        import httpx
    except ImportError:
        return

    original_build_request = httpx.Client.build_request

    def patched_build_request(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        request = original_build_request(self, *args, **kwargs)
        request.headers["Accept-Encoding"] = "identity"
        return request

    httpx.Client.build_request = patched_build_request  # type: ignore[assignment]
    _gzip_patched = True
