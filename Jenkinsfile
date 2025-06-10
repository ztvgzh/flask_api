pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "flask-api:${BUILD_NUMBER}"
        TARGET_HOST = "ubuntu@37.9.53.18"
        SSH_CREDENTIALS = "ssh-credentials"
        REMOTE_APP_DIR = "/opt/flask-api"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        skipDefaultCheckout(false)
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker image...'
                script {
                    def dockerImage = docker.build("${DOCKER_IMAGE}")
                    env.DOCKER_IMAGE_ID = dockerImage.id
                }
            }
        }

        stage('Test/Lint') {
            steps {
                echo 'Running code quality checks...'
                script {
                    def dockerImage = docker.image("${DOCKER_IMAGE}")
                    dockerImage.inside {
                        sh '''
                            pip install flake8
                            flake8 app/ --max-line-length=88 --ignore=E203,W503,E302,W293 || echo "Code style issues found but continuing..."
                        '''
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying to target server...'
                script {
                    // Сохраняем образ в tar-файл
                    sh "docker save ${DOCKER_IMAGE} -o flask-api-${BUILD_NUMBER}.tar"
                }
                sshagent([SSH_CREDENTIALS]) {
                    sh """
                        scp flask-api-${BUILD_NUMBER}.tar ${TARGET_HOST}:${REMOTE_APP_DIR}/
                        scp docker-compose.yml ${TARGET_HOST}:${REMOTE_APP_DIR}/
                        scp .env ${TARGET_HOST}:${REMOTE_APP_DIR}/
                        ssh ${TARGET_HOST} '
                            cd ${REMOTE_APP_DIR}
                            docker-compose down
                            docker load -i flask-api-${BUILD_NUMBER}.tar
                            export IMAGE_TAG=${BUILD_NUMBER}
                            docker-compose up -d
                            docker system prune -f
                        '
                    """
                }
                // Опционально удалить локальный tar после деплоя
                sh "rm flask-api-${BUILD_NUMBER}.tar"
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
