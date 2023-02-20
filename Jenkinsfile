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
        sh 'pytest'
      }
    }

  }
}
