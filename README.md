# OSS CI isolation lab

A working comparison of GitHub Actions fork protections and two approaches built with existing Harness Unified capabilities. The contributor forks this repository and opens a PR back to the upstream repository. CI runs in the upstream owner's account.

## GitHub's approach

For external forks, `pull_request` runs untrusted code with a read-only `GITHUB_TOKEN` and withholds repository secrets. Maintainers can require approval before spending compute on those runs. Approval to run does not itself turn on repository secrets. [`pull_request_target`](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) has a trusted repository context and can access secrets, so its privileged jobs must not execute PR code.

GitHub also supports a privileged follow-up through [`workflow_run`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run). The follow-up must treat PR artifacts as untrusted data. GitHub Security Lab explains the [separate untrusted build and trusted reporting pattern](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/).

The [reference workflow](.github/workflows/fork-ci.yml) was tested with a real repository secret containing a synthetic canary. GitHub withheld it from the external fork. A separate same-repository control confirmed that the secret was configured and could resolve for trusted repository work.

## Harness option 1: conditionally skip privileged work

[Pipeline YAML](.harness/conditional.yaml)

Build and test the PR, but run the sample secret step only when the PR head repository ID matches the upstream repository ID. The pipeline definition comes from upstream `main`, and the trigger uses a webhook signing secret. The contributor's attempt to remove the condition in their fork did not change the executed pipeline.

This works when fork tests can run without the protected operation. In this sample, the fork ran 9 tests and skipped the test requiring a protected fixture. The same-repository control ran the secret step successfully.

The condition controls a step. It is not an account-wide restriction on secret access, and it does not supply protected dependencies to tests that need them.

## Harness option 2: prepare assets, then chain isolated tests

[Parent pipeline](.harness/chained.yaml) and [child pipeline](.harness/untrusted.yaml)

```text
Trusted preparation        Isolated contributor tests        Trusted reporting
Download fixed fixture  -> Verify fixture checksum       ->  Post GitHub status
Uses download credential   Build exact PR commit             Uses reporting credential
Runs no contributor code   Receives prepared data only       Runs no contributor code
```

The parent uses a credential to download a fixed JSON fixture from a private repository at a pinned commit. It passes only the prepared fixture, its SHA-256 checksum, and a nonsecret machine ID into a chained child pipeline. The small fixture is transferred as a base64 output variable. Both pipeline definitions come from upstream `main`.

The child starts a new Harness Cloud runtime, verifies the checksum and machine separation, fetches the exact PR commit anonymously from this public repository, and runs tests. It has no configured application secret or GitHub connector credential in its steps. A separate trusted stage posts the commit status through a fixed GitHub API operation.

The fork passed all 10 tests, including the prepared-fixture test, with 100% application line coverage. Named credential probes found neither sample credential in the contributor process or readable process environments. A deliberately wrong checksum stopped the child before checkout or tests.

This is the recommended starting point when credentials are needed to download assets. Harness documents [pipeline chaining and output-to-input mapping](https://developer.harness.io/harness-platform/use-harness-platform/pipelines/pipeline-chaining).

## Try or inspect it

- [External fork PR](https://github.com/ansibleautomates/oss-ci-isolation-lab/pull/1)
- [Same-repository control PR](https://github.com/ansibleautomates/oss-ci-isolation-lab/pull/2)
- [Contributor fork](https://github.com/Ompragash/oss-ci-isolation-lab)
- [Execution evidence and limitations](POC-RESULTS.md)

The YAML contains no pipeline-level name or identifier. Harness stores that registration metadata separately. Connector names, secret references, and the chained pipeline's organization/project path still require configuration in another environment.

For local unit tests:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m pytest -q
```

The protected-fixture test skips locally unless `APPROVED_ASSET_PATH` points to an approved fixture. Native Harness runs upload JUnit and LCOV reports. Coverage XML and HTML are also generated, but are not separately published as downloadable artifacts.

## Boundaries

The fixture is intentionally safe for contributors to read. This design protects the download credential, not the confidentiality of data deliberately passed to contributor code. If tests require a license key directly, those tests can read that key. A suitable test license or a service that performs the licensed operation without exposing the key is still needed.

The probes cover two named credentials and the trusted workspace marker. They are not a full audit of Harness runner tokens, process memory, host privileges, network access, or every secret access route. Production adoption requires least-privilege credentials, controlled pipeline editing and manual execution, and appropriate resource limits. For larger assets, replace the small output-variable transfer with immutable artifact storage and narrowly scoped retrieval access.

This contributor branch retains the deliberate YAML override and credential-presence probes.
