# OER.exports

## If you are looking for team information please look [here](https://github.com/openstax/content-managers/blob/master/README.md).

## Below is the workflow for the Textbooks developers and branch creation: 

## 1. milestone branch and tributary PRs
A textbook dev will create one branch and one big pull request (PR) for each release. The version number is bumped and the `version.txt` now uses the current milestone name (for example `naughty.newt 0.26.0` becomes `opulent.octopus 0.27.0`). The pull request is centralizing all the issues related to the milestone. Each dev creates an individual PR per issue, gets it reviewed by other devs then merges it into  the milestone PR. Do not merge your changes to master. When creating an individual PR, select the current milestone branch to compare against the milestone PR instead of master so the PR can be merged into it rather than into master. Please see steps 2 and 3 before contributing.

###### note: miscellaneous branches
Some changes may require a separate branch, such as pipleline changes to xslt, PrinceXML, docbook, spikes, etc. This may also include anything that doesn't directly pertain to a release such as documentation, repo maintenance, etc.

###### note: find data
Each issue will have a link to the relevant test data at the top of the description. If you can't find what you need, you should contact Alan (`@stackblocks`) or assigned tester.

## 2. issue PR workflow
When creating a new branch for an issue, name it issue-####, then commit to it as usual using descriptive commit messages. When creating a PR, use the issue number as part of the title and in the description, include a link to the issue the PR addresses. 
Request review from other devs. When the PR has been approved, merge it into the milestone PR. 

### Commit Messages

Some other suggestions (from [atom's CONTRIBUTING.md](https://github.com/atom/atom/blob/master/CONTRIBUTING.md#git-commit-messages))

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Consider starting the commit message with an applicable emoji:
    - :art: `:art:` when improving the format/structure of the code
    - :racehorse: `:racehorse:` when improving performance
    - :non-potable_water: `:non-potable_water:` when plugging memory leaks
    - :memo: `:memo:` when writing docs
    - :penguin: `:penguin:` when fixing something on Linux
    - :apple: `:apple:` when fixing something on macOS
    - :checkered_flag: `:checkered_flag:` when fixing something on Windows
    - :bug: `:bug:` when fixing a bug
    - :fire: `:fire:` when removing code or files
    - :green_heart: `:green_heart:` when fixing the CI build
    - :white_check_mark: `:white_check_mark:` when adding tests
    - :lock: `:lock:` when dealing with security
    - :arrow_up: `:arrow_up:` when upgrading dependencies
    - :arrow_down: `:arrow_down:` when downgrading dependencies
    - :shirt: `:shirt:` when removing linter warnings

## 3. reassign the issue to tester 
When the PR has been merged into the milestone PR, confirm that the PR in which the issue is fixed is referenced, update the issue with a screenshot of the fix and reassign issue to tester. 

###### note: comments on the issue
It's ok to include a screenshot or a comment in the issue before the PR has been merged but the issue should not be reassigned until the fix has been merged into the milestone PR.

## 4. dev testing
Fixes for individual issues are verified on [devb](https://devb.openstax.org) by Alan (`@stackblocks`) or assigned tester. If any problems are found, the issue is updated with comments and screen captures as necessary, and reassigned to the dev that created the fix. In that case, the dev opens a new PR with the appropriate fix and follows the process in step #2. When the issue has been verified on [devb](https://devb.openstax.org), it is closed. The only people closing issues are Alan or other testers.

## 5. code freeze and release to staging
Every other Monday, we release our code to staging. On that day, a final code review is conducted on the milestone PR, then the PR is merged, tagged and is ready for release. That stage is known as "code freeze". When the tag is ready, notify Alan with a link to the release. 

## 6. regression testing and junior branches
Regression testing is done on [staging](https://staging.openstax.org), to ensure there were no unintended consequences.
If a regression is found during that phase, we open a junior version of the current milestone. The sub-version in `version.txt` is bumped but the milestone name remains. For example, `opulent.octopus 0.27.0` becomes `opulent.octopus 0.27.1`. A new PR is created for the new branch but during this phase, devs push their fixes directly to the junior milestone branch instead of creating individual PRs. When all the fixes are ready, the milestone branch is code-reviewed, merged, tagged and ready for release.



