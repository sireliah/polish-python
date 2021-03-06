AdminExecuteSequence = [
('InstallInitialize', Nic, 1500),
('InstallFinalize', Nic, 6600),
('InstallFiles', Nic, 4000),
('InstallAdminPackage', Nic, 3900),
('FileCost', Nic, 900),
('CostInitialize', Nic, 800),
('CostFinalize', Nic, 1000),
('InstallValidate', Nic, 1400),
]

AdminUISequence = [
('FileCost', Nic, 900),
('CostInitialize', Nic, 800),
('CostFinalize', Nic, 1000),
('ExecuteAction', Nic, 1300),
('ExitDialog', Nic, -1),
('FatalError', Nic, -3),
('UserExit', Nic, -2),
]

AdvtExecuteSequence = [
('InstallInitialize', Nic, 1500),
('InstallFinalize', Nic, 6600),
('CostInitialize', Nic, 800),
('CostFinalize', Nic, 1000),
('InstallValidate', Nic, 1400),
('CreateShortcuts', Nic, 4500),
('MsiPublishAssemblies', Nic, 6250),
('PublishComponents', Nic, 6200),
('PublishFeatures', Nic, 6300),
('PublishProduct', Nic, 6400),
('RegisterClassInfo', Nic, 4600),
('RegisterExtensionInfo', Nic, 4700),
('RegisterMIMEInfo', Nic, 4900),
('RegisterProgIdInfo', Nic, 4800),
]

InstallExecuteSequence = [
('InstallInitialize', Nic, 1500),
('InstallFinalize', Nic, 6600),
('InstallFiles', Nic, 4000),
('FileCost', Nic, 900),
('CostInitialize', Nic, 800),
('CostFinalize', Nic, 1000),
('InstallValidate', Nic, 1400),
('CreateShortcuts', Nic, 4500),
('MsiPublishAssemblies', Nic, 6250),
('PublishComponents', Nic, 6200),
('PublishFeatures', Nic, 6300),
('PublishProduct', Nic, 6400),
('RegisterClassInfo', Nic, 4600),
('RegisterExtensionInfo', Nic, 4700),
('RegisterMIMEInfo', Nic, 4900),
('RegisterProgIdInfo', Nic, 4800),
('AllocateRegistrySpace', 'NOT Installed', 1550),
('AppSearch', Nic, 400),
('BindImage', Nic, 4300),
('CCPSearch', 'NOT Installed', 500),
('CreateFolders', Nic, 3700),
('DeleteServices', 'VersionNT', 2000),
('DuplicateFiles', Nic, 4210),
('FindRelatedProducts', Nic, 200),
('InstallODBC', Nic, 5400),
('InstallServices', 'VersionNT', 5800),
('IsolateComponents', Nic, 950),
('LaunchConditions', Nic, 100),
('MigrateFeatureStates', Nic, 1200),
('MoveFiles', Nic, 3800),
('PatchFiles', Nic, 4090),
('ProcessComponents', Nic, 1600),
('RegisterComPlus', Nic, 5700),
('RegisterFonts', Nic, 5300),
('RegisterProduct', Nic, 6100),
('RegisterTypeLibraries', Nic, 5500),
('RegisterUser', Nic, 6000),
('RemoveDuplicateFiles', Nic, 3400),
('RemoveEnvironmentStrings', Nic, 3300),
('RemoveExistingProducts', Nic, 6700),
('RemoveFiles', Nic, 3500),
('RemoveFolders', Nic, 3600),
('RemoveIniValues', Nic, 3100),
('RemoveODBC', Nic, 2400),
('RemoveRegistryValues', Nic, 2600),
('RemoveShortcuts', Nic, 3200),
('RMCCPSearch', 'NOT Installed', 600),
('SelfRegModules', Nic, 5600),
('SelfUnregModules', Nic, 2200),
('SetODBCFolders', Nic, 1100),
('StartServices', 'VersionNT', 5900),
('StopServices', 'VersionNT', 1900),
('MsiUnpublishAssemblies', Nic, 1750),
('UnpublishComponents', Nic, 1700),
('UnpublishFeatures', Nic, 1800),
('UnregisterClassInfo', Nic, 2700),
('UnregisterComPlus', Nic, 2100),
('UnregisterExtensionInfo', Nic, 2800),
('UnregisterFonts', Nic, 2500),
('UnregisterMIMEInfo', Nic, 3000),
('UnregisterProgIdInfo', Nic, 2900),
('UnregisterTypeLibraries', Nic, 2300),
('ValidateProductID', Nic, 700),
('WriteEnvironmentStrings', Nic, 5200),
('WriteIniValues', Nic, 5100),
('WriteRegistryValues', Nic, 5000),
]

InstallUISequence = [
('FileCost', Nic, 900),
('CostInitialize', Nic, 800),
('CostFinalize', Nic, 1000),
('ExecuteAction', Nic, 1300),
('ExitDialog', Nic, -1),
('FatalError', Nic, -3),
('UserExit', Nic, -2),
('AppSearch', Nic, 400),
('CCPSearch', 'NOT Installed', 500),
('FindRelatedProducts', Nic, 200),
('IsolateComponents', Nic, 950),
('LaunchConditions', Nic, 100),
('MigrateFeatureStates', Nic, 1200),
('RMCCPSearch', 'NOT Installed', 600),
('ValidateProductID', Nic, 700),
]

tables=['AdminExecuteSequence', 'AdminUISequence', 'AdvtExecuteSequence', 'InstallExecuteSequence', 'InstallUISequence']
