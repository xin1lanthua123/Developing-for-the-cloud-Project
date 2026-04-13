apiVersion: apps/v1
kind: Deployment
metadata:
  name: incident-api
  namespace: incident-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: incident-api
  template:
    metadata:
      labels:
        app: incident-api
    spec:
      serviceAccountName: backend-incident-sa
      containers:
        - name: incident-api
          image: ${ECR_REPO_URI}:${IMAGE_TAG}
          ports:
            - containerPort: 8000
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "250m"
              memory: "256Mi"
          env:
            - name: DDB_TABLE_NAME
              value: ${DDB_TABLE_NAME}

            - name: UPLOAD_BUCKET_NAME
              value: ${UPLOAD_BUCKET_NAME}

            - name: AWS_REGION
              value: ${AWS_REGION}

            - name: AWS_DEFAULT_REGION
              value: ${AWS_REGION}

            - name: COGNITO_REGION
              value: ${AWS_REGION}

            - name: COGNITO_USER_POOL_ID
              value: ${COGNITO_USER_POOL_ID}

            - name: COGNITO_CLIENT_ID
              value: ${COGNITO_CLIENT_ID}

            - name: JIRA_BASE_URL
              valueFrom:
                secretKeyRef:
                  name: jira-secret
                  key: JIRA_BASE_URL

            - name: JIRA_EMAIL
              valueFrom:
                secretKeyRef:
                  name: jira-secret
                  key: JIRA_EMAIL

            - name: JIRA_TOKEN
              valueFrom:
                secretKeyRef:
                  name: jira-secret
                  key: JIRA_TOKEN

            - name: JIRA_PROJECT_KEY
              valueFrom:
                secretKeyRef:
                  name: jira-secret
                  key: JIRA_PROJECT_KEY