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
        sh '''
        export PATH=$PWD/.venv/bin:$PATH
        python3 -m pytest
        '''
      }
    }

  }
}
