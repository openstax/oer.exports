# TODO:
#
# - check that docbook-xsl/xhtml/addon.xsl exists (to make sure it was installed locally)
# - check that the book paths in config.yml contain collection.xml
# - when a task errors make grunt fail
# - add option to skip `pdf` task if the `collection.xhtml` already exists

module.exports = (grunt) ->

  path = require('path')
  fs = require('fs')
  pkg = require('./package.json')
  chalk = require('chalk')
  config = grunt.file.readYAML('config.yml')

  failIfNotExists = (message, filePath) ->
    throw new Error("#{message}: #{filePath}") if not fs.existsSync(filePath)

  skipIfExists = (filePath) ->
    if config.skipping and fs.existsSync(filePath)
      grunt.log.writeln("#{chalk.green('Skipping step because target file exists:')} #{filePath}")
      return true

  # Project configuration.
  grunt.initConfig
    pkg: pkg
    config: config

    shell:
      options:
        timeout: 0
        stdout: false
        stderr: false
        failOnError: true

      'compile':
        command: (bookName) ->
          return "lessc css/ccap-#{bookName}.less > css/ccap-#{bookName}.css"

      # 1. Generate a PDF and more importantly, the huge HTML file
      'pdf':
        command: (bookName, branchName='new') ->
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"

          # Shortcut if skipping flag is set
          return '' if skipIfExists("#{tempDir}/collection.xhtml")

          # Make sure the files exist
          failIfNotExists('Path to PrinceXML does not exist', config.prince)
          failIfNotExists('Path to unzipped collection does not exist', config.books[bookName])
          failIfNotExists('Unzipped Docbook does not exist', './docbook-xsl/VERSION.xsl')
          failIfNotExists('CSS file does not exist', "./css/ccap-#{bookName}.css")

          return [
            'mkdir <%= config.testingDir %>'
            'virtualenv .'
            'source ./bin/activate'
            'pip install lxml argparse pillow'
            # Send stderr to /dev/null because grunt falls over with too many log lines
            "echo 'Building book (it should take a long time. If it is quick then it probably failed)...'"
            "python ./collectiondbk2pdf.py -v
              -p <%= config.prince %>
              -d <%= config.books.#{bookName} %>
              -s ccap-#{bookName}
              -t #{tempDir}
              <%= config.testingDir %>/#{bookName}-#{branchName}.pdf
              2> /dev/null
            "
          ].join('; ')

      # 2. Generate HTML Coverage Report (optional)
      # 2a. Generate LCOV file
      'coverage':
        command: (bookName, branchName='new') ->
          lessFile = "./css/ccap-#{bookName}.less"
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"
          lcovFile = "#{config.testingDir}/#{bookName}-#{branchName}.lcov"

          # Shortcut if skipping flag is set
          return '' if skipIfExists(lcovFile)

          # Make sure the files exist
          failIfNotExists("Less file does not exist: #{lessFile}", lessFile)
          failIfNotExists("XHTML file missing. generate with `grunt shell:pdf:#{bookName}`: #{tempDir}/collection.xhtml", "#{tempDir}/collection.xhtml")

          return "node ./node_modules/.bin/css-coverage -d -v
            -s #{lessFile}
            -h #{tempDir}/collection.xhtml
            -l #{lcovFile}"
      # 2b. Generate HTML Report from LCOV file
      'coverage-report':
        command: (bookName, branchName='new') ->
          failIfNotExists("LCOV file missing. generate with `grunt shell:coverage:#{bookName}`", "#{config.testingDir}/#{bookName}-#{branchName}.lcov")

          return "genhtml <%= config.testingDir %>/#{bookName}-#{branchName}.lcov
            --output-directory <%= config.testingDir %>/#{bookName}-#{branchName}-coverage
          "

      # 3. Generate HTML For Later Diffing
      'bake':
        command: (bookName, branchName='new') ->
          cssDiffPath = './node_modules/css-diff'
          lessFile = "./css/ccap-#{bookName}.less"
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"
          bakedXhtmlFile = "#{config.testingDir}/#{bookName}-#{branchName}.xhtml"

          failIfNotExists("LESS file missing", lessFile)
          failIfNotExists("XHTML file missing. generate with `grunt shell:pdf:#{bookName}`", "#{tempDir}/collection.xhtml")

          return "phantomjs #{cssDiffPath}/phantom-harness.coffee
            #{cssDiffPath}
            #{process.cwd()}/#{lessFile}
            #{process.cwd()}/#{tempDir}/collection.xhtml
            #{bakedXhtmlFile}
          "

      # 4. Generate Diff if the last argument is not 'master'
      'create-diff':
        command: (bookName, branchName='new') ->
          if branchName == 'master'
            grunt.log.writeln('No diff to make because the branch is master')
          else
            cssDiffPath = './node_modules/css-diff'
            masterXhtmlFile = "#{config.testingDir}/#{bookName}-master.xhtml"
            bakedXhtmlFile = "#{config.testingDir}/#{bookName}-#{branchName}.xhtml"

            failIfNotExists("Baked master XHTML file missing.", masterXhtmlFile)
            failIfNotExists("Baked XHTML file missing.")        if not fs.existsSync(bakedXhtmlFile)

            return "xsltproc
              --stringparam oldPath #{process.cwd()}/#{masterXhtmlFile}
              #{cssDiffPath}/compare.xsl
              #{bakedXhtmlFile} > #{config.testingDir}/#{bookName}-diff.xhtml
            "


  grunt.registerTask 'diff-book', 'Perform a regression', (bookName) ->
    branchName = 'new'
    grunt.log.writeln('Use --verbose to see the output because these take a while.')
    grunt.task.run("shell:pdf:#{bookName}:#{branchName}")
    grunt.task.run("shell:bake:#{bookName}:#{branchName}")
    grunt.task.run("shell:create-diff:#{bookName}:#{branchName}")
    if config.coverage
      grunt.task.run("shell:coverage:#{bookName}:#{branchName}")


  grunt.registerTask 'prepare-book', 'Generate the master versions of books to compare against', (bookName) ->
    grunt.log.writeln('Use --verbose to see the output because these take a while.')
    grunt.task.run("shell:pdf:#{bookName}:master")
    grunt.task.run("shell:bake:#{bookName}:master")
    if config.coverage
      grunt.task.run("shell:coverage:#{bookName}:master")


  # Dependencies
  # ============
  for name of pkg.dependencies when name.substring(0, 6) is 'grunt-'
    grunt.loadNpmTasks(name)
  for name of pkg.devDependencies when name.substring(0, 6) is 'grunt-'
    if grunt.file.exists("./node_modules/#{name}")
      grunt.loadNpmTasks(name)

  # Tasks
  # =====

  # Used for lessc compiling
  allBooks = [
    'physics'
    'sociology'
    'anatomy'
    'biology'
    'precalculus'
    'statistics'
    'economics'
    'psychology'
  ]
  compileBooks = []
  for bookName in allBooks
    compileBooks.push("shell:compile:#{bookName}")
  grunt.registerTask('compile', 'Generate CSS files for all books', compileBooks)
  grunt.registerTask('default', ['compile'])


  masterBooks = []
  diffBooks = []
  for bookName of config.books
    masterBooks.push("prepare-book:#{bookName}")
    diffBooks.push("diff-book:#{bookName}")

  if masterBooks.length
    grunt.registerTask('prepare', 'Prepare files for diffing assuming this is the master branch', masterBooks)
    grunt.registerTask('diff', 'Generate diffs against the prepared files generated on the master branch', diffBooks)


  else
    grunt.log.writeln('Configure at least one book path in config.yml')
