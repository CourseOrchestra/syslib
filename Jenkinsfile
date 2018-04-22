node {
    def server = Artifactory.server 'ART'
    def buildInfo
    def warnings
    
    stage ('Clone') {
        checkout scm
    }
    
    stage ('Static analysis') {
        sh 'rm -f flake8report.txt'
        sh 'flake8 --ignore=E301,E302,E303,E501,W291,W293 --exit-zero --output-file=flake8report.txt'
        sh 'mkdir -p target'
        sh 'echo "flake8_warnings: `wc -l < flake8report.txt`" > target/syslib.yml'
        archive 'flake8report.txt'
        warnings = readYaml file: 'target/syslib.yml'
        echo "Flake8 warnings count: ${warnings.flake8_warnings}"
    }

    stage ('Ratcheting') {
        def downloadSpec = """
         {"files": [
            {
              "pattern": "syslib/*/syslib.yml",
              "build": "syslib :: master/LATEST",
              "target": "previous.yml",
              "flat": "true"
            }
            ]
        }"""
        server.download spec: downloadSpec
        def oldWarnings = readYaml file: 'previous.yml'
        if (warnings.flake8_warnings > oldWarnings.flake8_warnings) {
            error "Number of flake8 warnings ${warnings.flake8_warnings} is greater than previous ${oldWarnings.flake8_warnings}."
        }
    }

    if (env.BRANCH_NAME == 'master') {
        stage ('Compress & upload sources') {
            sh 'tar --exclude=*.class --exclude=target --exclude=templates --exclude=.git --exclude Jenkinsfile --exclude flake8report.txt -zcvf target/syslib.tgz .'
            sh 'tar -zcvf target/syslib.templates.tgz templates'
            def uploadSpec = """
            {
             "files": [
                {
                  "pattern": "target/syslib.*",
                  "target": "syslib/${currentBuild.number}/",
                  "props": "flake8.warnings=${warnings.flake8_warnings}"
                }
                ]
            }"""
            buildInfo = server.upload spec: uploadSpec
            buildInfo.env.capture = true
            server.publishBuildInfo buildInfo
        }
    }
}