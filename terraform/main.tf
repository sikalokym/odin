data "azurerm_client_config" "current" {}

# data "azuread_users" "admin_users" { 
#   user_principal_names = [ "MKIS@volvocars.com", "OSCHOEN@volvocars.com" ]
# }

# resource "azuread_group" "cld-app-6255-corp-mssql-server-admin" {
#     display_name = "cld-app-6255-corp-mssql-server-admin-dev"
#     owners = data.azuread_users.admin_users.object_ids
#     security_enabled = true    
# }

resource "azurerm_resource_group" "rg_odin" {
    name = "rg-odin-${var.purpose}"
    location = var.location

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

resource "random_password" "password" {
    length = 12
    min_lower = 1
    min_special = 1
    min_upper = 1
    min_numeric = 1
}

resource "azurerm_key_vault" "key_vault" {
    name = "odin-${var.purpose}-key-vault"
    location = var.location
    resource_group_name = azurerm_resource_group.rg_odin.name
    tenant_id = data.azurerm_client_config.current.tenant_id
    sku_name = "standard"
    public_network_access_enabled = false
    access_policy = [ 
        {
          tenant_id = data.azurerm_client_config.current.tenant_id
          object_id = "0b059d05-0a48-4dfc-b07e-cf837d454163"
          secret_permissions = [
            "Get",
            "List",
            "Set",
            "Delete"
          ]
          application_id = ""
          certificate_permissions = []
          key_permissions = []
          storage_permissions = []
        },
        {
          tenant_id = data.azurerm_client_config.current.tenant_id
          object_id = "322c4686-ccac-40ad-85d2-9ba4a42a9485"
          application_id = ""
          secret_permissions = [
            "Get",
            "List",
            "Set",
            "Delete"
          ]
          certificate_permissions = []
          key_permissions = []
          storage_permissions = []
        }

    ]

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

module "key_vault_networking" {
  source = "./networking"
  location = var.location
  private_service_connection_name = azurerm_key_vault.key_vault.name
  private_service_connection_resource_id = azurerm_key_vault.key_vault.id
  resource_group_name = azurerm_resource_group.rg_odin.name
  subresource_name = "vault"
  subnet_id = data.azurerm_subnet.odin_subnet_inbound.id
}

# resource "azurerm_key_vault_secret" "db_secret" {
#     name = "db-secret"
#     value = random_password.password.result
#     key_vault_id = azurerm_key_vault.key_vault.id
# }

module "databases" {
  source = "./database"
  administrator_login_password = random_password.password.result
  env = var.env
  location = var.location
  purpose = var.purpose
  resource_group_name = azurerm_resource_group.rg_odin.name
  inbound_subnet_id = data.azurerm_subnet.odin_subnet_inbound.id
}

module "webapps" {
  source = "./webapps"
  client_id = var.client_id
  env = var.env
  location = var.location
  purpose = var.purpose
  resource_group_name = azurerm_resource_group.rg_odin.name
  subnets = {
    inbound_subnet_id = data.azurerm_subnet.odin_subnet_inbound.id
    outbound_subnet_id = data.azurerm_subnet.odin_subnet_outbound.id
  }
  odin_sqlserver_name = module.databases.odin_sqlserver_name
  odin_sqldatabase_name = module.databases.odin_sqldatabase_name
  depends_on = [ module.databases ]
}
