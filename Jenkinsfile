pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh "#!/bin/bash \n" +
           "source configure.sh"
      }
    }

    stage('Test') {
      steps {
        sh 'pytest'
      }
    }

  }
}
