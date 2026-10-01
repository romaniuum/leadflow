output "public_ip" {
  value = yandex_compute_instance.leadflow.network_interface[0].nat_ip_address
}

output "ssh" {
  value = "ssh ${var.vm_user}@${yandex_compute_instance.leadflow.network_interface[0].nat_ip_address}"
}
