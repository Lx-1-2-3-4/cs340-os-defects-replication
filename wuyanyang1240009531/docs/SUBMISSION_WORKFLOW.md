# Proposed branch and pull-request workflow

This contribution extends teammates' existing data/baseline with attributed
checks and preprocessing robustness experiments. Keep the same group repository;
there is no need to create a disconnected repository or copy the baseline as
new authorship. Existing teammate directories remain theirs.

## Local state and intended review

- Starting revision: `91697f2eb9ca51105f8c976d266081b9daa1e7be`.
- Local branch: `wuyanyang-preprocessing-audit` (already created).
- Contribution folder: `wuyanyang1240009531/`.
- Other intended changes: root member index and isolated CI job.
- No commit, push, pull request or merge is performed by the analysis scripts.
- Upload still requires the user's explicit approval.

## Recommended sequence after approval

1. Fetch remote refs, inspect all new teammate commits, and integrate the current
   remote main into the contribution branch without losing local work. Do not
   reset main, force-push, or blindly overwrite root README/CI files. Rerun the
   module after integration. A changed shared snapshot requires deliberate
   provenance review rather than bypassing snapshot tests.
2. Review `git diff` and the full untracked file list. Stage only the module and
   the two intended root files. Preserve dataset bytes, teammate attribution,
   AI disclosure and successful current logs.
3. Verify repository-local Git name/email belong to the submitting student and
   the email is associated with the student's GitHub account. Authentication
   identity, commit identity and commit-message name are distinct; do not infer
   account ownership from the configured email, print tokens, or impersonate
   another student. Do not change global Git identity as a side effect.
4. Commit the substantive reviewed change with the required message, for example:
   `Add preprocessing audit and robustness experiments (1240009531 吴彦阳)`.
5. Push the contribution branch and open a PR targeting the group's main branch.
   Describe the new evidence, reused inputs, local checks, unresolved limitations
   and exact file scope. Link it in the group report/contribution record.
   If the student's account has no write permission on the group repository,
   use an authorized fork and a cross-repository PR instead of borrowing a
   teammate's credentials.
6. Run the remote CI and address real failures. Have a teammate review the PR,
   then merge into main before the relevant assessment. Preserve actual student
   attribution in merge/squash choices; check the final history afterwards.
7. Keep each course-relevant commit message compliant, including any merge or
   squash commit the team creates: it needs the actual committing member's ID
   and full name. Do not assume GitHub's generated message includes them. If a
   PR is squashed, manually check the resulting author, coauthor credit and
   message instead of relying on defaults.

A personal branch is for review/isolation, not a replacement for the group's
final main branch and final `v1.0` release. GitHub contribution-graph visibility
is also not the course's assessment criterion. Do not assume the teaching team
will inspect an unmerged branch; arrange integration into main and retain PR
evidence. Ask the TA only if the course's branch-review practice remains unclear.

## Weekly history

The handout states a Sunday 23:59 weekly check. The 15 November 2026 check is
already in the past as of 16 November 2026. A later push cannot count as an
earlier week's push; do not backdate or fabricate progress. A missing personal
push does not establish a missed group week: check whether teammates already
pushed meaningful work and keep individual-contribution requirements separate.

## Current remote-verification limitation

The read-only remote-ref query on 16 November 2026 failed with a TLS connection
error. Consequently this local review cannot confirm the latest main revision
or whether an identically named remote branch exists. Confirm both immediately
before eventual upload. This does not block local code review and testing.
