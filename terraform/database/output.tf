output "odin_sqlserver_name" {
  value = azurerm_mssql_server.odin_mssql_server.name
  sensitive = false
}

output "odin_sqldatabase_name" {
  value = var.purpose == "dev" ? azurerm_mssql_database.odin-mssql-database-dev.name[1] : azurerm_mssql_database.odin-mssql-database.name[1]
  sensitive = false
}