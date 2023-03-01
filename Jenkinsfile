pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh 'sudo ./configure.sh'
      }
    }

    stage('Test') {
      steps {
        sh 'sudo ./configure.sh'
        sh 'python3 -m pytest'
      }
    }

  }
}
