module.exports = (grunt) ->

  path = require('path')
  fs = require('fs')
  pkg = require('./package.json')
  chalk = require('chalk')
  try
    config = grunt.file.readYAML('config.yml')
  catch e
    console.warn 'Missing config.yml but continuing anyway'
    config = {}

  # Use local phantomjs
  PHANTOMJS_BIN = './node_modules/css-diff/node_modules/.bin/phantomjs'

  failIfNotExists = (message, filePath) ->
    throw new Error("#{message}. Expected #{filePath} to exist.") if not fs.existsSync(filePath)

  skipIfExists = (taskName, filePath) ->
    if config.skipping?[taskName] and fs.existsSync(filePath)
      grunt.log.writeln("#{chalk.bgBlue('Skipping step because target file exists:')} #{filePath}")
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
          return "./node_modules/.bin/lessc css/ccap-#{bookName}.less > css/ccap-#{bookName}.css"

      # 1. Generate a PDF and more importantly, the huge HTML file
      'pdf':
        command: (bookName, branchName='new') ->
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"

          # Shortcut if skipping flag is set
          return '' if skipIfExists('pdf', "#{tempDir}/collection.xhtml")

          # Make sure the files exist
          failIfNotExists('Path to PrinceXML does not exist', config.prince)
          failIfNotExists('Path to unzipped collection does not exist', config.books[bookName])
          failIfNotExists('Path to unzipped collection is invalid', "#{config.books[bookName]}/collection.xml")
          failIfNotExists('Unzipped Docbook does not exist', './docbook-xsl/VERSION')
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

      'pdf-only':
        command: (bookName, branchName='new') ->
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"
          cssFile = "./css/ccap-#{bookName}.css"
          htmlFile = "#{tempDir}/collection.xhtml"
          pdfFile = "#{config.testingDir}/#{bookName}-#{branchName}.pdf"

          # Shortcut if skipping flag is set
          return '' if skipIfExists('pdfOnly', pdfFile)

          # Make sure the files exist
          failIfNotExists('Path to PrinceXML does not exist', config.prince)
          failIfNotExists('Path to generated HTML does not exist', "#{tempDir}/collection.xhtml")
          failIfNotExists('CSS file does not exist', "./css/ccap-#{bookName}.css")

          return "#{config.prince}
            --style=#{cssFile}
            --output=#{pdfFile}
            #{htmlFile}
            2> /dev/null
          "

      # 2. Generate HTML Coverage Report (optional)
      # 2a. Generate LCOV file
      'coverage':
        command: (bookName, branchName='new') ->
          lessFile = "./css/ccap-#{bookName}.less"
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"
          lcovFile = "#{config.testingDir}/#{bookName}-#{branchName}.lcov"

          # Shortcut if skipping flag is set
          return '' if skipIfExists('coverage', lcovFile)

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

          # Shortcut if skipping flag is set
          return '' if skipIfExists('bake', bakedXhtmlFile)

          failIfNotExists("Less file does not exist: #{lessFile}", lessFile)
          failIfNotExists("XHTML file missing. generate with `grunt shell:pdf:#{bookName}`: #{tempDir}/collection.xhtml", "#{tempDir}/collection.xhtml")

          return "#{PHANTOMJS_BIN} #{cssDiffPath}/phantom-harness.coffee
            #{cssDiffPath}
            #{process.cwd()}/#{lessFile}
            #{process.cwd()}/#{tempDir}/collection.xhtml
            #{bakedXhtmlFile}
          "

      # Like `bake` except the styling is in a separate CSS file instead of `style="..."`
      'preview':
        command: (bookName, branchName='new') ->
          cssDiffPath = './node_modules/css-diff'
          lessFile = "./css/ccap-#{bookName}.less"
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"
          previewXhtmlFile = "#{tempDir}/preview.xhtml"
          previewCssFile = "#{tempDir}/preview.css"

          # Shortcut if skipping flag is set
          return '' if skipIfExists('preview', previewXhtmlFile)

          failIfNotExists("LESS file missing", lessFile)
          failIfNotExists("XHTML file missing. generate with `grunt shell:pdf:#{bookName}`", "#{tempDir}/collection.xhtml")

          return [
            "#{PHANTOMJS_BIN} #{cssDiffPath}/phantom-harness.coffee
              #{cssDiffPath}
              #{process.cwd()}/#{lessFile}
              #{process.cwd()}/#{tempDir}/collection.xhtml
              #{previewXhtmlFile}
              #{previewCssFile}
            "
            "sed -i '' 's/\\<body\\>/<body><link rel=\"stylesheet\" href=\"preview.css\" \\/>/' #{previewXhtmlFile}"

          ].join('; ')

      'preview-link':
        command: (bookName, branchName='new') ->
          imagesDir = "./css/ccap-#{bookName}"
          tempDir = "#{config.testingDir}/tempdir-#{bookName}-#{branchName}"
          bakedXhtmlFile = "#{config.testingDir}/#{bookName}-#{branchName}.xhtml"
          previewFile = "#{tempDir}/preview.xhtml"
          return [
            "ln -s #{imagesDir} #{config.testingDir}/ccap-#{bookName}"
          ].join('; ')


      # 4. Generate Diff if the last argument is not 'master'
      'create-diff':
        options: stdout: true # show the number of differences
        command: (bookName, branchName='new') ->
          if branchName == 'master'
            grunt.log.writeln('No diff to make because the branch is master')
          else
            cssDiffPath = './node_modules/css-diff'
            masterXhtmlFile = "#{config.testingDir}/#{bookName}-master.xhtml"
            bakedXhtmlFile = "#{config.testingDir}/#{bookName}-#{branchName}.xhtml"

            failIfNotExists("Baked master XHTML file missing.", masterXhtmlFile)
            failIfNotExists("Baked XHTML file missing.")        if not fs.existsSync(bakedXhtmlFile)

            return "echo '#{chalk.bgGreen('Differences found:')} ' && xsltproc
              --stringparam oldPath #{process.cwd()}/#{masterXhtmlFile}
              --output #{config.testingDir}/#{bookName}-diff.xhtml
              #{cssDiffPath}/compare.xsl
              #{bakedXhtmlFile} 2>&1 | wc -l
            "

  grunt.registerTask 'diff-book', 'Perform a regression', (bookName) ->
    branchName = 'new'
    grunt.log.writeln('Use --verbose to see the output because these take a while.')
    grunt.task.run("shell:pdf:#{bookName}:#{branchName}")
    # grunt.task.run("shell:preview:#{bookName}:#{branchName}")
    grunt.task.run("shell:bake:#{bookName}:#{branchName}")
    grunt.task.run("shell:create-diff:#{bookName}:#{branchName}")
    if config.coverage
      grunt.task.run("shell:coverage:#{bookName}:#{branchName}")


  grunt.registerTask 'prepare-book', 'Generate the master versions of books to compare against', (bookName) ->
    grunt.log.writeln('Use --verbose to see the output because these take a while.')
    grunt.task.run("shell:pdf:#{bookName}:master")
    # grunt.task.run("shell:preview:#{bookName}:master")
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
    'history'
  ]
  compileBooks = []
  for bookName in allBooks
    compileBooks.push("shell:compile:#{bookName}")
  grunt.registerTask('compile', 'Generate CSS files for all books', compileBooks)
  grunt.registerTask('default', ['compile'])


  if config.books
    grunt.registerTask 'prepare', 'Prepare files for diffing assuming this is the master branch', (bookName=null) ->
      if bookName
        grunt.task.run("prepare-book:#{bookName}")
      else
        for bookName of config.books
          grunt.task.run("prepare-book:#{bookName}")

    grunt.registerTask 'diff', 'Generate diffs against the prepared files generated on the master branch', (bookName) ->
      if bookName
        grunt.task.run("diff-book:#{bookName}")
      else
        for bookName of config.books
          grunt.task.run("diff-book:#{bookName}")



  else
    grunt.log.writeln('Configure at least one book path in config.yml')
