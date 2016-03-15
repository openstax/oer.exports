#OER.exports

## 1. use one branch as a milestone overview
A template dev will create one branch and one big pull request for each release. The version number is bumped and the version.txt now uses the current milestone name (for example naughty.newt 0.26.0 becomes opulent.octopus 0.27.0). The pull request is centralizing all the issues related to the milestone. Do not create individual PR per issue, use the common PR created for the milestone and do not merge your changes to master. Please see steps 3 and 4 before contributing.

###### note: miscellaneous branches
Some changes may require a separate branch, such as pipleline changes to xslt, PrinceXML, docbook, spikes, etc. This may also include anything that doesn't directly pertain to a release such as documentation, repo maintenance, etc.

## 2. issue management
The textbook team meets every Tuesday at 10am to plan upcoming releases. At that time we will review all open issues, including any that do not have an associated milestone and assign them appropriately. We determine which issues should be assigned by the sustain team (team:sustain github label) or the forward team (team:forward). Any forward issue is assigned to the appropriate Template Dev.

###### note: find data
Each issue will have a link to the relevant test data at the top of the description. If you can't find what you need, you should contact Kerwin (@Kerwinso) or assigned tester.

## 3. reference issues when committing
Please use the issue number within commit messages, for example "issue #1111". This will create a link within the PR to the issue itself and help track changes. Typically, only referencing the issue is enough but if there are multiple fixes for one issue, you may add a descriptive comment when needed, for example "issue #1111 - changing font-size".

## 4. review code

## 5. comment on the issue when addressed in the PR
When the fix for an issue has been pushed to github and is ready for review, go to the issue and reference the PR in the comments. For example you may have something like "Addressed in PR #1111". This is also a good time to mention anything that the tester should be aware of or anything we may need to keep track of later on.

At this stage, the workflow is:
  - find issue #1111 on github
  - add a comment saying "Addressed in PR #2222"

## 6. reassign to tester when the fix has been pushed to the PR on github
Reassign an issue to Kerwin (@kerwinso) or assigned tester only when it is ready for testing and the files are on github.

## 8. dev testing
Fixes for individual issues are verified on textbook-dev by Kerwin (@kerwinso) or assigned tester. If any problems are found, the issue is updated with comments and screen captures as necessary, and reassigned to the dev that created the fix. When the issue has been verified on textbook-dev, it is closed. The only people closing issues are Kerwin or other testers.

Regression testing is done on textbook-qa, to ensure there were no unintended consequences.

## 7. final code review
When all the issues have been tested, fixes verified and closed on textbook-dev, the template developers review code for that branch. //day before release, person who's creating the tag.

## 8. code deployment to QA for regression testing
After fix verification is complete, we merge the pull request into the master branch and create a git tag.

After a tag is created, create a github release. This should contain information about:
 - name of the release
 - PR reference (e.g. #1111)
 - short description of changes (what titles are effected)
 - dates, server deployments
 - "pre release" checkbox whether it's a QA release or not. If it's deployed to QA, check the checkbox, it will be unchecked when released on Production. Include an estimated date for releases to QA and Production.

After template devs have merged the PR, the testers will create a Trello card on the [devops board](https://trello.com/b/5VGYnZS0/devops) for deployment. The card goes in the application deployment section and contains the following information:
 - oer.exports version number (see version.txt)
 - milestone name
 - due date and time
 - urgency label (typically medium urgency)
 - assigned devOps admin (typically Dennis Williamson)
 - link to the tag on github
 - checkbox for server for deployment
 - checkbox for code readiness (Kerwin, Alana, Alina)
 - checkbox for release verification by a Alina (@openstaxAlina) or a DMS

For an example card, see: https://trello.com/c/NQWn3w4B/236-oer-exports-0-26-0-release-to-textbook-qa-server
After code has been deployed to textbook-QA, someone will verify that code has been deployed correctly by checking that one easy to verify fix exists on that server.


## 9. textbook-qa regression testing and handling regression issues
Typically, DMSs perform regression testing on textbook-QA. Kerwin or the assigned tester will provide a plan for testing that includes the affected titles and expected changes. For an example see https://docs.google.com/spreadsheets/d/10gtI0l43nnK557pilS8E1HlyervNngzcNVUBccgOyqo/edit#gid=0
Closed issues may be reopened if the fix couldn't be verified on textbook-QA or github issues may be opened in the case of new regressions or unintended changes.
Every time the fix is verified on textbook-QA, a comment and a screen capture is provided. General modifications causing regression may be described as acceptable changes and documented. Alana needs to approve all those changes.

If issues are found during regression testing, a textbook dev will create a new branch and a new PR named with the same milestone name and the suffix qa (opulent.octopus.qa for example), which becomes our new main branch and is used to address any issues. The sub-version in version.txt is bumped but the milestone name remains. For example, opulent.octopus 0.27.0 becomes opulent.octopus 0.27.1. Repeat the steps listed above (2 to 8) as necessary.

## 10. code deployment to production
When all testing is complete, we deploy to production. We have 6 production environments: production (cnx.org) and 5 staging servers that are used for by the XML production team to develop content. The testers will create a Trello card on the devOps board for deployment.

After the code is deployed on Production and staging servers and verified, create release notes reporting on all issues submitted by Wisewire for that milestone. Not every issue may result in a fix. At that time, we may also provide them with an updated tagging legend; as well a new test collection if content doesn't exist on one of the staging servers (XML production has not started).
