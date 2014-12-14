Title: The second article
Date: 2012-12-01 10:02

![Ceph](http://ceph.com/docs/master/_static/logo.png)

*文档中所有操作都基于CentOS-6.4-x86_64-minimal.iso环境下*

## Install(准备工作)

![](http://ceph.com/docs/master/_images/ditaa-ab0a88be6a09668151342b36da8ceabaf0528f79.png)

说明：Admin node 作为管理ceph集群（部署，维护）,
ceph-node1 ceph-node2 ceph-node3作为ceph集群使用

**1. 给各个ceph-node添加一个用户**

	ssh user@ceph-server
	sudo useradd -d /home/ceph -m ceph
	sudo passwd ceph

**2. 在ceph-node上ceph用户，添加root权限**

	echo "ceph ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph
	sudo chmod 0440 /etc/sudoers.d/ceph

**3. 在admin node上生成ssh-key**

	ssh-keygen

**4. 拷贝公钥到各个节点，建立信任**

	ssh-copy-id ceph@ceph-server

**5. 修改~/.ssh/config，建立简便ssh连接**

	Host ceph-node-1
		Hostname ceph-node-1.fqdn-or-ip-address.com
		User ceph

    Host ceph-node-2
  		Hostname ceph-node-2.fqdn-or-ip-address.com
        User Ceph

    Host ceph-node-3
  		Hostname ceph-node-3.fqdn-or-ip-address.com
        User Ceph

**6. 修改/etc/hosts, 使admin node可以通过主机名访问ceph node**

**7. 添加ceph  yum源**
注：{ceph-stable-release}替换为：ceph版本，比如emperor，
{distro}根据不同os替换， centos6为：el6

	sudo vim /etc/yum.repos.d/ceph.repo

	[ceph-noarch]
	name=Ceph noarch packages
	baseurl=http://ceph.com/rpm-{ceph-stable-release}/{distro}/noarch
	enabled=1
	gpgcheck=1
	type=rpm-md
	gpgkey=https://ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc


**8. 关闭所有ceph-node放火墙**

	sudo /etc/init.d/iptables stop

## Install(Storage Cluster)
![](http://ceph.com/docs/master/_images/ditaa-4f2f6a2d2959888b2a0b5e3f277a4c7da7c7e089.png)

注意：
> *Important Do not call ceph-deploy with sudo or run it as root if you are logged in as a different user, because it will not issue sudo commands needed on the remote host.*

**1. 建立工作目录**

	mkdir my-cluster
	cd my-cluster

**2. 安装集群**

	ceph-deploy new ceph-node1

说明: ceph-deploy new 用来初始化一些配置，并指定一个monitor host


如果出现以下错误，更改各个节点/etc/sudoers, 注释掉`Defaults requiretty`

	sudo: sorry, you must have a tty to run sudo

安装ceph
	
	ceph-deploy install ceph-node1 ceph-node2 ceph-node3
	# 安装monitor server
	ceph-deploy mon create ceph-node1
	# 获取keyring
	ceph-deploy gatherkeys ceph-node1

到节点ceph-node2, ceph-node3上，创建目录，作为数据存储(OSD)，
注：也可以直接使用分区，参考：[http://ceph.com/docs/master/rados/deployment/ceph-deploy-osd](http://ceph.com/docs/master/rados/deployment/ceph-deploy-osd "ceph-deploy osd")

	ssh ceph-node2
	sudo mkdir /tmp/osd0
	exit

	ssh ceph-node3
	sudo mkdir /tmp/osd1
	exit

在admin node上执行：

	ceph-deploy osd prepare ceph-node2:/tmp/osd0 ceph-node3:/tmp/osd1
	ceph-deploy osd activate ceph-node2:/tmp/osd0 ceph-node3:/tmp/osd1


**扩展：**

1. `ceph-deploy osd prepare osdserver1:sdb:/dev/ssd1`,以分区作为osd数据存储
2. `ceph-deploy osd create osdserver1:sdb:/dev/ssd1`，`prepare`和`activate`的合并命令
3. `ceph-deploy disk zap osdserver1:sdb`,删除节点磁盘分区


如果出现以下异常，确认monitor server的6789端口是否被防火墙屏蔽。

	[ceph-2][WARNIN] 2014-01-06 13:48:18.215285 7fb28abfd700  0 -- :/1021341 >> 172.16.15.21:6789/0 pipe(0x7fb28c024480 sd=4 :0 s=1 pgs=0 cs=0 l=1 c=0x7fb28c0246e0).fault

如果出现以下异常，命令中加入参数`-c config-file -k keyringfile`

	[ceph@david-centos ~]$ ceph health detail
	Traceback (most recent call last):
  	File "/usr/bin/ceph", line 774, in <module>
    	sys.exit(main())
 	 File "/usr/bin/ceph", line 559, in main
    	conf_defaults=conf_defaults, conffile=conffile)
 	 File "/usr/lib/python2.6/site-packages/rados.py", line 221, in __init__
    	self.conf_read_file(conffile)
 	 File "/usr/lib/python2.6/site-packages/rados.py", line 272, in conf_read_file
    	raise make_ex(ret, "error calling conf_read_file")
	rados.Error: error calling conf_read_file: errno EACCES


查看集群状态：
	
	ceph health
如果结果：`HEALTH_OK` 表示一切正常，如果出现：

	HEALTH_WARN 91 pgs degraded; 192 pgs stuck unclean

查看osd数据节点状态：，如果出现状态为`down`情况，查看节点日志。

	[ceph@david-centos ~]$ ceph -c ceph.conf osd tree
	# id	weight	type name	up/down	reweight
	-1	0.03998	root default
	-2	0.01999		host ops-h-01
	0	0.009995			osd.0	up	1	
	1	0.009995			osd.1	up	1	
	-3	0.009995		host ceph-2
	2	0.009995			osd.2	up	1	
	-4	0.009995		host ceph-3
	3	0.009995			osd.3	up	1

其他osd trouble shoting: [http://ceph.com/docs/master/rados/troubleshooting/troubleshooting-osd/](http://ceph.com/docs/master/rados/troubleshooting/troubleshooting-osd/)


添加一个monitor

	ceph-mon -i ceph-2 --pid-file /var/run/ceph/mon.ceph-2.pid -c /etc/ceph/ceph.conf --public-addr 172.16.15.22

上传一个文件到cluster storage

	# 上传
	rados put {object-name} {file-path} --pool=data
	rados put test-object-1 testfile.txt --pool=data
    # 列出data pool的所有文件
	rados -p data ls
    # 显示某个文件的位置
	ceph osd map {pool-name} {object-name}
	ceph osd map data test-object-1
    # 删除
	rados rm test-object-1 --pool=data

如出现如下报错, 是由于rados无法读/etc/ceph/ceph.conf文件，使用sudo

	[ceph@david-centos ~]$ rados rm test-object-1 --pool=data
	global_init: error reading config file.


## Install (Block Device + kvm + libvirt)

![](http://ceph.com/docs/master/_images/ditaa-bf701cb7a7ba894563b2d023c926977af6f88187.png)

**1. 配置源**

添加新的repo文件ceph-qemu.repo

	[ceph-extras]
	name=Ceph Extra Packages and Backports $basearch
	baseurl=http://ceph.com/packages/ceph-extras/rpm/centos6/$basearch
	enabled=1
	priority=2
	gpgcheck=1
	type=rpm-md
	gpgkey=https://ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc
	[ceph-extras-noarch]
	name=Ceph Extra Packages and Backports noarch
	baseurl=http://ceph.com/packages/ceph-extras/rpm/centos6/noarch
	enabled=1
	priority=2
	gpgcheck=1
	type=rpm-md
	gpgkey=https://ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc
	[ceph-extras-source]
	name=Ceph Extra Packages and Backports Sources
	baseurl=http://ceph.com/packages/ceph-extras/rpm/centos6/SRPMS
	enabled=1
	priority=2
	gpgcheck=1
	type=rpm-md
	gpgkey=https://ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc

**2. 安装yum-plugin-priorities**

	sudo yum install yum-plugin-priorities

确认 /etc/yum/pluginconf.d/priorities.conf配置如下：

	[main]
	enabled = 1
执行`yum clean all`


**3. 安装libvirt和kvm**

	sudo yum install qemu-kvm qemu-kvm-tools qemu-img
	sudo yum install qemu-guest-agent qemu-guest-agent-win32

**4. 安装ceph并配置管理员**

在admin node上，执行
	
	ceph-deploy install {qemu-hostname}
	ceph-deploy admin {qemu-hostname}


**5. 安装libvirt 和 virt-install**

	yum install libvirt virt-install
	/etc/init.d/libvirtd restart

**6. 配置ceph user**

创建pool：
	
	ceph osd pool create libvirt-pool 128 128

创建user 注：client.libvirt 表示为 TYPE.USER_ID

	ceph auth get-or-create client.libvirt mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=libvirt-pool'

创建rbd磁盘镜像：

	qemu-img create -f rbd rbd:libvirt-pool/new-libvirt-image 2G

**7. 配置用户认证**

在qemu节点上：

	cat > secret.xml <<EOF
		<secret ephemeral='no' private='no'>
        	<usage type='ceph'>
                <name>client.libvirt secret</name>
        	</usage>
		</secret>
	EOF

define 配置：

	virsh secret-define --file secret.xml

设置keyring：注：client.libvirt.key可以通过 `ceph auth get client.libvirt` 得到key值

	virsh secret-set-value --secret {uuid of secret} --base64 $client.libvirt.key && rm client.libvirt.key secret.xml
	
**８. 使用virt-install创建虚拟机**

**９. 挂载rbd磁盘**

使用`virsh edit domid`来更改配置：

    <disk type='network' device='disk'>
      <driver name='qemu'/>
      <auth username='libvirt'>
        <secret type='ceph' uuid='9fc17a20-12de-7820-a6d7-911cdbb727b9'/>
      </auth>
      <source protocol='rbd' name='libvirt-pool/new-libvirt-image'>
        <host name='172.16.15.21' port='6789'/>
      </source>
      <target dev='hdb' bus='ide'/>
      <alias name='ide0-0-1'/>
      <address type='drive' controller='0' bus='0' target='0' unit='1'/>
    </disk>
    <disk type='network' device='disk'>
      <driver name='qemu'/>
      <auth username='libvirt'>
        <secret type='ceph' uuid='9fc17a20-12de-7820-a6d7-911cdbb727b9'/>
      </auth>
      <source protocol='rbd' name='libvirt-pool/test1'>
        <host name='172.16.15.22' port='6789'/>
      </source>
      <target dev='hdc' bus='ide'/>
      <alias name='ide0-1-0'/>
      <address type='drive' controller='0' bus='1' target='0' unit='0'/>
    </disk>
