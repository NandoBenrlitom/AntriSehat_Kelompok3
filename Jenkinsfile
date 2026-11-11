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
                bat 'docker build --target test -t %IMAGE%:test .'
            }
        }
        stage('Build Image') {
            steps {
                bat 'docker build -t %IMAGE%:%TAG% -t %IMAGE%:latest .'
            }
        }
        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    bat 'echo %PASS% | docker login -u %USER% --password-stdin'
                    bat 'docker push %IMAGE%:%TAG% && docker push %IMAGE%:latest'
                }
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'antrisehat-env', variable: 'ENV_FILE')]) {
                    bat 'copy %ENV_FILE% .env'
                    bat 'docker compose pull app scheduler && docker compose up -d'
                }
            }
        }
        stage('Smoke Test') {
            steps {
                bat '''
                    timeout /t 15 /nobreak >nul
                    powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:8000/health' -Method Get } catch { exit 1 }"
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