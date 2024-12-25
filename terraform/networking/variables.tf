variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
  default = "West Europe"
}

variable "subresource_name" {
  type = string
}

variable "private_service_connection_name" {
  type = string
}

variable "private_service_connection_resource_id" {
  type = string
}

variable "subnet_id" {
  type = string
}