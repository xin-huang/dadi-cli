
variable "AWS" {
  type = object({
    instance_type = string,
    region        = string,
    public_key    = string
  })
}

variable "dadi_cli" {
  type = object({
    run           = bool,
    use_workqueue = bool,
    parameters    = string,
  })
}

variable "cuda" {
  type = object({
    gpus = string
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
