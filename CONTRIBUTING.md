#OER.exports


##using one branch as a milestone overview
We create one big pull request for each release. The pull request is centralizing all the issues related to the milestone.

##referencing issues when committing
Use "issue #1111" within commit messages. You may add a descriptive comment when needed, for example "issue #1111 - changing font-size"

##commenting on the issue when addressed in the PR
When the fix for an issue has been pushed to github and is ready for review, go to the issue and reference the PR in the comments

##reassign to Kerwin or the testing person when the fix is on github
Reassign an issue to Kerwin only when it is ready for testing and the files are on github. 

## Regression testing
regression testing is done directly on QA, while individual books are tested on textbook-dev. When testing is completed on textbook-dev, it's moved to QA. The PR is closed and merged to master, a tag is created.

If QA has issues, we open a new PR named milestone.name-qa, which becomes our new main branch and is used to address any issues found during regression testing. The version is bumped but the milestone name remmains. For example, milestone.name 0.26.0 becomes milestone.name 0.26.1
