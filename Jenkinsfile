pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "urva123ishfaq"
        IMAGE_UNSTABLE = "${DOCKERHUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE   = "${DOCKERHUB_USER}/sentiment-api:stable"
        CONTAINER_NAME = "sentiment-test-container"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                script {
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    sh "docker build -t ${IMAGE_UNSTABLE} ."
                    sh """
                        docker run -d \
                            --name ${CONTAINER_NAME} \
                            -p 5000:5000 \
                            ${IMAGE_UNSTABLE}
                    """
                    sh """
                        for i in \$(seq 1 30); do
                            if curl -sf http://localhost:5000/health; then
                                echo 'App is ready'
                                break
                            fi
                            echo "Waiting for app... attempt \$i"
                            sleep 5
                        done
                    """
                }
            }
        }

        stage('Unit Test') {
            steps {
                script {
                    sh """
                        docker run --rm \
                            --network host \
                            -e BASE_URL=http://localhost:5000 \
                            ${IMAGE_UNSTABLE} \
                            python -m pytest tests/test_api.py -v --tb=short
                    """
                }
            }
        }

        stage('UI Test') {
            steps {
                script {
                    sh "docker rm -f selenium-chrome || true"
                    sh """
                        docker run -d \
                            --name selenium-chrome \
                            --network host \
                            selenium/standalone-chrome:latest
                    """
                    sh "sleep 5"
                    sh """
                        docker run --rm \
                            --network host \
                            -e BASE_URL=http://localhost:5000 \
                            -e SELENIUM_REMOTE_URL=http://localhost:4444/wd/hub \
                            ${IMAGE_UNSTABLE} \
                            python -m pytest tests/test_ui.py -v --tb=short
                    """
                }
            }
        }

        stage('Build and Push') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh "echo \${DOCKER_PASS} | docker login -u \${DOCKER_USER} --password-stdin"
                        sh "docker push ${IMAGE_UNSTABLE}"
                        sh """
                            git fetch origin stable-fallback
                            git checkout origin/stable-fallback -- app.py
                            docker build -t ${IMAGE_STABLE} .
                            docker push ${IMAGE_STABLE}
                            git checkout HEAD -- app.py
                        """
                        sh "docker logout"
                    }
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    sh """
                        kubectl apply -f k8s/pvc.yaml
                        kubectl apply -f k8s/blue-deployment.yaml
                        kubectl apply -f k8s/green-deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl rollout status deployment/sentiment-blue-deployment --timeout=300s
                        kubectl rollout status deployment/sentiment-green-deployment --timeout=300s
                        echo "Deployment complete. NodePort 32500 is live."
                    """
                }
            }
        }

    }

    post {
        always {
            sh "docker rm -f ${CONTAINER_NAME} selenium-chrome || true"
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check logs above."
        }
    }
}
