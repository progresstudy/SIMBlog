## glusterfs + openstack

### 1. 说明
1. cinder 通过rpc/local方法控制存储(lvm/glusterfs/ceph/emc/netapp etc.)，从存储中划分出一小块空间作为volume使用，并把相关信息存储到数据库中，比如 volume_type (iscsi, rbd, gluster etc.)，data (iscsi target, volume name, path etc.)
2. 当虚拟机使用volume作为启动盘启动或挂载volume时，nova会和cinder通信获得connection info, 一个json格式的volume信息。 nova会据此生成xml。注：不同的volume type，有不同的driver形成不同格式的xml。通过设置nova.conf中volume_drivers来配置volume_type和driver之间的关系。

#####nova cinder storage relation :

>img


### 2. 准备工作

#####1. 升级 qemu 和 libvirt
qemu1.3 之后支持原生的glusterfs存储接口。

libvirt 升级

    yum install libnl-devel libpciaccess-devel device-mapper-devel device-mapper-libs device-mapper-event-libs yajl yajl-devel libxml2-devel -y
    ./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc
    make 
    make install 
    ldconfig 


qemu升级：

    ./configure --prefix=/usr --enable-glusterfs --sysconfdir=/etc
    make
    make install
    
#####2. 更改libvirt配置

如果希望实现动态迁移，需要更改libvirt配置

更改/etc/libvirt/libvirtd.conf

	before : #listen_tls = 0
	after : listen_tls = 0
	before : #listen_tcp = 1
	after : listen_tcp = 1
	add: auth_tcp = "none"
 
更改/etc/init.d/libvirtd文件中：

	before : LIBVIRTD_ARGS=
	after : LIBVIRTD_ARGS=" -l"
	
#####3.配置glusterfs

在 `/etc/gluster/glusterd.vol` 中添加设置,并重启glusterd服务

	option rpc-auth-allow-insecure on
	
执行

	gluster volume set <volname> server.allow-insecure on
	gluster volume stop <volname>
	gluster volume start <volname>


### 3. 安装cinder，glance，nova
使用客制镜像安装

### 4. 配置
#####1.更改nova.conf文件

	add : qemu_allowed_storage_drivers = gluster
	remove : force_config_drive = always
	modify : vncserver_proxyclient_address = 0.0.0.0
    modify : vncserver_listen = 0.0.0.0
    
#####2. cinder配置

修改cinder.conf

	volume_driver = cinder.volume.drivers.glusterfs.GlusterfsDriver
	glusterfs_shares_config = /etc/cinder/shares.conf
	glusterfs_mount_point_base = /var/lib/cinder/volumes
新建shares.conf 
(注：hcg3/hcg4为glusterfs存储节点，h2312v3为glusterfs的volume name)

	hcg3:/h2312v3
	hcg4:/h2312v3

更改/etc/hosts，作hostname和ip的映射

#####附cinder.conf 和 nova.conf配置

nova.conf

    [DEFAULT]
    flat_interface = eth0
    flat_network_bridge = br100
    vlan_interface = eth0
    public_interface = br100
    network_manager = nova.network.manager.FlatDHCPManager
    glance_api_servers = 172.16.32.6:9292
    rabbit_password = 3O8XZDsdlnod
    rabbit_host = 172.16.32.6
    rpc_backend = nova.openstack.common.rpc.impl_kombu
    ec2_dmz_host = 172.16.32.6
    vncserver_proxyclient_address = 0.0.0.0
    vncserver_listen = 0.0.0.0
    vnc_enabled = true
    logging_context_format_string = %(asctime)s.%(msecs)03d %(levelname)s %(name)s [%(request_id)s %(user_name)s %(project_name)s] %(instance)s%(message)s
    instances_path = /nova/instances
    lock_path = /nova
    state_path = /nova
    enabled_apis = ec2,osapi_compute,metadata
    bindir = /usr/bin
    instance_name_template = instance%08x
    fatal_deprecations = True
    sql_connection = mysql://root:SxmbIMt8sxMh@127.0.0.1/nova?charset=utf8
    metadata_workers = 4
    ec2_workers = 4
    osapi_compute_workers = 4
    my_ip = 172.16.32.6
    osapi_compute_extension = nova.api.openstack.compute.contrib.standard_extensions
    s3_port = 3333
    s3_host = 172.16.32.6
    default_floating_pool = nova
    fixed_range = 
    force_dhcp_release = True
    dhcpbridge_flagfile = /etc/nova/nova.conf
    scheduler_driver = nova.scheduler.filter_scheduler.FilterScheduler
    rootwrap_config = /etc/nova/rootwrap.conf
    api_paste_config = /etc/nova/api-paste.ini
    allow_resize_to_same_host = True
    auth_strategy = keystone
    debug = True
    verbose = True
    qemu_allowed_storage_drivers = gluster
    
    [osapi_v3]
    enabled = True
    
    [keystone_authtoken]
    signing_dir = /var/cache/nova
    admin_password = 1xak8mlMsGDB
    admin_user = nova
    cafile = 
    admin_tenant_name = service
    auth_protocol = http
    auth_port = 35357
    auth_host = 172.16.32.6
    
    [spice]
    enabled = false
    
    
cinder.conf

    ####################
    # cinder.conf sample #
    ####################
    
    [DEFAULT]
    restore_discard_excess_bytes = true
    glance_api_version = 2
    volume_driver = cinder.volume.drivers.glusterfs.GlusterfsDriver
    rabbit_password = 3O8XZDsdlnod
    rabbit_host = 172.16.32.6
    rpc_backend = cinder.openstack.common.rpc.impl_kombu
    periodic_interval = 60
    lock_path = /cinder
    state_path = /cinder
    osapi_volume_extension = cinder.api.contrib.standard_extensions
    rootwrap_config = /etc/cinder/rootwrap.conf
    api_paste_config = /etc/cinder/api-paste.ini
    sql_connection = mysql://root:SxmbIMt8sxMh@172.16.32.6/cinder?charset=utf8
    iscsi_helper = tgtadm
    my_ip = 172.16.32.5
    volume_name_template = volume-%s
    volume_group = stack-volumes
    verbose = True
    debug = True
    auth_strategy = keystone
    glusterfs_shares_config = /etc/cinder/shares.conf
    glusterfs_mount_point_base = /var/lib/cinder/volumes
    # default glance hostname or ip (string value)
    glance_host=172.16.32.6
    
    ..... 未完


### 5. 使用

	nova volume-create --image-id <image_id> <size>
	nova boot boot-volume <volume-id> flavor <flaovr-id> <vm-name>
	nova live-migration <vm-name> <nodename>
	
###6. 其他
qemu直接启动:

	qemu-system-x86_64 --enable-kvm -m 1024 -drive file=gluster://hcg3/h2312v3/instances/cee24685-6cae-46ef-b2e0-df5a48c37a4a/disk -cdrom /var/lib/libvirt/images/custom3.iso -vnc :54
	
`virsh migrate`

	virsh migrate --live --p2p <domain> qemu+tcp://<descnode>/system

nova.conf中去掉`qemu_allowed_storage_drivers = gluster`配置，虚拟机所在节点会
把glusterfs挂到节点上，然后使用volume所在节点的路径，挂到虚拟机上，非 gluster://方式。


可以把glusterfs挂到节点上，虚拟机存储路径`instances_path = /nova/instances`指向共享存储,同样可以实现live migration. 此种情况下，需要更改/etc/libvirt/qemu.conf,设置
`dynamic_ownership = 0`,否则会出现镜像文件权限死锁问题。

FYI:

>> The problem is after I successful live migrate a domain, the domain
> os  become read-only.
> and when I use qemu-img to show the disk info at node which domain
> current running ,
> the command return 'Permission denied'. BUT, I can use qemu-img show
> the disk info at the previous node.

>If you are using glusterfs, libvirt doesn't recognize it as a 'shared'
filesystem, and therefore does a 'chown' back to root:root when stopping
the image on one host, which gets into a race with chowning to
lilbvirt:qemu on the other. If the image ends up being owned by 
root:root, then the guest no longer has access to the file system, and 
switches to read-only.




###7. 使用LVM Iscsi
cinder.conf

	[DEFAULT]
	glance_api_version = 2
	rabbit_password = 3O8XZDsdlnod
	rabbit_host = 10.0.0.200
	rpc_backend = cinder.openstack.common.rpc.impl_kombu
	periodic_interval = 60
	lock_path = /cinder
	state_path = /cinder
	osapi_volume_extension = cinder.api.contrib.standard_extensions
	rootwrap_config = /etc/cinder/rootwrap.conf
	api_paste_config = /etc/cinder/api-paste.ini
	sql_connection = mysql://root:SxmbIMt8sxMh@10.0.0.200/cinder?charset=utf8
	iscsi_helper = tgtadm
	my_ip = 10.0.0.21
	volume_name_template = volume-%s
    ## the vg name
	volume_group = stack-volumes
	verbose = True
	debug = True
	auth_strategy = keystone

修改`/etc/tgt/targets.conf` 和 `/etc/tgt/conf.d/cinder.conf` 并重启tgt

	add : include /etc/cinder/volumes/* 

