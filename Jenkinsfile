// Jenkinsfile (Declarative) - Kubernetes Pod Agent with dind, sonar-scanner and kubectl
// This Jenkinsfile expects the following placeholders to be replaced in Jenkins credentials/config:
// - git-creds (Git credential id)
// - docker-registry-creds (username/password for Nexus)
// - sonar-token-text-emotion (sonar token)
// By default GIT_REPO_URL points to the uploaded file path /mnt/data/app.py for local testing; replace with your Git repo URL.

pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: sonar-scanner
      image: sonarsource/sonar-scanner-cli
      command: ["cat"]
      tty: true

    - name: kubectl
      image: bitnami/kubectl:latest
      command: ["cat"]
      tty: true
      securityContext:
        runAsUser: 0
        readOnlyRootFilesystem: false
      env:
        - name: KUBECONFIG
          value: /kube/config
      volumeMounts:
        - name: kubeconfig-secret
          mountPath: /kube/config
          subPath: kubeconfig

    - name: dind
      image: docker:dind
      args: ["--registry-mirror=https://mirror.gcr.io", "--storage-driver=overlay2"]
      securityContext:
        privileged: true
      env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
      volumeMounts:
        - name: docker-config
          mountPath: /etc/docker/daemon.json
          subPath: daemon.json
  volumes:
    - name: docker-config
      configMap:
        name: docker-daemon-config
    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret
'''
        }
    }

    environment {
        IMAGE_NAME        = "text-emotion-detection"
        IMAGE_TAG         = "v1"
        REGISTRY_URL      = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REGISTRY_REPO     = "ajinkya-project"
        FULL_IMAGE_NAME   = "${REGISTRY_URL}/${REGISTRY_REPO}/${IMAGE_NAME}:${IMAGE_TAG}"

        SONAR_HOST_URL    = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
        SONAR_PROJECT_KEY = "text_emotion_detection_project"
        K8S_NAMESPACE     = "2401096"
        K8S_DEPLOYMENT    = "text-emotion-detection-deployment"
        K8S_MANIFEST_FILE = "text-emotion-deployment.yaml"

        // Default branch to checkout. Change to 'master' if required.
        GIT_BRANCH        = 'main'
        // Use uploaded file path as repo URL for local testing; replace with actual git repo URL.
        GIT_REPO_URL      = '/mnt/data/app.py'
    }

    options {
        timestamps()
        skipStagesAfterUnstable()
        ansiColor('xterm')
    }

    stages {

        stage('Checkout') {
            steps {
                // Use an explicit valid refspec and branch; avoids invalid 'refs/heads/**' errors
                script {
                    checkout([$class: 'GitSCM',
                        branches: [[name: "*/${GIT_BRANCH}"]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        userRemoteConfigs: [[url: GIT_REPO_URL, credentialsId: 'git-creds', refspec: '+refs/heads/*:refs/remotes/origin/*']]
                    ])
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                      sleep 15
                      docker build -t ${IMAGE_NAME}:latest .
                      docker image ls
                    '''
                }
            }
        }

        stage('Run Tests in Docker') {
            steps {
                container('dind') {
                    sh '''
                      # Adjust this command based on how you run tests in the container
                      if docker run --rm ${IMAGE_NAME}:latest pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml; then
                        echo "Tests passed"
                      else
                        echo "Tests failed"
                        exit 1
                      fi
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    withCredentials([string(credentialsId: 'sonar-token-text-emotion', variable: 'SONAR_TOKEN')]) {
                        sh '''
                          sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=$SONAR_TOKEN \
                            -Dsonar.python.coverage.reportPaths=coverage.xml
                        '''
                    }
                }
            }
        }

        stage('Login to Docker Registry') {
            steps {
                container('dind') {
                    sh 'docker --version'
                    sh 'sleep 10'
                    withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                          echo "$DOCKER_PASS" | docker login ${REGISTRY_URL} \
                            --username "$DOCKER_USER" \
                            --password-stdin
                        '''
                    }
                }
            }
        }

        stage('Build - Tag - Push') {
            steps {
                container('dind') {
                    sh '''
                      docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}
                      docker push ${FULL_IMAGE_NAME}
                      docker pull ${FULL_IMAGE_NAME}
                      docker image ls
                    '''
                }
            }
        }

        stage('Deploy Text Emotion App') {
            steps {
                container('kubectl') {
                    script {
                        dir('k8s-deployment') {
                            sh """
                              kubectl apply -f ${K8S_MANIFEST_FILE}
                              kubectl rollout status deployment/${K8S_DEPLOYMENT} -n ${K8S_NAMESPACE}
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. Image: ${FULL_IMAGE_NAME}"
        }
        failure {
            echo "Pipeline failed. Check the logs for details."
        }
        always {
            // best-effort cleanup / info
            container('dind') {
                sh 'docker image ls --format "{{.Repository}}:{{.Tag}}\t{{.ID}}" | sed -n "1,20p" || true'
            }
        }
    }
}
