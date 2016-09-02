import groovy.json.JsonSlurper

def env = System.getenv()

def scriptPath = new File(__FILE__)
def rootPath = scriptPath.getParentFile().getParentFile()

def jsonSlurper = new JsonSlurper()

def justDockerfilesConfigPath = env.get("JUST_DOCKERFILES_CONFIG") ?: new File(rootPath, "just-dockerfiles.json").getAbsolutePath()
def justDockerfilesConfigFile = new File(justDockerfilesConfigPath)
def justDockerfilesConfig = jsonSlurper.parseText(justDockerfilesConfigFile.getText())

def testGithubOrg = justDockerfilesConfig.testGithubOrg
def testGithubProject = justDockerfilesConfig.testGithubProject
def targetGithubOrg = justDockerfilesConfig.targetGithubOrg
def targetGithubProject = justDockerfilesConfig.targetGithubProject

def jobViewName = justDockerfilesConfig.jobViewName
def baseJobName = justDockerfilesConfig.baseJobName


def engine = new groovy.text.SimpleTemplateEngine()

recipePath = new File(rootPath, 'recipes')

testShellTemplate = engine.createTemplate('''
if [ ! -d ${testGithubProject} ];
then
    git clone --recursive git://github.com/${testGithubOrg}/${testGithubProject}.git
fi
cd ${testGithubProject};
git pull;
make run-test TARGET_ROOT=`pwd`/".." RECIPE_NAME="$testName" REPORT=`pwd`/../\\${BUILD_TAG}-report.xml
''')

recipePath.eachFile {
    def recipeName = it.name
    def jobName = "${baseJobName}${recipeName}"
    println "tets here"
    def sout = new StringBuilder(), serr = new StringBuilder()
    def proc = "make dump-description RECIPE_NAME=${recipeName}".execute(null, rootPath)
    proc.consumeProcessOutput(sout, serr)
    proc.waitForOrKill(30000)
    println "out> $sout err> $serr"
    def defJsonString = new File(it, "def.json").text
    def recipeDef = jsonSlurper.parseText(defJsonString)
    templateBinding = [
        "testGithubOrg": testGithubOrg,
        "testGithubProject": testGithubProject,
        "testName": recipeName
    ]
    def shellCommand = testShellTemplate.make(templateBinding).toString()
    def fields = justDockerfilesConfig.customFields ?: []
    def fieldsHtml = fields.collect {
        "<p><em>${it.label}</em>: <pre>${recipeDef.get(it.name, '')}</pre></p>"
    }.join("")

    def jenkinsDescription = """<p>${recipeDef["description"]}</p>
$fieldsHtml
<p>This test can be executed locally with the following command:</p>
<pre>
${shellCommand}
</pre>
    """
    job(jobName) {
        description(jenkinsDescription)
        
        scm {
            github "${targetGithubOrg}/${targetGithubProject}"
        }
        triggers {
            cron("@daily")
        }
        steps {
            shell(shellCommand)
        }
        publishers {
            archiveJunit '${BUILD_TAG}-report.xml'
        }
    }
}

listView("${jobViewName}") {
    description("All ${jobViewName} jobs")
    filterBuildQueue()
    filterExecutors()
    jobs {
        name("${baseJobName}")
        regex(/${baseJobName}.+/)
    }
    jobFilters {
    }
    columns {
        status()
        name()
        lastDuration()
        buildButton()
    }
}
