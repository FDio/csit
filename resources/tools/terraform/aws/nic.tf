resource "aws_network_interface" "dut1_if2" {
  subnet_id = aws_subnet.c.id
  source_dest_check = false
  private_ip = var.dut1_if2_ip
  private_ips = [var.dut1_if2_ip]
  security_groups = [aws_security_group.CSIT.id]
  attachment {
    instance     = aws_instance.dut1.id
    device_index = 1
  }
  depends_on = [aws_vpc.CSIT]
}

data "aws_network_interface" "dut1_if2" {
  id = aws_network_interface.dut1_if2.id
}

resource "aws_network_interface" "dut1_if1" {
  subnet_id = aws_subnet.b.id
  source_dest_check = false
  private_ip = var.dut1_if1_ip
  private_ips = [var.dut1_if1_ip]
  security_groups = [aws_security_group.CSIT.id]
  attachment {
    instance     = aws_instance.dut1.id
    device_index = 2
  }
  depends_on = [aws_vpc.CSIT, aws_subnet.b]
}

data "aws_network_interface" "dut1_if1" {
  id = aws_network_interface.dut1_if1.id
}

resource "aws_network_interface" "dut2_if1" {
  subnet_id = aws_subnet.c.id
  source_dest_check = false
  private_ip = var.dut2_if1_ip
  private_ips = [var.dut2_if1_ip]
  security_groups = [aws_security_group.CSIT.id]
  attachment {
    instance     = aws_instance.dut2.id
    device_index = 1
  }
  depends_on = [aws_vpc.CSIT, aws_subnet.c]
}

data "aws_network_interface" "dut2_if1" {
  id = aws_network_interface.dut2_if1.id
}

resource "aws_network_interface" "dut2_if2" {
  subnet_id = aws_subnet.d.id
  source_dest_check = false
  private_ip = var.dut2_if2_ip
  private_ips = [var.dut2_if2_ip]
  security_groups = [aws_security_group.CSIT.id]
  attachment {
    instance     = aws_instance.dut2.id
    device_index = 2
  }
  depends_on = [aws_vpc.CSIT, aws_subnet.d]
}

data "aws_network_interface" "dut2_if2" {
  id = aws_network_interface.dut2_if2.id
}

resource "aws_network_interface" "tg_if1" {
  subnet_id = aws_subnet.b.id
  source_dest_check = false
  private_ip = var.tg_if1_ip
  private_ips = [var.tg_if1_ip]
  security_groups = [aws_security_group.CSIT.id]
  attachment {
    instance     = aws_instance.tg.id
    device_index = 1
  }
  depends_on = [aws_vpc.CSIT, aws_subnet.b]
}

data "aws_network_interface" "tg_if1" {
  id = aws_network_interface.tg_if1.id
}

resource "aws_network_interface" "tg_if2" {
  subnet_id = aws_subnet.d.id
  source_dest_check = false
  private_ip = var.tg_if2_ip
  private_ips = [var.tg_if2_ip]
  security_groups = [aws_security_group.CSIT.id]
  attachment {
    instance     = aws_instance.tg.id
    device_index = 2
  }
  depends_on = [aws_vpc.CSIT, aws_subnet.d]
}

data "aws_network_interface" "tg_if2" {
  id = aws_network_interface.tg_if2.id
}
