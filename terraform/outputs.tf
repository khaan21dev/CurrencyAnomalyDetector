output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "sql_server_name" {
  value = azurerm_mssql_server.main.name
}


output "sql_connection_string" {
  value     = "Server=${azurerm_mssql_server.main.fully_qualified_domain_name};Database=currency-rates-db;User=${var.sql_admin_username};Password=${var.sql_admin_password}"
  sensitive = true
}


output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "acr_admin_username" {
  value     = azurerm_container_registry.main.admin_username
  sensitive = true
}

output "acr_admin_password" {
  value     = azurerm_container_registry.main.admin_password
  sensitive = true
}
