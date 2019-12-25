import virtualbox


class _Machine:
    def __init__(self, vbox, vm_name):
        self.vbox = vbox
        self.vm_name = vm_name
        self.session = virtualbox.Session()
        vm = self.vbox.find_machine(self.vm_name)
        vm.launch_vm_process(self.session, 'gui', '')

    def stop(self):
        self.session.console.power_down()


class VBoxControl:
    def __init__(self):
        self.vbox = virtualbox.VirtualBox()
        self.vbox_list = [vm.name for vm in self.vbox.machines]
        self.vbox_machines = []
        print('VBOX List', self.vbox_list)

    def start_machine(self):
        pass


if __name__ == '__main__':
    vc = VBoxControl()