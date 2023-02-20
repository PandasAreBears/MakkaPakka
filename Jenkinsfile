pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        './configure.sh'
      }
    }

    stage('Test') {
      steps {
        sh 'pytest'
      }
    }

  }
}
