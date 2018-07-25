#
# This is a WLST script to create and configure an OSB cluster.
#

print '[INFO] Setting parameters..'
machines='place-holder-for-managed-servers'
server_groups=['OSB-MGD-SVRS-COMBINED']
data_source_driver='oracle.jdbc.OracleDriver'
data_source_test='SQL SELECT 1 FROM DUAL'

domain_application_home = os.getenv('DOMAIN_APPLICATION_HOME')
domain_configuration_home = os.getenv('DOMAIN_CONFIGURATION_HOME')
fusion_middleware_home = os.getenv('FUSION_MIDDLEWARE_HOME')
middleware_home = os.getenv('MIDDLEWARE_HOME')
nodemanager_home = os.getenv('NODE_MANAGER_HOME')
weblogic_home = os.getenv('WEBLOGIC_HOME')

weblogic_template = middleware_home + '/wlserver/common/templates/wls/wls.jar'

print "[INFO] Create domain '%s' " % domain_name
readTemplate(weblogic_template)
setOption('AppDir', domain_application_home)
setOption('DomainName', domain_name)
setOption('OverwriteDomain', 'true')
setOption('ServerStartMode', 'prod')
setOption('NodeManagerType', 'CustomLocationNodeManager')
setOption('NodeManagerHome', nodemanager_home)
cd('/Security/base_domain/User/weblogic')
cmo.setName(admin_username)
cmo.setUserPassword(admin_password)
cd('/')

print '[INFO] Save domain'
writeDomain(domain_configuration_home)
closeTemplate()

print '[INFO] Read domain'
readDomain(domain_configuration_home)

#delete('osb_server1', 'Server')

print '[INFO] Create OSB cluster'
cluster = create(cluster_name,'Cluster')
cluster.setClusterMessagingMode('unicast')

print '[INFO] Creating machines and servers..'
for i in range(len(machines)):
    print "[INFO] Creating machine_%s" % repr(i)
    machine = create(machines.keys()[i],'UnixMachine')
    #machine.setPostBindUIDEnabled(java.lang.Boolean('true'))
    #machine.setPostBindUID(oracle_user_name)
    #machine.setPostBindGIDEnabled(java.lang.Boolean('true'))
    #machine.setPostBindGID(oracle_group_name)
    cd('/Machine/' + machine.getName())
    nodemanager = create(machine.getName(),'NodeManager')
    nodemanager.setListenAddress(machines.values()[i])
    nodemanager.setListenPort(int(nodemanager_listen_port))
    nodemanager.setNMType(nodemanager_connection_mode)
    cd('/')
    for j in range(int(managed_servers_per_machine)):
        managed_server_listen_port = int(managed_server_listen_port_start) + j
        #hName = machines.keys()[i].split('.')[0]
        mserver_name=managed_server_name
        if int(managed_servers_per_machine) > 1:
            mserver_name = managed_server_name+'_' + repr(j+1)
        print "[INFO] [%s] Creating server.." % mserver_name
        server = create(mserver_name,'Server')
        server.setListenPort(managed_server_listen_port)
        server.setListenAddress(managed_server_listen_address)
        server.setCluster(cluster)
        server.setMachine(machine)
        cd('Servers/' + mserver_name)
        print "[INFO] [%s] Configure overload protection"
        overload_protection = create(mserver_name,'OverloadProtection')
        overload_protection.setFailureAction('force-shutdown')
        overload_protection.setPanicAction('system-exit')
        cd('OverloadProtection/' + mserver_name)
        create(mserver_name,'ServerFailureTrigger')
        cd('../..')
        overload_protection.getServerFailureTrigger().setMaxStuckThreadTime(600)
        overload_protection.getServerFailureTrigger().setStuckThreadCount(0)
        print "[INFO] [%s] Configure logging" % mserver_name
        server_log = create(mserver_name,'Log')
        server_log.setRotationType('bySize')
        server_log.setFileMinSize(5000)
        server_log.setNumberOfFilesLimited(java.lang.Boolean('true'))
        server_log.setFileCount(10)
        server_log.setLogFileSeverity('Info')
        server_log.setStdoutSeverity('Error')
        server_log.setDomainLogBroadcastSeverity('Error')
        web_server = create(mserver_name,'WebServer')
        cd('WebServer/' + mserver_name)
        create(mserver_name,'WebServerLog')
        cd('../..')
        web_server.getWebServerLog().setLoggingEnabled(java.lang.Boolean('false'))
        web_server.getWebServerLog().setRotationType('bySize')
        web_server.getWebServerLog().setFileMinSize(5000)
        web_server.getWebServerLog().setNumberOfFilesLimited(java.lang.Boolean('true'))
        web_server.getWebServerLog().setFileCount(10)
        cd('../..')
        print "[INFO] [%s] Set server group" % mserver_name
        #setServerGroups(mserver_name, server_groups)
        print "[INFO] [%s] Assign server to cluster '%s'" % (mserver_name, cluster_name)
        assign('Server', mserver_name, 'Cluster', cluster_name)
        cd('/')

print "[INFO] Retarget JMS resources.."
filestores = cmo.getFileStores()
for filestore in filestores:
    filestore.setDirectory(domain_application_home)
    targets = filestore.getTargets()
    for target in targets:
        if ' (migratable)' in target.getName():
            assign('FileStore', filestore.getName(), 'Target', target.getName().strip('(migratable)').strip())
jmsservers = cmo.getJMSServers()
for jmsserver in jmsservers:
    targets = jmsserver.getTargets()
    for target in targets:
        if ' (migratable)' in target.getName():
            assign('JMSServer', jmsserver.getName(), 'Target', target.getName().strip('(migratable)').strip())
safagents = cmo.getSAFAgents()
for safagent in safagents:
    targets = safagent.getTargets()
    for target in targets:
        if ' (migratable)' in target.getName():
            assign('SAFAgent', safagent.getName(), 'Target', target.getName().strip('(migratable)').strip())

print '[INFO] Adjust data source settings..'
jdbcsystemresources = cmo.getJDBCSystemResources()
for jdbcsystemresource in jdbcsystemresources:
    cd ('/JDBCSystemResource/' + jdbcsystemresource.getName() + '/JdbcResource/' \
        + jdbcsystemresource.getName() + '/JDBCConnectionPoolParams/NO_NAME_0')
    cmo.setInitialCapacity(1)
    cmo.setMaxCapacity(15)
    cmo.setMinCapacity(1)
    cmo.setStatementCacheSize(0)
    cmo.setTestConnectionsOnReserve(java.lang.Boolean('false'))
    cmo.setTestTableName(data_source_test)
    cmo.setConnectionCreationRetryFrequencySeconds(30)
    cd ('/JDBCSystemResource/' + jdbcsystemresource.getName() + '/JdbcResource/' \
        + jdbcsystemresource.getName() + '/JDBCDriverParams/NO_NAME_0')
    print 'DB URL: '+data_source_url
    print 'DB Schema Prefix: ' +data_source_user_prefix
    cmo.setUrl(data_source_url)
    cmo.setPasswordEncrypted(data_source_password)
    cd ('/JDBCSystemResource/' + jdbcsystemresource.getName() + '/JdbcResource/' \
        + jdbcsystemresource.getName() + '/JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0/Property/user')
    cmo.setValue(cmo.getValue().replace('DEV', data_source_user_prefix))
    cd('/')

print '[INFO] Set NodeManager credentials'
cd('/SecurityConfiguration/' + domain_name)
cmo.setNodeManagerUsername(nodemanager_username)
cmo.setNodeManagerPasswordEncrypted(nodemanager_password)

print '[INFO] Configuring AdminServer..'
cd('/Server/' + admin_server_name)
cmo.setListenAddress(admin_server_listen_address)
cmo.setListenPort(int(admin_server_listen_port))
create(admin_server_name,'SSL')
cd('SSL/' + admin_server_name)
cmo.setHostnameVerificationIgnored(true)
cmo.setHostnameVerifier(None)
cmo.setTwoWaySSLEnabled(false)
cmo.setClientCertificateEnforced(false)

print '[INFO] Set up authentication configuration'
cd('/SecurityConfiguration/'+ domain_name +'/Realms/myrealm')
cd('AuthenticationProviders/DefaultAuthenticator')
set('ControlFlag', 'SUFFICIENT')
cd('../../')

print '[INFO] Save changes'
updateDomain()
closeDomain()
