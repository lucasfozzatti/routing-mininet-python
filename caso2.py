#!/usr/bin/env python

import cmd
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from subprocess import call


class Topology():

    def __init__(self):
        self.routers = []
        self.hosts = []
        self.switches = []
        self.net = Mininet( topo=None,
                    build=False,
                    ipBase='10.0.0.0/8',)
        self.r1 = '' 
        self.suc = 0   
        self.host = 0       
  
    def generate_topology(self):    
        n = 2
        r = 6
        nhost=1
        suc = 1
        self.suc = int(input("Ingrese la cantidad de sucursales: "))
        self.host = int(input("Ingrese la cantidad de Hosts por sucursal: ")) 
        for i in range(self.suc):
            
            s_input = 's' + str(n)
            globals()[s_input] = self.net.addSwitch('s'+ str(n),cls=OVSKernelSwitch, failMode='standalone')
            self.switches.append(globals()[s_input])
            
            if n == 2:
                self.r1 = self.net.addHost('r1', cls=Node, ip='0.0.0.0')
                self.r1.cmd('sysctl -w net.ipv4.ip_forward=1')
            
            self.net.addLink(self.r1,globals()[s_input])
            n+=1

            r_input = 'r' + str(n)
            globals()[r_input] = self.net.addHost('r'+ str(n), cls=Node, ip='192.168.100.'+ str(r) +'/29')
            globals()[r_input].cmd('sysctl -w net.ipv4.ip_forward=1')
            self.net.addLink(globals()[s_input],globals()[r_input])
            self.routers.append(globals()[r_input])
            n+=1
            
            sn_input = 's' + str(n)
            globals()[sn_input] = self.net.addSwitch('s'+ str(n),cls=OVSKernelSwitch, failMode='standalone')
            self.net.addLink(globals()[r_input], globals()[sn_input])
            self.switches.append(globals()[sn_input])
            r += 8
            n += 1
            h=254
            for i in range(self.host):
                user_input = 'h' + str(nhost)
                globals()[user_input] = self.net.addHost('h'+ str(nhost), cls=Host, ip='10.0.'+ str(suc) +'.'+ str(h) +'/24')
                self.net.addLink(globals()[sn_input],globals()[user_input])
                self.hosts.append(globals()[user_input] )
                h -= 1
                nhost += 1
            suc += 1        
        
    def start(self):

        info( '*** Starting network\n')
        self.net.build()
        info( '*** Starting controllers\n')
        for controller in self.net.controllers:
            controller.start()

        info( '*** Starting switches\n')
        for i in self.switches:
            
            self.net.get(str(i)).start([])
        info( '*** Post configure switches and hosts\n')

        n = 0
        p = 6
        t = 1
        
        for i, j in enumerate(self.routers):
           
            j.cmd('ip add add 10.0.{}.1/24 dev {}-eth1 brd +'.format(i+1, j))
            j.cmd('ip route add 192.168.100.0/24 via 192.168.100.{}'.format(t))
            j.cmd('ip route add 10.0.0.0/21 via 192.168.100.{}'.format(t))
            
            self.r1.cmd('ip add add 192.168.100.{}/29 dev r1-eth{} brd +'.format(t,i))
            self.r1.cmd('ip route add 10.0.{}.0/24 via 192.168.100.{}'.format(i+1,p))
        
            p+=8
            t += 8
            
        s = 1
        red = 0
        h = self.host
        for i, j in enumerate(self.hosts):
            
            p=str(j)[1]
            j.cmd('ip route add 192.168.100.0/24 via 10.0.{}.1'.format(s))
            j.cmd('ip route add 10.0.0.0/21 via 10.0.{}.1'.format(s))
            
            if  len(str(j))== 3:
                
                p = str(j)[1] + str(j)[2]
               
            if int(p) == self.host:
                
                red += 8
                s+=1
                self.host += h
                

        CLI(self.net)
        self.net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main = Topology()
    main.generate_topology()
    main.start()


