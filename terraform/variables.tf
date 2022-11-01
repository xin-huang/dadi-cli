
variable "AWS" {
  type = object({
    instance_type = string,
    region        = string,
    public_key    = string
  })
}

variable "dadi_cli" {
  type = object({
    run        = bool,
    parameters = string,
    fs_file    = string
  })
}

variable "workqueue_factory" {
  type = object({
    run = bool
  })
}

variable "project_name" {
  type = string
}

variable "workqueue_password" {
  type = string
}
