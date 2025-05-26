## Based on Original Work

This project is based on the [amazon-eks-kubernetes-api-aws-lambda](https://github.com/aws-samples/amazon-eks-kubernetes-api-aws-lambda) sample by AWS.

### 🔧 Modifications include:

## 1. AWS Profile Selection

The deployment script now prompts:

> "Are you using multiple AWS profiles?"

- If you answer **yes**, it will list available profiles and let you choose one.
- If you answer **no**, it proceeds using the default AWS credentials (from `aws configure`, environment variables, or IAM role).

No extra configuration is required if you're already authenticated with default credentials.

---

## 2. Lambda Code Refactored into Two Files

The Lambda function code has been modularized for clarity and maintainability:

- **`lambda_function.py`**: The main Lambda handler triggered by API Gateway.
- **`kubeconfig.py`**: A helper module that:
  - Retrieves the Kubernetes authentication token using the AWS EKS API.
  - Returns a valid `kubeconfig` structure for temporary access.

This separation makes the code easier to read, test, and extend.
➡️ It also helps you to focus on editing only the main Lambda logic, where you can use any Kubernetes API you want — such as interacting with pods, deployments, services, or other resources —without needing to modify or navigate the underlying authentication code.

