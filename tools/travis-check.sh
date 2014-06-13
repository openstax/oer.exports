# Verify no CSS files changed as a result of running `grunt compile`
FILES_CHANGED=$(git status -s | wc -l)
exit $FILES_CHANGED
