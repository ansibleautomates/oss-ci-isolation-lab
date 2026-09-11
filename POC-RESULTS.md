# OSS CI isolation POC results

Tested on 11 September 2026. The public upstream repository and contributor fork are separate GitHub accounts. All Harness runs execute in the upstream owner's Harness project.

## Verified behavior

| Test | Result |
| --- | --- |
| GitHub Actions external fork | Passed. Read-only contents permission, secret source `None`, configured repository canary absent. |
| GitHub Actions same-repository control | Passed. Secret source `Actions`, synthetic canary resolved. |
| Harness external fork condition | Passed. `same_repository_secret` skipped; contributor code ran; named credentials absent in the bounded probes. |
| Harness same-repository condition control | Passed. `same_repository_secret` succeeded and resolved the synthetic canary. |
| Trusted private asset preparation | Passed. Fixed fixture downloaded using authentication from a private repository at a pinned commit. No contributor code executed in preparation. |
| Chained contributor execution | Passed. A different machine boot ID, no trusted sentinel file, exact PR SHA checkout, and checksum verification. |
| Tests using the prepared fixture | Passed. 10 tests, 0 skipped, 100% application line coverage. Harness Tests and Coverage views were inspected. |
| Attempted fork YAML overrides | Did not take effect. The fork removed the condition and added a child step requesting the canary; executions used upstream definitions. |
| Incorrect fixture checksum | Rejected before checkout or tests. Failure: `Prepared asset checksum mismatch`. |
| GitHub commit status reporting | Passed for both success and deliberate test failure. Reporting ran on separate trusted stages and kept failed pipelines failed. |
| Reports after failing tests | Passed. The final failed child retained JUnit and coverage uploads; Harness Tests showed 9 passed and 1 failed. |

## Final repeat with the completed configuration

The final positive PR commit is `09d5b4a493b68c828cb62373be56ee89e0a6e560`. It remains mergeable and keeps the deliberate YAML override probes.

| Check | Final evidence |
| --- | --- |
| GitHub Actions | [Passed](https://github.com/ansibleautomates/oss-ci-isolation-lab/actions/runs/34603917042) |
| Harness conditional guard | [Passed](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_conditions/deployments/ya5eF_T_TlqpguBekA1fhw/pipeline) |
| Harness chained parent | [Passed](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_chained/deployments/CnxnqjEKTayHRIjbyBLqcQ/pipeline) |
| Harness isolated child | [10 tests passed](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_untrusted/deployments/o6G7Dl-KRrq5qqRgzkCnIQ/tests) |

The final negative control commit is `c99cf15f916bb97bd862e6feb55bf1eb8176ea27`. Its failure is intentional.

| Check | Final evidence |
| --- | --- |
| GitHub Actions | [Expected failure](https://github.com/ansibleautomates/oss-ci-isolation-lab/actions/runs/34603921123) |
| Harness conditional guard | [Expected failure with trusted reporting completed](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_conditions/deployments/LMcffdZ7TD6XFPXgLZnWUw/pipeline) |
| Harness chained parent | [Expected failure with trusted reporting completed](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_chained/deployments/Vp8KkeNqQzGEXTxeuwGpkA/pipeline) |
| Harness isolated child | [Retained report: 9 passed, 1 failed](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_untrusted/deployments/sN1Sg4IDSRyi-ml9BGOTfw/tests) |

GitHub's commit status API confirmed both Harness contexts were `success` on the positive commit and `failure` on the negative commit. The reporting stage never ran contributor code. The final failed report was also verified in the Harness UI.

## Evidence

- [GitHub external fork reference](https://github.com/ansibleautomates/oss-ci-isolation-lab/actions/runs/34602402441): 9 passed, 1 skipped. `OSS_CI_CANARY` and `OSS_CI_ASSETS_TOKEN` were absent in the probe. Only the canary was configured as a GitHub repository secret.
- [GitHub same-repository control](https://github.com/ansibleautomates/oss-ci-isolation-lab/actions/runs/34602689724): `same_repository_canary_resolved: true`.
- [Harness external fork conditional run](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_conditions/deployments/RosT3alfRWi-ldzRmwMw1w/pipeline): 9 passed, 1 skipped; privileged step skipped.
- [Harness same-repository control](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_conditions/deployments/3_NwWuT7QnufxUwS6oD4qQ/pipeline): privileged step succeeded.
- [Harness chained external fork parent](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_chained/deployments/Pfrpod8GT7yACaIVuAuEVg/pipeline).
- [Harness isolated fork tests](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_untrusted/deployments/5Jf88aFlR1ark8PfWv0Xow/tests): 10 passed, including `test_prepared_asset`.
- [Harness isolated fork coverage](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_untrusted/deployments/5Jf88aFlR1ark8PfWv0Xow/code-coverage): test output and file table show 9 of 9 lines covered, 100%. One summary card showed 8 lines covered while the file table showed 9; that UI discrepancy was not investigated.
- [Checksum rejection control](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_untrusted/deployments/0bIJDTXBSnKgIoFWy7qNOA/pipeline): checksum failed; checkout, contributor probe, build, tests, and uploads skipped.

The first signed Harness fork run tested commit `3c28f4a31a92f2b7ecf60694e7fc4fe8c2c00645`. The private fixture was pinned to commit `225af5ec76b70ae52a7b01567871b2c3e0fee8f3` in `ansibleautomates/oss-ci-assets-private`. The prepared data checksum was `98bda61ec1e3951924b2f6665ebd571b0b9fa755a3f65e470efa1bf58208b938`.

## Trusted GitHub reporting

Because the test runner uses anonymous Git checkout, this POC explicitly posts commit statuses from a separate trusted stage. That stage receives the pipeline's recorded stage status and exact commit SHA, executes fixed inline code, and sends a fixed commit-status request. It does not execute code, scripts, or binaries from the PR.

Both `harness/conditional-guard` and `harness/chained-isolation` posted success for commit `9463162d7dac09b8f3cad1c4c12e2e2540b53d02`. [Conditional reporting execution](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_conditions/deployments/TS_st10jTEqJ3QK2wFgNrA/pipeline) and [chained reporting execution](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_chained/deployments/1EogOha7Su2xxhrCSwCbSw/pipeline) succeeded.

[PR #3](https://github.com/ansibleautomates/oss-ci-isolation-lab/pull/3) deliberately adds a failing test. Both contexts posted failure for commit `4f9d7b556d61df0c5158100753bad5a820317ba8`. The [conditional pipeline](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_conditions/deployments/4AYak4u6QkClFdvRNw5pzQ/pipeline) and [chained pipeline](https://unifiedpipeline.harness.io/ng/account/MGY3MmJmM2ItNTY5Ny00Yj/all/orgs/default/projects/chef_oss_pov/pipelines/oss_ci_chained/deployments/61yztrBeT7OubOGK85Iplw/pipeline) remained failed even though their reporting stages succeeded. This failure is an expected test control.

The final report-upload step uses `if: <+Always>` and checks whether the report files exist. This retains reports when pytest fails while avoiding a missing-file error when checkout or fixture verification fails.

## How the isolation works

The restricted child has automatic connector-based cloning disabled and uses an anonymous fetch from the fixed public upstream URL. The SHA is validated and checked after checkout. It receives a permitted JSON fixture through parent outputs mapped to child inputs, not the original download credential. No shared cache or shared workspace is configured. The child checks that its machine boot ID differs from the preparation machine and that the preparation sentinel file is absent.

The contributor probe attempts to read only two named credentials, `OSS_CI_CANARY` and `OSS_CI_ASSETS_TOKEN`, from its environment and readable `/proc/*/environ` files. It reports booleans and never prints credential values. These results demonstrate the measured boundary, not exhaustive resistance to hostile code.

## Reproduction configuration

- Pipelines: `oss_ci_conditions`, `oss_ci_chained`, and `oss_ci_untrusted`.
- GitHub connector: `oss_ci_github`.
- Application canary: `oss_ci_canary`, containing a random synthetic value.
- Trusted download/reporting credential: `oss_ci_assets_token`, containing the existing authorized upstream GitHub PAT. Its permissions were not reduced for this POC.
- Webhook authentication: `oss_ci_webhook_secret`, separately generated. Both triggers reference it, and GitHub webhook 677679790 has a secret configured. Signed synchronize events started the runs. Adversarial signature validation was not independently tested.
- PR triggers listen for open, synchronize, and reopen targeting `main`, and load pipeline definitions from `main`.
- Exact head SHA comes from the event. Trusted preparation also checks the PR's current head through GitHub's API and stops if it changed.
- Runtime: separate Harness Cloud stages, pipeline caches disabled. Child and conditional pipelines have 10-minute timeouts; the chained parent has 15 minutes.
- Auto-abort of previous PR executions is configured but was not stress-tested. No contributor quota or spend cap was implemented.

The initial unsigned open event did not produce a Harness execution while the signing configuration was being completed. Subsequent signed synchronize events were used for the fork test. One earlier checksum trial also had an abbreviated SHA input; the linked checksum control above uses the complete correct SHA and isolates the checksum change.

## What remains outside this POC

Runtime license secrecy, a full audit of Harness infrastructure credentials, cross-tenant isolation, shared-cache attacks, anonymous Harness report access, artifact retention, and production-scale asset transfer are not proven here. Test report parsing still processes contributor-produced data. The fixture is small and benign, not an arbitrary executable artifact.

The exact PR head is tested, rather than a merge with the current upstream branch. Mergeability checks and merge-result validation would need an explicit policy. GitHub's normal `pull_request` workflow uses the PR merge context; this difference matters when the base branch changes.

The conditional pattern is useful for tests that can omit privileged work. The chained pattern is the stronger fit when tests need approved files obtainable using a credential. Neither makes a secret unreadable to code that is deliberately given that secret.
