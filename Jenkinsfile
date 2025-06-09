pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "flask-api:${BUILD_NUMBER}"
        DOCKER_REGISTRY = "localhost:5001" 
        DOCKER_REPO = "flask-api"
        TARGET_HOST = "ubuntu@37.9.53.180" 
        SSH_CREDENTIALS = "ssh-credentials" // ID ваших SSH credentials в Jenkins
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
                    dockerImage = docker.build("${DOCKER_IMAGE}")
                }
            }
        }
        
        stage('Test/Lint') {
            steps {
                echo 'Running code quality checks...'
                script {
                    // Запуск линтера внутри Docker контейнера
                    dockerImage.inside {
                        sh '''
                            pip install flake8
                            flake8 app/ --max-line-length=88 --ignore=E203,W503
                            echo "Code quality check passed!"
                        '''
                    }
                }
            }
        }
        
        stage('Push') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        dockerImage.push("${BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying to target server...'
                sshagent([SSH_CREDENTIALS]) {
                    sh '''
                        # Копирование docker-compose.yml и .env на целевой сервер
                        scp docker-compose.yml ${TARGET_HOST}:/opt/flask-api/
                        scp .env ${TARGET_HOST}:/opt/flask-api/
                        
                        # Подключение к серверу и запуск контейнеров
                        ssh ${TARGET_HOST} "
                            cd /opt/flask-api
                            docker-compose down
                            docker pull ${DOCKER_REGISTRY}/${DOCKER_REPO}:${BUILD_NUMBER}
                            export IMAGE_TAG=${BUILD_NUMBER}
                            docker-compose up -d
                            docker system prune -f
                        "
                    '''
                }
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
