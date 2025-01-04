resource "azurerm_service_plan" "odin_service_plan" {
    name = var.purpose != "" ? "odin-${var.purpose}-service_plan" : "odin-service_plan"
    location = var.location
    resource_group_name = var.resource_group_name
    os_type = local.os_type
    sku_name = local.sku_name[var.purpose]

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

resource "azurerm_linux_web_app" "odin_backend_app" {
    name = var.purpose != "" ? "odin-${var.purpose}-portal-backend" : "odin-portal-backend"
    location = var.location
    resource_group_name = var.resource_group_name
    service_plan_id = azurerm_service_plan.odin_service_plan.id
    virtual_network_subnet_id = var.subnets.outbound_subnet_id
    https_only = true
    public_network_access_enabled = false
    app_settings = {
        "SCM_DO_BUILD_DURING_DEPLOYMENT": true,
        "minTlsVersion": "1.2",
        "DB_CONNECTION_STRING": "Driver={ODBC Driver 18 for SQL Server};Server=${var.odin_sqlserver_name}.database.windows.net;Database=${var.odin_sqldatabase_name};Authentication=SqlPassword;Encrypt=no;TrustServerCertificate=no;Connection Timeout=60;",
        "SQL_DB_UID": "pmt_db_service",
        "SQL_DB_PWD": "",
        "CPAM_API_URL": "https://se-qa-api.volvocars.biz/cpam/service/ProductDataGet",
        "CPAM_REFRESH_DATE": "mon-4",
        "CPAM_USER_KEY": "0ee7aafa944473221e76edd7f604290b"

    }

    site_config {
        vnet_route_all_enabled = true
        application_stack {
            python_version = "3.11"
        }
        app_command_line = "gunicorn --workers 2 --bind=0.0.0.0 --timeout 600 app:app --preload"
        always_on = false
    }

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

module "backend_networking" {
  source = "../networking"
  location = var.location
  private_service_connection_name = azurerm_linux_web_app.odin_backend_app.name
  private_service_connection_resource_id = azurerm_linux_web_app.odin_backend_app.id
  resource_group_name = var.resource_group_name
  subresource_name = "sites"
  subnet_id =  var.subnets.inbound_subnet_id
}

resource "azurerm_linux_web_app" "odin_frontend_app" {
    name = var.purpose != "prod" ? "odin-${var.purpose}-portal" : "odin-portal"
    location = var.location
    resource_group_name = var.resource_group_name
    service_plan_id = azurerm_service_plan.odin_service_plan.id
    virtual_network_subnet_id = var.subnets.outbound_subnet_id
    https_only = true
    public_network_access_enabled = false
    app_settings = {
        "SCM_DO_BUILD_DURING_DEPLOYMENT": true,
        "minTlsVersion": "1.2",
        "VUE_APP_CLIENT_ID": var.client_id,
        "VUE_APP_BACKEND_HOSTNAME": azurerm_linux_web_app.odin_backend_app.default_hostname
        "VUE_APP_ENV": upper(var.purpose)
    }

    site_config {
        vnet_route_all_enabled = true
        application_stack {
            node_version = "20-lts"
        }
        always_on = false
    }

    lifecycle {
      ignore_changes = [
        tags["AppID"],
        tags["EnvType"],
        tags["owner-appid"]
       ]
    }
}

module "frontend_networking" {
  source = "../networking"
  location = var.location
  private_service_connection_name = azurerm_linux_web_app.odin_frontend_app.name
  private_service_connection_resource_id = azurerm_linux_web_app.odin_frontend_app.id
  resource_group_name = var.resource_group_name
  subresource_name = "sites"
  subnet_id =  var.subnets.inbound_subnet_id
}