// This file relates to internal XMOS infrastructure and should be ignored by external users

@Library('xmos_jenkins_shared_library@v0.56.0') _

getApproval()
pipeline {

    agent none

    parameters {
        string(
            name: 'TOOLS_VERSION',
            defaultValue: '15.3.1',
            description: 'XTC tools version'
        )
        string(
            name: 'XMOSDOC_VERSION',
            defaultValue: 'v8.1.2',
            description: 'xmosdoc version'
        )
        string(
            name: 'INFR_APPS_VERSION',
            defaultValue: 'v3.6.0',
            description: 'The infr_apps version'
        )
    }

    options {
        skipDefaultCheckout()
        timestamps()
        buildDiscarder(xmosDiscardBuildSettings(onlyArtifacts = false))
    }

    stages {
        stage('🏗️ Build and test') {
            agent {
                label "documentation"
            }

            stages {
                stage('Checkout') {
                    steps {

                        println "Stage running on ${env.NODE_NAME}"

                        script {
                            def (server, user, repo) = extractFromScmUrl()
                            env.REPO_NAME = repo
                        }

                        dir(REPO_NAME) {
                            checkoutScmShallow()
                        }
                    }
                }

                stage('Build, checks, docs') {
                    parallel {
                        stage('Code build') {
                            steps {
                                dir(REPO_NAME) {
                                    xcoreBuild()
                                }
                            }
                        }

                        stage('Repo checks') {
                            steps {
                                warnError("Repo checks failed") {
                                    runRepoChecks("${WORKSPACE}/${REPO_NAME}")
                                }
                            }
                        }

                        stage('Doc build') {
                            steps {
                                dir(REPO_NAME) {
                                    buildDocs()
                                }
                            }
                        }
                    }
                }

                stage("Archive sandbox") {
                    steps {
                        archiveSandbox(REPO_NAME)
                    }
                }
            } // stages
            post {
                cleanup {
                    xcoreCleanSandbox()
                }
            }
        } // stage 'Build and test'

        stage('Tests') {
            parallel {
                stage('Linux') {
                    agent {
                        label 'xcore.ai'
                    }
                    steps {
                        println "Stage running on ${env.NODE_NAME}"
                        dir("${REPO_NAME}") {
                            checkoutScmShallow()
                        }
                        dir("${REPO_NAME}/tests") {
                            withTools(params.TOOLS_VERSION) {
                                createVenv(reqFile: "requirements.txt")
                                withVenv {
                                    sh "pytest test_all.py -vv"
                                }
                            }
                        }
                    }
                    post {
                        always {
                            dir("${REPO_NAME}/tests") {
                                junit testResults: 'pytest-junit.xml', allowEmptyResults: true
                            }
                        }
                        cleanup {
                            xcoreCleanSandbox()
                        }
                    }
                }
                stage('Mac') {
                    agent {
                        label 'xcore.ai-mcab && macos'
                    }
                    steps {
                        println "Stage running on ${env.NODE_NAME}"
                        dir("${REPO_NAME}") {
                            checkoutScmShallow()
                        }
                        dir("${REPO_NAME}/tests") {
                            withTools(params.TOOLS_VERSION) {
                                createVenv(reqFile: "requirements.txt")
                                withVenv {
                                    sh "pytest test_all.py -vv"
                                }
                            }
                        }
                    }
                    post {
                        always {
                            dir("${REPO_NAME}/tests") {
                                junit testResults: 'pytest-junit.xml', allowEmptyResults: true
                            }
                        }
                        cleanup {
                            xcoreCleanSandbox()
                        }
                    }
                }
                stage('Windows') {
                    agent {
                        label 'xcore.ai-mcab && windows'
                    }
                    steps {
                        println "Stage running on ${env.NODE_NAME}"
                        dir("${REPO_NAME}") {
                            checkoutScmShallow()
                        }
                        dir("${REPO_NAME}/tests") {
                            withTools(params.TOOLS_VERSION) {
                                createVenv(reqFile: "requirements.txt")
                                withVenv {
                                    sh "pytest test_all.py -vv"
                                }
                            }
                        }
                    }
                    post {
                        always {
                            dir("${REPO_NAME}/tests") {
                                junit testResults: 'pytest-junit.xml', allowEmptyResults: true
                            }
                        }
                        cleanup {
                            xcoreCleanSandbox()
                        }
                    }
                }
            }
        }

        stage('🚀 Release') {
            when {
                expression { triggerRelease.isReleasable() }
            }
            steps {
                triggerRelease()
            }
        }
    } // stages
} // pipeline
