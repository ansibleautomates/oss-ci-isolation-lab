"""Bounded probe: report presence of two named POC credentials, never their values."""
import json
import os
from pathlib import Path

NAMES = ("OSS_CI_CANARY", "OSS_CI_ASSETS_TOKEN")


def probe():
    own_environment = {name: bool(os.environ.get(name)) for name in NAMES}
    process_environment = {name: False for name in NAMES}
    inspected = 0
    for entry in Path("/proc").glob("[0-9]*/environ"):
        try:
            data = entry.read_bytes().split(b"\0")
        except (OSError, PermissionError):
            continue
        inspected += 1
        for name in NAMES:
            prefix = name.encode() + b"="
            process_environment[name] |= any(v.startswith(prefix) and len(v) > len(prefix) for v in data)
    result = {
        "own_environment_credentials_present": own_environment,
        "readable_process_credentials_present": process_environment,
        "readable_process_environments_checked": inspected,
        "trusted_workspace_sentinel_present": Path("/tmp/oss-ci-trusted-sentinel").exists(),
        "scope": "named-poc-credentials-only",
        "contributor_modified_probe_executed": True,
    }
    print(json.dumps(result, sort_keys=True))
    assert not any(own_environment.values()), "Named POC credential present in contributor environment"
    assert not any(process_environment.values()), "Named POC credential present in a readable process environment"
    assert not result["trusted_workspace_sentinel_present"], "Trusted workspace visible to contributor"


if __name__ == "__main__":
    probe()
