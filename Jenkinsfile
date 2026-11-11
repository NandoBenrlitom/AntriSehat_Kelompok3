pipeline {
    agent any

    triggers {
        githubPush()
        cron('H 1 * * *')
    }

    environment {
        IMAGE = 'haidarmirza/antrisehat'
        TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Test') {
            steps {
                bat 'docker build --target test -t $IMAGE:test .'
            }
        }
        stage('Build Image') {
            steps {
                sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
            }
        }
        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh 'echo $PASS | docker login -u $USER --password-stdin'
                    sh 'docker push $IMAGE:$TAG && docker push $IMAGE:latest'
                }
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'antrisehat-env', variable: 'ENV_FILE')]) {
                    sh 'cp $ENV_FILE .env'
                    sh 'docker compose pull app scheduler && docker compose up -d'
                }
            }
        }
        stage('Smoke Test') {
            steps {
                sh '''
                    sleep 15
                    curl -fsS http://localhost:8000/health || \
                    curl -fsS http://172.17.0.1:8000/health || \
                    curl -fsS http://host.docker.internal:8000/health
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline sukses: aplikasi dan scheduler AntriSehat berhasil ter-deploy!'
        }
        failure {
            echo 'Pipeline gagal: periksa stage yang berwarna merah pada Stage View.'
        }
    }
}