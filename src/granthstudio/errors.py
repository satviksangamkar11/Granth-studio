"""Error types. Every refusal or block in the pipeline raises one of these.

``exit_code`` is what the CLI returns: 1 configuration, 2 refused or gate failed,
3 NOT VALIDATED integration (no output was produced).
"""


class GranthError(Exception):
    exit_code = 2


class ConfigError(GranthError):
    """Bad configuration, fixture or usage. Fix the input and rerun."""

    exit_code = 1


class SchemaError(ConfigError):
    """A document does not match its JSON Schema."""


class ResearchNotApproved(GranthError):
    """Research has unresolved or provisional items, or no approval receipt exists."""


class SourceChanged(GranthError):
    """Approved research changed after approval; a new approval version is required."""


class CanonReferenceError(GranthError):
    """A reference points at an unknown or unapproved canon entry."""


class IdentityConflict(GranthError):
    """Identities may match or names are shared without an explicit decision."""


class GateFailure(GranthError):
    """A hard quality gate blocked the output."""


class CapabilityDisabled(GranthError):
    """An LTX capability (i2v or flf) is not validated; execution is refused."""

    exit_code = 3


class IntegrationUnavailable(GranthError):
    """An external integration is not validated on this machine (NOT VALIDATED)."""

    exit_code = 3


class TaskFailed(GranthError):
    """A scheduled task failed on one attempt."""
