locals {
  tags = {
    "Name"        = "${var.application_name}"
    "Environment" = "${var.application_name}"
  }
}

# Create elastic beanstalk VPC
resource "aws_vpc" "vpc" {
  assign_generated_ipv6_cidr_block = true
  cidr_block                       = var.vpc_cidr_block
  enable_dns_hostnames             = var.vpc_enable_dns_hostnames
  enable_dns_support               = var.vpc_enable_dns_support
  instance_tenancy                 = var.vpc_instance_tenancy
  tags                             = local.tags
}

# Create elastic beanstalk Subnets
resource "aws_subnet" "subnet" {
  depends_on = [
    aws_vpc.vpc
  ]
  availability_zone               = var.subnet_availability_zone
  assign_ipv6_address_on_creation = true
  cidr_block                      = aws_vpc.vpc.cidr_block
  ipv6_cidr_block                 = cidrsubnet(aws_vpc.vpc.ipv6_cidr_block, 8, 1)
  map_public_ip_on_launch         = true
  vpc_id                          = aws_vpc.vpc.id
  tags                            = local.tags
}

resource "aws_internet_gateway" "internet_gateway" {
  depends_on = [
    aws_vpc.vpc
  ]
  vpc_id = aws_vpc.vpc.id
  tags   = local.tags
}

# Create elastic beanstalk IAM mapping
data "aws_iam_policy_document" "service" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["elasticbeanstalk.amazonaws.com"]
    }
    effect = "Allow"
  }
}

resource "aws_iam_role" "service" {
  assume_role_policy = data.aws_iam_policy_document.service.json
  name               = "${var.application_name}-eb-service"
}

resource "aws_iam_role_policy_attachment" "enhanced_health" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"
  role       = aws_iam_role.service.name
}

resource "aws_iam_role_policy_attachment" "service" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService"
  role       = aws_iam_role.service.name
}

data "aws_iam_policy_document" "ec2" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    effect = "Allow"
  }
  statement {
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }
    effect = "Allow"
  }
}

resource "aws_iam_role" "ec2" {
  assume_role_policy = data.aws_iam_policy_document.ec2.json
  name               = "${var.application_name}-ec2-role"
}

resource "aws_iam_role_policy_attachment" "elastic_beanstalk_multi_container_docker" {
  depends_on = [
    aws_iam_role.ec2
  ]
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
  role       = aws_iam_role.ec2.name
}

resource "aws_iam_instance_profile" "ec2_iam_instance_profile" {
  depends_on = [
    aws_iam_role.ec2
  ]
  name = "${var.application_name}-iam-instance-profile"
  role = aws_iam_role.ec2.name
}

resource "aws_iam_role_policy_attachment" "web_tier" {
  depends_on = [
    aws_iam_role.ec2
  ]
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
  role       = aws_iam_role.ec2.name
}

resource "aws_iam_role_policy_attachment" "worker_tier" {
  depends_on = [
    aws_iam_role.ec2
  ]
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
  role       = aws_iam_role.ec2.name
}

resource "aws_iam_role_policy_attachment" "ssm_automation" {
  depends_on = [
    aws_iam_role.ec2
  ]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole"
  role       = aws_iam_role.ec2.name
}

resource "aws_iam_role_policy_attachment" "ssm_ec2" {
  depends_on = [
    aws_iam_role.ec2
  ]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
  role       = aws_iam_role.ec2.name
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  depends_on = [
    aws_iam_role.ec2
  ]
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.ec2.name
}

resource "aws_ssm_activation" "ec2" {
  depends_on = [
    aws_iam_role.ec2,
    aws_iam_role_policy_attachment.ecr_readonly,
    aws_iam_role_policy_attachment.ssm_ec2,
    aws_iam_role_policy_attachment.ssm_automation,
    aws_iam_role_policy_attachment.web_tier,
    aws_iam_role_policy_attachment.worker_tier
  ]
  name               = "${var.application_name}-ec2-activation"
  iam_role           = aws_iam_role.ec2.id
  registration_limit = 3
}

data "aws_iam_policy_document" "default" {
  statement {
    actions = [
      "elasticloadbalancing:DescribeInstanceHealth",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeTargetHealth",
      "ec2:DescribeInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:GetConsoleOutput",
      "ec2:AssociateAddress",
      "ec2:DescribeAddresses",
      "ec2:DescribeSecurityGroups",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeScalingActivities",
      "autoscaling:DescribeNotificationConfigurations",
    ]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    sid = "AllowOperations"
    actions = [
      "autoscaling:AttachInstances",
      "autoscaling:CreateAutoScalingGroup",
      "autoscaling:CreateLaunchConfiguration",
      "autoscaling:DeleteLaunchConfiguration",
      "autoscaling:DeleteAutoScalingGroup",
      "autoscaling:DeleteScheduledAction",
      "autoscaling:DescribeAccountLimits",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeLaunchConfigurations",
      "autoscaling:DescribeLoadBalancers",
      "autoscaling:DescribeNotificationConfigurations",
      "autoscaling:DescribeScalingActivities",
      "autoscaling:DescribeScheduledActions",
      "autoscaling:DetachInstances",
      "autoscaling:PutScheduledUpdateGroupAction",
      "autoscaling:ResumeProcesses",
      "autoscaling:SetDesiredCapacity",
      "autoscaling:SetInstanceProtection",
      "autoscaling:SuspendProcesses",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "autoscaling:UpdateAutoScalingGroup",
      "cloudwatch:PutMetricAlarm",
      "ec2:AssociateAddress",
      "ec2:AllocateAddress",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:DescribeAccountAttributes",
      "ec2:DescribeAddresses",
      "ec2:DescribeImages",
      "ec2:DescribeInstances",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSnapshots",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:DisassociateAddress",
      "ec2:ReleaseAddress",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:TerminateInstances",
      "ecs:CreateCluster",
      "ecs:DeleteCluster",
      "ecs:DescribeClusters",
      "ecs:RegisterTaskDefinition",
      "elasticbeanstalk:*",
      "elasticloadbalancing:ApplySecurityGroupsToLoadBalancer",
      "elasticloadbalancing:ConfigureHealthCheck",
      "elasticloadbalancing:CreateLoadBalancer",
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
      "elasticloadbalancing:DescribeInstanceHealth",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeTargetHealth",
      "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
      "elasticloadbalancing:DescribeTargetGroups",
      "elasticloadbalancing:RegisterTargets",
      "elasticloadbalancing:DeregisterTargets",
      "iam:ListRoles",
      "iam:PassRole",
      "logs:CreateLogGroup",
      "logs:PutRetentionPolicy",
      "rds:DescribeDBEngineVersions",
      "rds:DescribeDBInstances",
      "rds:DescribeOrderableDBInstanceOptions",
      "s3:GetObject",
      "s3:GetObjectAcl",
      "s3:ListBucket",
      "sns:CreateTopic",
      "sns:GetTopicAttributes",
      "sns:ListSubscriptionsByTopic",
      "sns:Subscribe",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "codebuild:CreateProject",
      "codebuild:DeleteProject",
      "codebuild:BatchGetBuilds",
      "codebuild:StartBuild",
    ]
    resources = ["*"]
    effect    = "Allow"
  }

  statement {
    sid = "AllowS3OperationsOnElasticBeanstalkBuckets"
    actions = [
      "s3:*"
    ]
    resources = [
      "arn:aws:s3:::*"
    ]
    effect = "Allow"
  }

  statement {
    sid = "AllowDeleteCloudwatchLogGroups"
    actions = [
      "logs:DeleteLogGroup"
    ]
    resources = [
      "arn:aws:logs:*:*:log-group:/aws/elasticbeanstalk*"
    ]
    effect = "Allow"
  }

  statement {
    sid = "AllowCloudformationOperationsOnElasticBeanstalkStacks"
    actions = [
      "cloudformation:*"
    ]
    resources = [
      "arn:aws:cloudformation:*:*:stack/awseb-*",
      "arn:aws:cloudformation:*:*:stack/eb-*"
    ]
    effect = "Allow"
  }
}

resource "aws_iam_role_policy" "default" {
  depends_on = [
    aws_iam_role.ec2
  ]
  name   = "${var.application_name}-eb-default"
  policy = data.aws_iam_policy_document.default.json
  role   = aws_iam_role.ec2.id
}

# Create elastic beanstalk Application
resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket
  tags   = local.tags
}

resource "aws_s3_object" "object" {
  bucket = aws_s3_bucket.bucket.id
  key    = "beanstalk/app.zip"
  source = "app.zip"
  tags   = local.tags
}

resource "aws_elastic_beanstalk_application" "application" {
  depends_on = [
    aws_vpc.vpc,
    aws_subnet.subnet,
    aws_ssm_activation.ec2
  ]
  name        = var.application_name
  description = var.application_description

  dynamic "appversion_lifecycle" {
    for_each = var.appversion_lifecycle_service_role_arn != "" ? ["true"] : []
    content {
      service_role          = var.appversion_lifecycle_service_role_arn
      max_count             = var.appversion_lifecycle_max_count
      delete_source_from_s3 = var.appversion_lifecycle_delete_source_from_s3
    }
  }
  tags = local.tags
}

resource "aws_elastic_beanstalk_application_version" "application_version" {
  depends_on = [
    aws_elastic_beanstalk_application.application
  ]
  name        = "${var.application_name}-base"
  application = var.application_name
  description = var.application_description
  bucket      = aws_s3_bucket.bucket.id
  key         = aws_s3_object.object.id
  tags        = local.tags
}

# Create elastic beanstalk Environment
resource "aws_elastic_beanstalk_environment" "environment" {
  depends_on = [
    aws_vpc.vpc,
    aws_subnet.subnet,
    aws_ssm_activation.ec2
  ]
  application            = aws_elastic_beanstalk_application.application.name
  description            = var.environment_description
  name                   = var.environment_name
  solution_stack_name    = var.environment_solution_stack_name
  tier                   = var.environment_tier
  wait_for_ready_timeout = var.environment_wait_for_ready_timeout
  version_label          = var.environment_version_label
  tags                   = local.tags

  # EC2
  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = aws_vpc.vpc.id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "AssociatePublicIpAddress"
    value     = var.associate_public_ip_address
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = aws_subnet.subnet.id
  }

  # Loadbalancer
  setting {
    namespace = "aws:elbv2:listener:default"
    name      = "ListenerEnabled"
    value     = var.default_listener_enabled
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "LoadBalancerType"
    value     = var.environment_loadbalancer_type
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBSubnets"
    value     = aws_subnet.subnet.id
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "Port"
    value     = var.environment_process_default_port
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "Protocol"
    value     = var.environment_loadbalancer_type == "network" ? "TCP" : "HTTP"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "ELBScheme"
    value     = var.environment_type == "LoadBalanced" ? var.elb_scheme : ""
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckInterval"
    value     = var.environment_process_default_healthcheck_interval
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthyThresholdCount"
    value     = var.environment_process_default_healthy_threshold_count
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "UnhealthyThresholdCount"
    value     = var.environment_process_default_unhealthy_threshold_count
  }

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "ServiceRole"
    value     = aws_iam_role.service.name
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.ec2_iam_instance_profile.name
  }

  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name      = "SystemType"
    value     = var.healthreporting_system_type
  }

  setting {
    namespace = "aws:ec2:instances"
    name      = "InstanceTypes"
    value     = var.instances_instance_types
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions"
    name      = "ManagedActionsEnabled"
    value     = var.managedactions_managed_actions_enabled ? "true" : "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions"
    name      = "PreferredStartTime"
    value     = var.managedactions_preferred_start_time
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions:platformupdate"
    name      = "UpdateLevel"
    value     = var.managedactions_platformupdate_update_level
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions:platformupdate"
    name      = "InstanceRefreshEnabled"
    value     = var.managedactions_platformupdate_instance_refresh_enabled
  }

  # Autoscaling
  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MinSize"
    value     = var.autoscaling_asg_minsize
  }
  setting {
    namespace = "aws:autoscaling:asg"
    name      = "MaxSize"
    value     = var.autoscaling_asg_maxsize
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "MeasureName"
    value     = var.autoscaling_trigger_measure_name
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "Statistic"
    value     = var.autoscaling_trigger_statistic
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "Unit"
    value     = var.autoscaling_trigger_unit
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "LowerThreshold"
    value     = var.autoscaling_trigger_lower_threshold
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "LowerBreachScaleIncrement"
    value     = var.autoscaling_trigger_lower_breach_scale_increment
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "UpperThreshold"
    value     = var.autoscaling_trigger_upper_threshold
  }

  setting {
    namespace = "aws:autoscaling:trigger"
    name      = "UpperBreachScaleIncrement"
    value     = var.autoscaling_trigger_upper_breach_scale_increment
  }

  # Logs
  setting {
    namespace = "aws:elasticbeanstalk:hostmanager"
    name      = "LogPublicationControl"
    value     = var.hostmanager_log_publication_control ? "true" : "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "StreamLogs"
    value     = var.cloudwatch_logs_stream_logs ? "true" : "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "DeleteOnTerminate"
    value     = var.cloudwatch_logs_delete_on_terminate ? "true" : "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name      = "RetentionInDays"
    value     = var.cloudwatch_logs_retention_in_days
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs:health"
    name      = "HealthStreamingEnabled"
    value     = var.cloudwatch_logs_health_health_streaming_enabled ? "true" : "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs:health"
    name      = "DeleteOnTerminate"
    value     = var.cloudwatch_logs_health_delete_on_terminate ? "true" : "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs:health"
    name      = "RetentionInDays"
    value     = var.cloudwatch_logs_health_retention_in_days
  }

  # Add additional Elastic Beanstalk settings
  dynamic "setting" {
    for_each = var.environment_variables
    content {
      namespace = "aws:elasticbeanstalk:application:environment"
      name      = setting.key
      value     = setting.value
    }
  }
}
