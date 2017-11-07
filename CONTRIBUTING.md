#OER.exports

## 1. using one branch as a milestone overview
A textbook dev will create one branch and one big pull request for each release. The version number is bumped and the version.txt now uses the current milestone name (for example naughty.newt 0.26.0 becomes opulent.octopus 0.27.0). The pull request is centralizing all the issues related to the milestone. Do not create individual PR per issue, use the common PR created for the milestone and do not merge your changes to master.

### 1.a
Some changes may require a separate branch, such as pipleline changes to xslt, PrinceXML, docbook etc. This may also include anything that doesn't directly pertain to a release such as documentation, repo maintenance, etc.

## 2. issue management
The textbook team meets every Tuesday at 10am to plan upcoming releases. At that time we will review all open issues, including any that do not have an associated milestone and assign them approximately. We determine which issues should be handled by the sustain team or the forward team. Any forward issue is attributed to the appropriate Template Dev. 

## 2. referencing issues when committing
Please use the issue number within commit messages, for example "issue #1111". This will create a link within the PR to the issue itself and help track changes. Typically, only referencing the issue is enough but if there are multiple fixes for one issue, you may add a descriptive comment when needed, for example "issue #1111 - changing font-size".

The workflow is:
  - checkout branch
  - make changes
  - add files and commit (git commit -m "issue #1111")
  - push to PR

### Commit Messages

Some other suggestions (from [atom's CONTRIBUTING.md](https://github.com/atom/atom/blob/master/CONTRIBUTING.md#git-commit-messages))

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :penguin: `:penguin:` when fixing something on Linux
    * :apple: `:apple:` when fixing something on macOS
    * :checkered_flag: `:checkered_flag:` when fixing something on Windows
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when fixing the CI build
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings

## 3. commenting on the issue when addressed in the PR
When the fix for an issue has been pushed to github and is ready for review, go to the issue and reference the PR in the comments. For example you may have something like "Addressed in PR #1111". This is also a good time to mention anything that the tester should be aware of or anything we may need to keep track of later on.

At this stage, the workflow is:
  - find issue #1111 on github
  - add a comment saying "Addressed in PR #2222"

## 4. reassign to tester when the fix has been pushed to the PR on github
Reassign an issue to Kerwin (@kerwinso) or assigned tester only when it is ready for testing and the files are on github.

## 5. dev testing
Fixes for individual issues are verified on textbook-dev by Kerwin (@kerwinso) or assigned tester. If any problems are found, the issue is updated with comments and screen captures as necessary, and reassigned to the dev that created the fix. When the issue has been verified on textbook-dev, it is closed. The only people closing issues are Kerwin or other testers.

Regression testing is done on textbook-qa, to ensure there were no unintended consequences.

## 6. code review
When all the issues have been tested, fixes verified and closed on textbook-dev and, the textbook developers review code for that branch. This typically happens the day of the release (listed on the github milestone).

## 7. code deployment for QA regression testing
When code review is complete, code is deployed to textbook-qa. A member of the textbook team will create a tag and merge the PR. After textbook devs have merged the PR, the testers will create a Trello card on the devops board ( https://trello.com/b/5VGYnZS0/devops) for deployment. The card goes in the application deployment section and contains the following information:
'various bug fixes associated with naughty newt milestone for print updates:
https://github.com/Connexions/oer.exports/releases/tag/v0.26.0 ".

For an example card, see: https://trello.com/c/NQWn3w4B/236-oer-exports-0-26-0-release-to-textbook-qa-server
After code has been deployed to textbook-QA, someone will verify that code has been deployed correctly by checking that one easy to verify fix exists on that server.
After the code is deployed and verified, release notes reporting all issues for that milestone are provided to WiseWire. Not every issue may result in a fix. At time we also provide them with any tagging legend change that may have been necessary as well a new test collection if content doesn't on one of the staging servers (XML producation has not started).

## 8. issues identified during textbook-qa regression testing
Typically, DMSs perform regression testing on textbook-QA. Kerwin or the assigned tester will provide a plan for testing that includes the affected books and expected changes. For an example see https://docs.google.com/spreadsheets/d/10gtI0l43nnK557pilS8E1HlyervNngzcNVUBccgOyqo/edit#gid=0
Closed issues may be reopened if the fix couldn't be verified on textbook-QA or github issues may be opened in the case of new regressions or unintended changes.
Every time the fix is verified on textbook-QA, a comment and a screencapture is provided. General modifications causing regression may be described as acceptable changes and documented. Alana needs to approve all those changes.

If issues are found during regression testing, a textbook dev will create a new branch and a new PR named with the same milestone name (opulent.octopus.qa for example), which becomes our new main branch and is used to address any issues. The sub-version in version.txt is bumped but the milestone name remains. For example, opulent.octopus 0.27.0 becomes opulent.octopus 0.27.1. Repeat the steps listed above (2 to 7) as necessary.

## 9. code deployment to production
When all testing is complete, we deploy to production. We have 6 production environments: production (cnx.org) and 5 staging servers that are used for by the XML production team to develop content. The testers will create a Trello card on the devops board for deployment.
