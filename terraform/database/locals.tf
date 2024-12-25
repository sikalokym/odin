locals {
    administrator_login = "odin_sqlserver_admin"
    max_size_gb = {
        dev = 10
        test = 32
        prod = 32
    }  
    sku_name = {
        dev = "S0"
        test = "GP_S_Gen5_1"
        prod = "GP_S_Gen5_1"
    }
}