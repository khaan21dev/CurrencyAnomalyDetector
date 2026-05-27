variable "resource_group_name" {
  default = "RG-CurrencyAnomalyDetector"
}

variable "location" {
  default = "northeurope"
}

variable "sql_admin_username" {
  default = "sqladmin"
}

variable "sql_admin_password" {
  description = "Azure SQL admin password"
  sensitive   = true
}
