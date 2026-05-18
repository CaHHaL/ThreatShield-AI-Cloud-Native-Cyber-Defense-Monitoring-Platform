output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.threatshield_server.public_ip
}

output "grafana_url" {
  description = "URL to access Grafana"
  value       = "http://${aws_instance.threatshield_server.public_ip}:3001"
}

output "api_url" {
  description = "URL for the backend API (use this in Vercel)"
  value       = "http://${aws_instance.threatshield_server.public_ip}:8000"
}

output "websocket_url" {
  description = "WebSocket URL (use this in Vercel)"
  value       = "ws://${aws_instance.threatshield_server.public_ip}:8000"
}
