module.exports = (grunt) ->

  path = require('path')
  fs = require('fs')
  pkg = require('./package.json')
  config = grunt.file.readYAML('config.yml')

  # Project configuration.
  grunt.initConfig
    pkg: pkg
    config: config

    shell:
      options:
        timeout: 0
        stdout: true

      'compile':
        command: (bookName) ->
          return "lessc css/ccap-#{bookName}.less > css/ccap-#{bookName}.css"

      # 1. Generate a PDF and more importantly, the huge HTML file
      'regress-pdf':
        command: (bookName, branchName='new') ->
          tempDir = "<%= config.testingDir %>/tempdir-#{bookName}-#{branchName}"
          return [
            'mkdir <%= config.testingDir %>'
            'virtualenv .'
            'source ./bin/activate'
            'pip install lxml argparse pillow'
            # Send stderr to /dev/null because grunt falls over with too many log lines
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
      'regress-coverage':
        command: (bookName, branchName='new') ->
          lessFile = "./css/ccap-#{bookName}.less"
          tempDir = "<%= config.testingDir %>/tempdir-#{bookName}-#{branchName}"
          return "node ./node_modules/.bin/css-coverage -d -v
            -s #{lessFile}
            -h #{tempDir}/collection.xhtml
            -l <%= config.testingDir %>/#{bookName}-#{branchName}.lcov"
      # 2b. Generate HTML Report from LCOV file
      'regress-coverage-report':
        command: (bookName, branchName='new') ->
          return "genhtml <%= config.testingDir %>/#{bookName}-#{branchName}.lcov
            --output-directory <%= config.testingDir %>/#{bookName}-#{branchName}-coverage
          "

      # 3. Generate HTML For Later Diffing
      'regress-baked-html':
        command: (bookName, branchName='new') ->
          cssDiffPath = './node_modules/css-diff'
          lessFile = "./css/ccap-#{bookName}.less"
          tempDir = "<%= config.testingDir %>/tempdir-#{bookName}-#{branchName}"
          bakedXhtmlFile = "<%= config.testingDir %>/#{bookName}-#{branchName}.xhtml"
          return "phantomjs #{cssDiffPath}/phantom-harness.coffee
            #{cssDiffPath}
            #{process.cwd()}/#{lessFile}
            #{process.cwd()}/#{tempDir}/collection.xhtml
            #{bakedXhtmlFile}
          "

      # 4. Generate Diff if the last argument is not 'master'
      'regress-create-diff':
        command: (bookName, branchName='new') ->
          if branchName == 'master'
            grunt.log.writeln('No diff to make because the branch is master')
          else
            cssDiffPath = './node_modules/css-diff'
            bakedXhtmlFile = "<%= config.testingDir %>/#{bookName}-#{branchName}.xhtml"
            return "xsltproc
              --stringparam oldPath #{process.cwd()}/<%= config.testingDir %>/#{bookName}-master.xhtml
              #{cssDiffPath}/compare.xsl
              #{bakedXhtmlFile} > <%= config.testingDir %>/#{bookName}-diff.xhtml
            "


  grunt.registerTask 'regress-diff', 'Perform a regression', (bookName) ->
    branchName = 'new'
    grunt.log.writeln('Use --verbose to see the output because these take a while.')
    grunt.task.run("shell:regress-pdf:#{bookName}:#{branchName}")
    grunt.task.run("shell:regress-baked-html:#{bookName}:#{branchName}")
    grunt.task.run("shell:regress-create-diff:#{bookName}:#{branchName}")
    if config.coverage
      grunt.task.run("shell:regress-coverage:#{bookName}:#{branchName}")


  grunt.registerTask 'regress-master', 'Generate the master versions of books to compare against', (bookName) ->
    grunt.log.writeln('Use --verbose to see the output because these take a while.')
    grunt.task.run("shell:regress-pdf:#{bookName}:master")
    grunt.task.run("shell:regress-baked-html:#{bookName}:master")
    if config.coverage
      grunt.task.run("shell:regress-coverage:#{bookName}:master")


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
  grunt.registerTask('compile', compileBooks)
  grunt.registerTask('default', ['compile'])


  masterBooks = []
  diffBooks = []
  for bookName of config.books
    masterBooks.push("regress-master:#{bookName}")
    diffBooks.push("regress-diff:#{bookName}")

  if masterBooks.length
    grunt.registerTask('master-all', masterBooks)
    grunt.registerTask('regress-all', diffBooks)


  else
    grunt.log.writeln('Configure at least one book path in config.yml')
