pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh 'source configure.sh'
      }
    }

    stage('Test') {
      steps {
        sh 'source configure.sh'
        sh 'python3 -m pytest'
      }
    }

  }
}
