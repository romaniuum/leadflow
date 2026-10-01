variable "cloud_id" {
  type = string
}

variable "folder_id" {
  type = string
}

variable "zone" {
  type    = string
  default = "ru-central1-a"
}

variable "service_account_key_file" {
  description = "Path to the authorized key of the service account used by Terraform"
  type        = string
  default     = "key.json"
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/id_ed25519.pub"
}

variable "vm_user" {
  type    = string
  default = "deploy"
}

variable "ssh_allowed_cidrs" {
  description = "Who can connect over SSH, better to set your own IP like 1.2.3.4/32"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
