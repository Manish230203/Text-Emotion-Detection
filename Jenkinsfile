// Jenkinsfile — Kubernetes Pod Agent with explicit git container, dind, sonar-scanner and kubectl
// IMPORTANT: Replace credential IDs and any placeholder env vars as needed.

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
      volumeMounts:
        - mountPath: /home/jenkins/agent
          name: workspace-volume

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
        - mountPath: /home/jenkins/agent
          name: workspace-volume

    - name: dind
      image: docker:dind
      args: ["--storage-driver=overlay2"]   # removed registry-mirror flag to avoid duplication with daemon.json
      securityContext:
        privileged: true
      env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
      volumeMounts:
        - name: docker-config
          mountPath: /etc/docker/daemon.json
          subPath: daemon.json
        - mountPath: /home/jenkins/agent
          name: workspace-volume

    - name: git
      image: bitnami/git:latest
      command: ["cat"]
      tty: true
      volumeMounts:
        - mountPath: /home/jenkins/agent
          name: workspace-volume

    - name: jnlp
      image: jenkins/inbound-agent:3345.v03dee9b_f88fc-1
      env:
        - name: JENKINS_AGENT_WORKDIR
          value: /home/jenkins/agent
      volumeMounts:
        - mountPath: /home/jenkins/agent
          name: workspace-volume

  nodeSelector:
    kubernetes.io/os: "linux"
  restartPolicy: "Never"
  volumes:
    - name: docker-config
      configMap:
        name: docker-daemon-config
    - name: workspace-volume
      emptyDir: {}
    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret
'''
    }
  }

  // Prevent the automatic pipeline SCM checkout (which runs on jnlp and may not have git)
  options {
    skipDefaultCheckout()
    skipStagesAfterUnstable()
  }

  environment {
    // URL points to the uploaded local path (tool will transform path -> url). Replace with remote git URL if needed.
    GIT_REPO_URL      = '/mnt/data/app.py'
    GIT_BRANCH        = 'main' // change to 'master' if your repo uses master
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
  }

  stages {
    stage('Checkout') {
      steps {
        container('git') {
          script {
            // explicit checkout inside git container to avoid "git not found" on jnlp
            checkout([$class: 'GitSCM',
              branches: [[name: "*/${GIT_BRANCH}"]],
              doGenerateSubmoduleConfigurations: false,
              extensions: [],
              userRemoteConfigs: [[url: env.GIT_REPO_URL, credentialsId: 'git-creds', refspec: '+refs/heads/*:refs/remotes/origin/*']]
            ])
          }
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        container('dind') {
          sh '''
            # wait for dind to initialize a bit
            sleep 12
            docker version || true
            docker build -t ${IMAGE_NAME}:latest .
            docker image ls --format "{{.Repository}}:{{.Tag}}\\t{{.ID}}"
          '''
        }
      }
    }

    stage('Run Tests in Docker') {
      steps {
        container('dind') {
          sh '''
            # run tests inside a temporary container created from the built image
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
                -Dsonar.python.coverage.reportPaths=coverage.xml || true
            '''
          }
        }
      }
    }

    stage('Login to Docker Registry') {
      steps {
        container('dind') {
          withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh '''
              docker --version || true
              echo "$DOCKER_PASS" | docker login ${REGISTRY_URL} --username "$DOCKER_USER" --password-stdin
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
            docker pull ${FULL_IMAGE_NAME} || true
            docker image ls --format "{{.Repository}}:{{.Tag}}\\t{{.ID}}"
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
                # ensure manifest references correct image or uses imagePullPolicy: Always
                kubectl apply -f ${K8S_MANIFEST_FILE}
                kubectl -n ${K8S_NAMESPACE} rollout status deployment/${K8S_DEPLOYMENT} --timeout=120s
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
      echo "Pipeline failed. Check console logs for details."
    }
    always {
      script {
        try {
          container('dind') {
            sh 'docker image ls --format "{{.Repository}}:{{.Tag}}\\t{{.ID}}" | sed -n "1,30p" || true'
          }
        } catch (err) {
          echo "dind container not available for post-step listing."
        }
      }
    }
  }
}
