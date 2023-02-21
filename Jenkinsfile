pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh './configure.sh'
      }
    }

    stage('Test') {
      steps {
        sh 'python3 -m pytest'
      }
    }

  }
}
