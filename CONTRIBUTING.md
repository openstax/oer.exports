#OER.exports

## 1. using one branch as a milestone overview
A textbook dev will create one branch and one big pull request for each release. The version number is bumped and the `version.txt` now uses the current milestone name (for example `naughty.newt 0.26.0` becomes `opulent.octopus 0.27.0`). The pull request is centralizing all the issues related to the milestone. Do not create individual PR per issue, use the common PR created for the milestone and do not merge your changes to master. 

## 2. referencing issues when committing
Pleaes use the issue number within commit messages, for example `#1111`. This will create a link within the PR to the issue itself and help track changes. Typically, only referencing the issue is enough but if there are mulptiple fixes for one issue, you may add a descriptive comment when needed, for example `issue #1111 - changing font-size`.

## 3. commenting on the issue when addressed in the PR
When the fix for an issue has been pushed to github and is ready for review, go to the issue and reference the PR in the comments. For example you may have something like `Addressed in PR #1111`. This is also a good time to mention anything that the tester should be aware of or anything we may need to keep track of later on. 

## 4. reassign the issue to tester when the fix has been pushed to the PR on github
Reassign an issue to Kerwin (`@kerwinso`) or assigned tester only when it is ready for testing and the files are pushed to GitHub. 

## 5. regression testing
Fixes for individual issues are verified on `textbook-dev`.
Regression testing is done on https://textbook-qa.cnx.org, to ensure there were no unintended consequences. 

## 6. code review
When all the issues have been tested and closed, fixes verified on https://textbook-dev.cnx.org, the textbook developers review code for that branch. This typically happens the day of the release (listed on the github milestone).

## 7. code deployment for regression testing
When code review is complete, code is deployed to https://textbook-qa.cnx.org. A member of the textbook team will create a tag and merge the PR. After textbook devs have merged the PR, the testers will create a Trello card on the devops board for deployment. 

## 8. issues identified during textbook-qa regression testing
If issues are found during regression testing, a textbook dev will create a new branch and a new PR named `${MILESTONE.NAME}-qa`, which becomes our new main branch and is used to address any issues. The sub-version in `version.txt` is bumped but the milestone name remmains. For example, `opulent.octopus 0.27.0` becomes `opulent.octopus 0.27.1`. Repeat the steps listed above (2 to 7) as necessary.

## 9. code deployment to production
When all testing is complete, we deploy to production. We have 6 production environments: production (https://cnx.org) and 5 staging servers that are used for by the XML production team to develop content. The testers will create a Trello card on the devops board for deployment. 
