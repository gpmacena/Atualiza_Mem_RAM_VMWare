from pyVim import connect
from pyVmomi import vim
import ssl
import atexit
import time

# Configurações do vCenter
vcenter_host = 'endereço do vcenter'
vcenter_user = 'usuario'
vcenter_password = 'senha'
servers = [
    'nome do seu servidor no VMWare']

# Ignorar avisos de SSL
context = ssl._create_unverified_context()

try:
    # Conectar ao vCenter
    si = connect.SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)
    atexit.register(connect.Disconnect, si)
    
    print("Login no vCenter bem-sucedido.")

    # Listar todas as VMs
    def listar_vms():
        vms = []
        datacenters = si.content.rootFolder.childEntity
        for datacenter in datacenters:
            print(f"Datacenter: {datacenter.name}")
            vm_folder = datacenter.vmFolder
            for vm in vm_folder.childEntity:
                print(f" - Nome da VM: {vm.name}")
                vms.append(vm)
            
            for child in datacenter.hostFolder.childEntity:
                if hasattr(child, 'vm'):
                    for vm in child.vm:
                        print(f" - Nome da VM: {vm.name}")
                        vms.append(vm)
        return vms

    vms_list = listar_vms()

    print("Lista de VMs disponíveis:")
    for vm in vms_list:
        print(f"Nome da VM: {vm.name}")

    # Função para modificar a memória RAM de um servidor
    def alterar_memoria(vm_name):
        container_view = si.content.viewManager.CreateContainerView(si.content.rootFolder, [vim.VirtualMachine], True)
        
        vm = next((vm for vm in container_view.view if vm.name.lower() == vm_name.lower()), None)
        
        if not vm:
            print(f"Erro: VM {vm_name} não encontrada.")
            return

        print(f"Desligando {vm_name}...")
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            vm.PowerOff()
        
        while vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
            time.sleep(5)

        print(f"Alterando memória de {vm_name} para 10 GB...")
        config_spec = vim.vm.ConfigSpec()
        config_spec.memoryMB = 10240  # 10 GB
        task = vm.ReconfigVM_Task(config_spec)
        
        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(5)

        print(f"Iniciando {vm_name}...")
        vm.PowerOn()
        print(f"{vm_name} iniciado com sucesso.")

    # Loop pelos servidores
    for server in servers:
        alterar_memoria(server)

except vim.fault.InvalidLogin:
    print("Erro: Login inválido. Verifique suas credenciais.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
