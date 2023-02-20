pipeline {
    agent any
    stages {
        stage('Configure') {
            steps {
                echo 'Configuring...'
                sh 'source configure.sh'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
                sh 'pytest'
            }
        }
    }
}

  }
}