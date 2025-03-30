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
      version = "3.2.0"
    }
  }
}