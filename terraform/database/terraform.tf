terraform { 
  required_providers {
    mssql = {
      source = "betr-io/mssql"
      version = "0.3.1"
    }
  }
}
provider "mssql" {
  debug = true
}