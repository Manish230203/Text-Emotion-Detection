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
    IMAGE_NAME = "text-emotion-detection"
    IMAGE_TAG = "latest"
    FULL_IMAGE = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085/2401096-project/text-emotion-detection:${IMAGE_TAG}"
    // Use an existing namespace you have permissions for (2401199 recommended)
    K8S_NAMESPACE = "2401199"
  }

  stages {
    stage('Build Docker Image') {
      steps {
        container('dind') {
          sh '''
            sleep 15
            docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
            docker image ls
          '''
        }
      }
    }

    stage('Run Tests in Docker') {
      steps {
        container('dind') {
          sh '''
            docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
              pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml || true
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
                -Dsonar.python.coverage.reportPaths=coverage.xml || true
            '''
          }
        }
      }
    }

    stage('Login to Docker Registry') {
      steps {
        container('dind') {
          // Use Jenkins credentials (username/password) instead of hardcoding
          withCredentials([usernamePassword(credentialsId: 'nexus-docker-cred-id', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh '''
              docker --version
              sleep 5
              echo "$DOCKER_PASS" | docker login nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 -u "$DOCKER_USER" --password-stdin
            '''
          }
        }
      }
    }

    stage('Build - Tag - Push') {
      steps {
        container('dind') {
          sh '''
            docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE}
            docker push ${FULL_IMAGE}
            docker pull ${FULL_IMAGE} || true
            docker image ls
          '''
        }
      }
    }

    stage('Deploy AI Application') {
      steps {
        container('kubectl') {
          script {
            dir('k8s-deployment') {
              // copy kubeconfig from the mounted secret and run kubectl commands
              sh '''
                # ensure kubeconfig exists at expected mount (from pod spec)
                if [ ! -f /kube/config ]; then
                  echo "ERROR: kubeconfig not found at /kube/config"
                  exit 1
                fi

                # Apply manifests to the namespace we have access to (K8S_NAMESPACE)
                kubectl apply -f text-emotion-deployment.yaml -n ${K8S_NAMESPACE}

                # Ensure the deployment uses the image we built (idempotent)
                kubectl -n ${K8S_NAMESPACE} set image deployment/text-emotion-detection-deployment text-emotion-detection=${FULL_IMAGE} --record || true

                # Wait for rollout to finish
                kubectl -n ${K8S_NAMESPACE} rollout status deployment/text-emotion-detection-deployment --timeout=120s
              '''
            }
          }
        }
      }
    }
  }

  post {
    always {
      container('dind') {
        sh 'docker image prune -f || true'
      }
    }
    success {
      echo "Pipeline completed successfully."
    }
    failure {
      echo "Pipeline failed. Check logs."
    }
  }
}
