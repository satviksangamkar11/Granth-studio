"""Fail-closed model identity check shared by the reference runners (O-007)."""
from __future__ import annotations

import os


class IdentityError(RuntimeError):
    pass


def approved_identity(payload: dict, env_name: str) -> tuple[str, str]:
    """(model, revision) approved in config/models.yaml and sent in the payload. The environment variable may
    only restate the approved model; it can never substitute other weights."""
    model, revision = payload.get("model"), payload.get("revision")
    if not isinstance(model, str) or not model or not isinstance(revision, str) or not revision:
        raise IdentityError("payload carries no approved model/revision: refusing to run")
    override = os.environ.get(env_name)
    if override and override != model:
        raise IdentityError(f"{env_name}={override!r} differs from the approved model {model!r}: refusing to run")
    return model, revision


def verified_identity(model: str, revision: str, loaded_commit: object) -> dict:
    """The identity actually loaded must prove the approved revision."""
    if not isinstance(loaded_commit, str) or not loaded_commit:
        raise IdentityError(f"no revision evidence for the loaded {model} checkpoint: refusing to run")
    if loaded_commit != revision:
        raise IdentityError(f"loaded revision {loaded_commit} differs from approved {revision} for {model}: refusing to run")
    return {"model": model, "revision": loaded_commit}
