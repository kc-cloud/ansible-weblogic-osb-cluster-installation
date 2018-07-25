#
# This is a WLST script to create and configure an OSB cluster.
#
import sys
import os
import traceback

print '[INFO] Setting parameters..'
machines='PLACE-HOLDER'
server_groups=['OSB-MGD-SVRS-COMBINED']
admin_server_url = 't3://' + admin_server_listen_address + ':' + admin_server_listen_port
print '[INFO] Connecting to admin server: %s' % admin_server_url
if admin_server_listen_address not in machines.keys():
    connect(admin_username, admin_password, admin_server_url)
    templatePath = '/tmp/myTemplate.jar'
    try:
        os.remove(templatePath)
    except OSError:
        pass
    writeTemplate(templatePath)
    disconnect()
    selectCustomTemplate(templatePath)
    loadTemplates()
    domainPath = os.getenv('DOMAIN_CONFIGURATION_HOME')
    setOption('OverwriteDomain', 'true')
    writeDomain(domainPath)

connect(admin_username, admin_password, admin_server_url)
print cmo
edit()
startEdit()

try:
    cluster = cmo.lookupCluster(cluster_name)

    print '[INFO] Creating machines and servers..'
    for i in range(len(machines)):
        print "[INFO] Creating machine_%s" % repr(i)
        machine = cmo.lookupMachine(machines.keys()[i])
        if machine is None:
            machine = create(machines.keys()[i],'UnixMachine')
        else:
            print 'Machine already available'
        #machine.setPostBindUIDEnabled(java.lang.Boolean('true'))
        #machine.setPostBindUID(oracle_user_name)
        #machine.setPostBindGIDEnabled(java.lang.Boolean('true'))
        #machine.setPostBindGID(oracle_group_name)
        machine.getNodeManager().setListenAddress(machines.values()[i])
        machine.getNodeManager().setListenPort(int(nodemanager_listen_port))
        machine.getNodeManager().setNMType(nodemanager_connection_mode)
        for j in range(int(managed_servers_per_machine)):
            managed_server_listen_port = int(managed_server_listen_port_start) + j
            #hName = machines.keys()[i].split('.')[0]
            mserver_name = managed_server_name
            if int(managed_servers_per_machine) > 1:
                mserver_name = mserver_name+'_' + repr(j+1)
            print "[INFO] [%s] Creating server.." % mserver_name
            server = cmo.lookupMachine(mserver_name)
            if server is None:
                server = create(mserver_name,'Server')
            server.setListenPort(managed_server_listen_port)
            server.setListenAddress(managed_server_listen_address)
            server.setCluster(cluster)
            server.setMachine(machine)
            print "[INFO] [%s] Configure overload protection"
            #overload_protection = create(mserver_name,'OverloadProtection')
            overload_protection = server.getOverloadProtection()
            overload_protection.setFailureAction('force-shutdown')
            overload_protection.setPanicAction('system-exit')
            #create(mserver_name,'ServerFailureTrigger')
            overload_protection.createServerFailureTrigger()
            overload_protection.getServerFailureTrigger().setMaxStuckThreadTime(600)
            overload_protection.getServerFailureTrigger().setStuckThreadCount(0)
            print "[INFO] [%s] Configure logging" % mserver_name
            #server_log = create(mserver_name,'Log')
            server_log = server.getLog()
            server_log.setRotationType('bySize')
            server_log.setFileMinSize(5000)
            server_log.setNumberOfFilesLimited(java.lang.Boolean('true'))
            server_log.setFileCount(10)
            server_log.setLogFileSeverity('Info')
            server_log.setStdoutSeverity('Error')
            server_log.setDomainLogBroadcastSeverity('Error')
            #web_server = create(mserver_name,'WebServer')
            web_server = server.getWebServer()
            #create(mserver_name,'WebServerLog')
            web_server.getWebServerLog().setLoggingEnabled(java.lang.Boolean('false'))
            web_server.getWebServerLog().setRotationType('bySize')
            web_server.getWebServerLog().setFileMinSize(5000)
            web_server.getWebServerLog().setNumberOfFilesLimited(java.lang.Boolean('true'))
            web_server.getWebServerLog().setFileCount(10)
            print "[INFO] [%s] Set server group" % mserver_name
            #setServerGroups(mserver_name, server_groups)
            print "[INFO] [%s] Assign server to cluster '%s'" % (mserver_name, cluster_name)
            assign('Server', mserver_name, 'Cluster', cluster_name)

    save()
    activate(block='true')
    disconnect()
except:
    traceback.print_exc()
    print "Unexpected error:", sys.exc_info()[0]
    print 'Error occured ... canceling edit'
    cancelEdit('y')

 
