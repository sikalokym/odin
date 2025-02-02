resource "azurerm_mssql_server" "odin_mssql_server" {
    name = var.purpose != "" ? "odin-${var.purpose}-mssql-server" : "odin-mssql-server"
    resource_group_name = var.resource_group_name
    location = var.location
    version = "12.0"
    administrator_login = local.administrator_login
    administrator_login_password = var.administrator_login_password
    minimum_tls_version = "1.2"
    public_network_access_enabled = false
    azuread_administrator {
      login_username = "Kis, Mykola"
      object_id = "322c4686-ccac-40ad-85d2-9ba4a42a9485"
    }

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

module "sql_server_networking" {
  source = "../networking"
  location = var.location
  private_service_connection_name = azurerm_mssql_server.odin_mssql_server.name
  private_service_connection_resource_id = azurerm_mssql_server.odin_mssql_server.id
  resource_group_name = var.resource_group_name
  subresource_name = "sqlServer"
  subnet_id = var.inbound_subnet_id
}

resource "azurerm_mssql_database" "odin-mssql-database" {
    count = var.purpose != "dev" ? 1 : 0
    name = "odin-${var.purpose}-mssql-database"
    server_id = azurerm_mssql_server.odin_mssql_server.id
    collation = "SQL_Latin1_General_CP1_CI_AS"
    min_capacity = 0.5
    storage_account_type = "Local"
    auto_pause_delay_in_minutes = var.purpose == "prod" ? -1 : 60
    max_size_gb = local.max_size_gb[var.purpose]
    sku_name = local.sku_name[var.purpose]
    depends_on = [
        azurerm_mssql_server.odin_mssql_server
    ]

    lifecycle {
      prevent_destroy = true
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

resource "azurerm_mssql_database" "odin-mssql-database-dev" {
    count = var.purpose == "dev" ? 1 : 0
    name = "odin-${var.purpose}-mssql-database"
    server_id = azurerm_mssql_server.odin_mssql_server.id
    collation = "SQL_Latin1_General_CP1_CI_AS"
    storage_account_type = "Local"
    max_size_gb = local.max_size_gb[var.purpose]
    sku_name = local.sku_name[var.purpose]
    depends_on = [
        azurerm_mssql_server.odin_mssql_server
    ]

    lifecycle {
      prevent_destroy = true
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}