variable "name" {
  type        = string
  description = "Name of the role"
}

variable "policy" {
  type        = string
  description = "Policy of the role"
}

variable "role_sid" {
  type        = string
  description = "Role sid of the role"
  default     = ""
}
