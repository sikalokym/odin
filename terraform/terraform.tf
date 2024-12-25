# $env:TF_CLOUD_PROJECT = "Odin"
# $env:TF_CLOUD_ORGANIZATION = "Sikalokym"
# $env:TF_WORKSPACE = "development"

terraform { 
  cloud { 
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.10.0"
    }
    azuread = {
      source = "hashicorp/azuread"
      version = "3.0.2"
    }
  }
}