module "fdio-logs" {
  # fdio logs iam
  source         = "../terraform-vault-aws-secret-backend"
  name           = "dynamic-aws-creds-vault-fdio-logs"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  policy_document = jsonencode({
    Statement = [
      {
        Action = [
          "iam:*",
          "ec2:*",
          "s3:*",
          "elasticbeanstalk:*",
          "ssm:*",
          "cloudformation:*",
          "logs:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "cloudwatch:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
    Version = "2012-10-17"
  })
}

module "csit-cdash" {
  # csit cdash iam
  source         = "../terraform-vault-aws-secret-backend"
  name           = "dynamic-aws-creds-vault-cdash"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  policy_document = jsonencode({
    Statement = [
      {
        Action = [
          "iam:*",
          "ec2:*",
          "s3:*",
          "elasticbeanstalk:*",
          "ssm:*",
          "cloudformation:*",
          "logs:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "cloudwatch:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
    Version = "2012-10-17"
  })
}

module "fdio-csit-jenkins" {
  # fdio csit jenkins iam
  source         = "../terraform-vault-aws-secret-backend"
  name           = "dynamic-aws-creds-vault-fdio-csit-jenkins"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  policy_document = jsonencode({
    Statement = [
      {
        Action = [
          "iam:*",
          "ec2:*",
          "s3:*",
          "elasticbeanstalk:*",
          "ssm:*",
          "cloudformation:*",
          "logs:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "cloudwatch:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
    Version = "2012-10-17"
  })
}
