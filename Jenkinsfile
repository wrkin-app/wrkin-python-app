pipeline{
    agent any
    stages {
        stage('test script run'){
                steps{
                sh """
                    chmod +x virtual_env.sh
                    ./virtual_env.sh
                   """
                }
        }
        stage('Run') {
            steps{
                sh """
                    JENKINS_NODE_COOKIE=dontKillMe nohup python3 manage.py runserver 0.0.0.0:8000 &
                   """
            }
        } 
                
            }
}