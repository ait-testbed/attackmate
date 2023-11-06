void setBuildStatus(String message, String state) {
    step([
        $class: "GitHubCommitStatusSetter",
        reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/ait-aecid/attackmate"],
        contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
        errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
        statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
    ]);
}

def  docsimage = false

pipeline {
    agent any
    stages {
        stage("Build Documentation") {
                agent {
                        dockerfile {
                                dir 'docs'
                                args '-u root -v $PWD:/docs'
                                reuseNode true
                        }
                }
        	when {
        	        expression {
        	                BRANCH_NAME == "main" || BRANCH_NAME == "development"
        	        }
        	}
        	steps {
            	        script {
        	                docsimage = true
        	        }
                        dir("docs") {
                                sh "id"
                                sh "ls -la /docs"
        	                sh "make html"
                        }
                }
        }
        stage("Deploy Docs") {
        	when {
        	        expression {
        	                BRANCH_NAME == "main" || BRANCH_NAME == "development"
        	        }
        	}
                steps {
       	                sh "scripts/deploydocs.sh ${env.BRANCH_NAME} docs/build/html /var/www/aeciddocs/attackmate"
                }
        }
    }

    post {
        success {
            setBuildStatus("Build succeeded", "SUCCESS");
        }
        failure {
            setBuildStatus("Build failed", "FAILURE");
        }
    }
}
