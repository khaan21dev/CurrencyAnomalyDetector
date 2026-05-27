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

variable "logic_app_url" {
  description = "Logic App HTTP trigger URL"
  sensitive   = true
}
