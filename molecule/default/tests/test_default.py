"""Role testing files using testinfra."""


def test_hosts_file(host):
    """Validate /etc/hosts file."""
    etc_hosts = host.file("/etc/hosts")
    assert etc_hosts.exists
    assert etc_hosts.user == "root"
    assert etc_hosts.group == "root"

def test_nomad_template_config(host):
    """Validate /etc/consul-template.d/nomad/ files."""
    etc_nomad_template_d_nomad_config_hcl = host.file("/etc/consul-template.d/nomad/nomad_config.hcl")
    assert etc_nomad_template_d_nomad_config_hcl.exists
    assert etc_nomad_template_d_nomad_config_hcl.user == "nomad"
    assert etc_nomad_template_d_nomad_config_hcl.group == "nomad"
    assert etc_nomad_template_d_nomad_config_hcl.mode == 0o600

def test_template_files(host):
    """Validate /etc/consul-template.d/nomad/templates/ files."""
    nomad_ca_pem_tpl = host.file("/etc/consul-template.d/nomad/templates/nomad_ca.pem.tpl")
    nomad_cert_pem_tpl = host.file("/etc/consul-template.d/nomad/templates/nomad_cert.pem.tpl")
    nomad_key_pem_tpl = host.file("/etc/consul-template.d/nomad/templates/nomad_key.pem.tpl")
    for file in nomad_cert_pem_tpl, nomad_key_pem_tpl:
        assert file.exists
        assert file.user == "nomad"
        assert file.group == "nomad"
        assert file.mode == 0o600
    assert nomad_ca_pem_tpl.content_string == '{{ with secret "pki/issue/your-issuer" "common_name=nomad01.example.com" "ttl=90d" "alt_names=localhost" "ip_sans=127.0.0.1" }}\n{{ .Data.issuing_ca }}\n{{ end }}\n'
    assert nomad_cert_pem_tpl.content_string == '{{ with secret "pki/issue/your-issuer" "common_name=nomad01.example.com" "ttl=90d" "alt_names=localhost" "ip_sans=127.0.0.1" }}\n{{ .Data.certificate }}\n{{ .Data.issuing_ca }}\n{{ end }}\n'
    assert nomad_key_pem_tpl.content_string == '{{ with secret "pki/issue/your-issuer" "common_name=nomad01.example.com" "ttl=90d" "alt_names=localhost" "ip_sans=127.0.0.1" }}\n{{ .Data.private_key }}\n{{ end }}\n'

def test_nomad_certs_service_file(host):
    """Validate nomad-certs service file."""
    etc_systemd_system_nomad_certs_service = host.file("/etc/systemd/system/nomad-certs.service")
    assert etc_systemd_system_nomad_certs_service.exists
    assert etc_systemd_system_nomad_certs_service.user == "root"
    assert etc_systemd_system_nomad_certs_service.group == "root"
    assert etc_systemd_system_nomad_certs_service.mode == 0o644
    assert etc_systemd_system_nomad_certs_service.content_string != ""

def test_nomad_certs_service(host):
    """Validate nomad-certs service."""
    nomad_certs_service = host.service("nomad-certs.service")
    assert nomad_certs_service.is_enabled
    assert not nomad_certs_service.is_running
    assert nomad_certs_service.systemd_properties["Restart"] == "on-failure"
    assert nomad_certs_service.systemd_properties["User"] == "nomad"
    assert nomad_certs_service.systemd_properties["Group"] == "nomad"
    assert nomad_certs_service.systemd_properties["FragmentPath"] == "/etc/systemd/system/nomad-certs.service"
