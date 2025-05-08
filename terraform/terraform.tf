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
    mssql = {
      source = "betr-io/mssql"
      version = "0.3.1"
    }
  }
}