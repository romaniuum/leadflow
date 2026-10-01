resource "yandex_vpc_network" "leadflow" {
  name = "leadflow"
}

resource "yandex_vpc_subnet" "leadflow" {
  name           = "leadflow-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.leadflow.id
  v4_cidr_blocks = ["10.10.0.0/24"]
}

resource "yandex_vpc_security_group" "leadflow" {
  name       = "leadflow-sg"
  network_id = yandex_vpc_network.leadflow.id

  ingress {
    description    = "SSH"
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = var.ssh_allowed_cidrs
  }

  ingress {
    description    = "App"
    protocol       = "TCP"
    port           = 8000
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description    = "Grafana"
    protocol       = "TCP"
    port           = 3000
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description    = "Any outgoing traffic, needed for apt and docker pull"
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}
