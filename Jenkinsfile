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
    command:
    - cat
    tty: true
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
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
    securityContext:
      privileged: true  # Needed to run Docker daemon
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""  # Disable TLS for simplicity
    volumeMounts:
    - name: docker-config
      mountPath: /etc/docker/daemon.json
      subPath: daemon.json  # Mount the file directly here
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
    
    
    stages {
        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        sleep 15
                        docker build -t text-emotion-detection:latest .
                        docker image ls
                    '''
                }
            }
        }

        stage('Run Tests in Docker') {
            steps {
                container('dind') {
                    sh '''
                        docker run --rm text-emotion-detection:latest \
                        pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml
                    '''
                }
            }
        }
        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    withCredentials([string(credentialsId: 'sonar-token-2401096', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=2401096-Manish_Kenjale \
                                -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
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
                    sh 'docker login nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 -u admin -p Changeme@2025'
                }
            }
        }
        stage('Build - Tag - Push') {
            steps {
                container('dind') {
                    sh 'docker tag text-emotion-detection:latest nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401096-project/text-emotion-detection:latest'
                    sh 'docker push nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401096-project/text-emotion-detection:latest'
                    sh 'docker pull nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401096-project/text-emotion-detection:latest'
                    sh 'docker image ls'
                }
            }
        }
        
        stage('Deploy AI Application') {
  steps {
    container('kubectl') {
      script {
        dir('k8s-deployment') {
          sh """
            # Ensure kubeconfig is mounted at /kube/config by the pod spec (already configured)
            if [ ! -f /kube/config ]; then
              echo "ERROR: kubeconfig not found at /kube/config"
              exit 1
            fi

            # Replace any hard-coded forbidden namespace (2401096) in the manifests with the allowed one.
            # This makes the pipeline idempotent even if the YAML contains namespace: 2401096
            sed -i.bak 's/2401096/${K8S_NAMESPACE}/g' text-emotion-deployment.yaml || true

            # Apply manifests into the allowed namespace
            kubectl apply -f text-emotion-deployment.yaml -n ${K8S_NAMESPACE}

            # Make sure the deployment uses the image just pushed
            kubectl -n ${K8S_NAMESPACE} set image deployment/text-emotion-detection-deployment \
              text-emotion-detection=${FULL_IMAGE} --record

            # Wait for rollout to complete
            kubectl -n ${K8S_NAMESPACE} rollout status deployment/text-emotion-detection-deployment --timeout=120s
          """
        }
      }
    }
  }
}

    }
}