# Get latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group
resource "aws_security_group" "threatshield_sg" {
  name        = "threatshield_sg"
  description = "Security group for ThreatShield AI platform"

  # Admin SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Admin SSH"
  }

  # Cowrie SSH Honeypot
  ingress {
    from_port   = 2222
    to_port     = 2222
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Cowrie SSH Honeypot"
  }

  # Cowrie Telnet Honeypot
  ingress {
    from_port   = 2323
    to_port     = 2323
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Cowrie Telnet Honeypot"
  }

  # Fake Web Login Honeypot
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Fake Web Login Honeypot"
  }

  # FastAPI Backend
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "FastAPI Backend"
  }

  # Grafana Dashboard
  ingress {
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Grafana SOC Dashboard"
  }

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ThreatShield-SG"
  }
}

# EC2 Instance
resource "aws_instance" "threatshield_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.threatshield_sg.id]

  # 30GB is the maximum for Free Tier
  root_block_device {
    volume_size = 20 
    volume_type = "gp3"
  }

  user_data = templatefile("${path.module}/userdata.sh", {
    github_repo = var.github_repo_url
  })

  tags = {
    Name = "ThreatShield-Backend"
  }
}
