pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh './configure.sh'
      }
    }

    stage('Pre-commit') {
      steps {
        sh '''
        export PATH=$PWD/.venv/bin:$PATH
        pre-commit run --all-files
        '''
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
