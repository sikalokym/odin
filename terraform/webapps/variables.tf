variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "purpose" {
    description = "Purpose of use of the env: prod, dev, test, learn"
    type = string
    default = "dev"
    validation {
      condition = contains(["dev", "prod", "test", "learn"], var.purpose)
      error_message = "error purpose"
    }
}

variable "env" {
    description = "Prod or Dev environment"
    type = string
    default = "dev"
    validation {
      condition = contains(["dev", "prod"], var.env)
      error_message = "error env"
    }
}

variable "client_id" {
  type = string
}

variable "subnets" {
  type = object({
    inbound_subnet_id = string
    outbound_subnet_id = string
  })
}

variable "odin_sqlserver_name" {
  type = string
}

variable "odin_sqldatabase_name" {
  type = string
}