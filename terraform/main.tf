terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}


provider "azurerm" {
  features {}
  resource_provider_registrations = "none"
}


# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# Azure SQL Server
resource "azurerm_mssql_server" "main" {
  name                         = "sql-currency-anomaly"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

# Azure SQL Database
resource "azurerm_mssql_database" "main" {
  name      = "currency-rates-db"
  server_id = azurerm_mssql_server.main.id
  sku_name  = "Basic"
}

# SQL Firewall rule - allow Azure services
resource "azurerm_mssql_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# SQL Firewall rule - allow your local IP
resource "azurerm_mssql_firewall_rule" "allow_local" {
  name             = "AllowLocalAccess"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

# Azure Container Registry
resource "azurerm_container_registry" "main" {
  name                = "acrcurrencyanomaly"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

