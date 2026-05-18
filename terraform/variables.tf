variable "aws_region" {
  description = "AWS region for deployment"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type (must be free tier eligible)"
  default     = "t2.micro" 
}

variable "key_name" {
  description = "Name of the SSH key pair in AWS to use for the instance"
  type        = string
}

variable "github_repo_url" {
  description = "URL of your GitHub repository"
  type        = string
  default     = "https://github.com/CaHHaL/ThreatShield-AI-Cloud-Native-Cyber-Defense-Monitoring-Platform.git"
}
