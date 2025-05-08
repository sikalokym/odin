output "odin_sqlserver_name" {
  value = azurerm_mssql_server.odin_mssql_server.name
  sensitive = false
}

output "odin_sqldatabase_name" {
  value = one(concat(azurerm_mssql_database.odin-mssql-database-dev[*].name, azurerm_mssql_database.odin-mssql-database[*].name))
  sensitive = false
}

output "odin_sqldatabase_resource_id" {
  value = one(concat(azurerm_mssql_database.odin-mssql-database-dev[*].id, azurerm_mssql_database.odin-mssql-database[*].id))
}