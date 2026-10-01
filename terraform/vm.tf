data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2404-lts"
}

resource "yandex_compute_instance" "leadflow" {
  name        = "leadflow"
  platform_id = "standard-v3"

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 15
      type     = "network-hdd"
    }
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.leadflow.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.leadflow.id]
  }

  metadata = {
    user-data = templatefile("${path.module}/cloud-init.yaml", {
      user    = var.vm_user
      ssh_key = trimspace(file(pathexpand(var.ssh_public_key_path)))
    })
  }
}
