z . zaimportuj Table

_Validation = Table('_Validation')
_Validation.add_field(1,'Table',11552)
_Validation.add_field(2,'Column',11552)
_Validation.add_field(3,'Nullable',3332)
_Validation.add_field(4,'MinValue',4356)
_Validation.add_field(5,'MaxValue',4356)
_Validation.add_field(6,'KeyTable',7679)
_Validation.add_field(7,'KeyColumn',5378)
_Validation.add_field(8,'Category',7456)
_Validation.add_field(9,'Set',7679)
_Validation.add_field(10,'Description',7679)

ActionText = Table('ActionText')
ActionText.add_field(1,'Action',11592)
ActionText.add_field(2,'Description',7936)
ActionText.add_field(3,'Template',7936)

AdminExecuteSequence = Table('AdminExecuteSequence')
AdminExecuteSequence.add_field(1,'Action',11592)
AdminExecuteSequence.add_field(2,'Condition',7679)
AdminExecuteSequence.add_field(3,'Sequence',5378)

Condition = Table('Condition')
Condition.add_field(1,'Feature_',11558)
Condition.add_field(2,'Level',9474)
Condition.add_field(3,'Condition',7679)

AdminUISequence = Table('AdminUISequence')
AdminUISequence.add_field(1,'Action',11592)
AdminUISequence.add_field(2,'Condition',7679)
AdminUISequence.add_field(3,'Sequence',5378)

AdvtExecuteSequence = Table('AdvtExecuteSequence')
AdvtExecuteSequence.add_field(1,'Action',11592)
AdvtExecuteSequence.add_field(2,'Condition',7679)
AdvtExecuteSequence.add_field(3,'Sequence',5378)

AdvtUISequence = Table('AdvtUISequence')
AdvtUISequence.add_field(1,'Action',11592)
AdvtUISequence.add_field(2,'Condition',7679)
AdvtUISequence.add_field(3,'Sequence',5378)

AppId = Table('AppId')
AppId.add_field(1,'AppId',11558)
AppId.add_field(2,'RemoteServerName',7679)
AppId.add_field(3,'LocalService',7679)
AppId.add_field(4,'ServiceParameters',7679)
AppId.add_field(5,'DllSurrogate',7679)
AppId.add_field(6,'ActivateAtStorage',5378)
AppId.add_field(7,'RunAsInteractiveUser',5378)

AppSearch = Table('AppSearch')
AppSearch.add_field(1,'Property',11592)
AppSearch.add_field(2,'Signature_',11592)

Property = Table('Property')
Property.add_field(1,'Property',11592)
Property.add_field(2,'Value',3840)

BBControl = Table('BBControl')
BBControl.add_field(1,'Billboard_',11570)
BBControl.add_field(2,'BBControl',11570)
BBControl.add_field(3,'Type',3378)
BBControl.add_field(4,'X',1282)
BBControl.add_field(5,'Y',1282)
BBControl.add_field(6,'Width',1282)
BBControl.add_field(7,'Height',1282)
BBControl.add_field(8,'Attributes',4356)
BBControl.add_field(9,'Text',7986)

Billboard = Table('Billboard')
Billboard.add_field(1,'Billboard',11570)
Billboard.add_field(2,'Feature_',3366)
Billboard.add_field(3,'Action',7474)
Billboard.add_field(4,'Ordering',5378)

Feature = Table('Feature')
Feature.add_field(1,'Feature',11558)
Feature.add_field(2,'Feature_Parent',7462)
Feature.add_field(3,'Title',8000)
Feature.add_field(4,'Description',8191)
Feature.add_field(5,'Display',5378)
Feature.add_field(6,'Level',1282)
Feature.add_field(7,'Directory_',7496)
Feature.add_field(8,'Attributes',1282)

Binary = Table('Binary')
Binary.add_field(1,'Name',11592)
Binary.add_field(2,'Data',2304)

BindImage = Table('BindImage')
BindImage.add_field(1,'File_',11592)
BindImage.add_field(2,'Path',7679)

File = Table('File')
File.add_field(1,'File',11592)
File.add_field(2,'Component_',3400)
File.add_field(3,'FileName',4095)
File.add_field(4,'FileSize',260)
File.add_field(5,'Version',7496)
File.add_field(6,'Language',7444)
File.add_field(7,'Attributes',5378)
File.add_field(8,'Sequence',1282)

CCPSearch = Table('CCPSearch')
CCPSearch.add_field(1,'Signature_',11592)

CheckBox = Table('CheckBox')
CheckBox.add_field(1,'Property',11592)
CheckBox.add_field(2,'Value',7488)

Class = Table('Class')
Class.add_field(1,'CLSID',11558)
Class.add_field(2,'Context',11552)
Class.add_field(3,'Component_',11592)
Class.add_field(4,'ProgId_Default',7679)
Class.add_field(5,'Description',8191)
Class.add_field(6,'AppId_',7462)
Class.add_field(7,'FileTypeMask',7679)
Class.add_field(8,'Icon_',7496)
Class.add_field(9,'IconIndex',5378)
Class.add_field(10,'DefInprocHandler',7456)
Class.add_field(11,'Argument',7679)
Class.add_field(12,'Feature_',3366)
Class.add_field(13,'Attributes',5378)

Component = Table('Component')
Component.add_field(1,'Component',11592)
Component.add_field(2,'ComponentId',7462)
Component.add_field(3,'Directory_',3400)
Component.add_field(4,'Attributes',1282)
Component.add_field(5,'Condition',7679)
Component.add_field(6,'KeyPath',7496)

Icon = Table('Icon')
Icon.add_field(1,'Name',11592)
Icon.add_field(2,'Data',2304)

ProgId = Table('ProgId')
ProgId.add_field(1,'ProgId',11775)
ProgId.add_field(2,'ProgId_Parent',7679)
ProgId.add_field(3,'Class_',7462)
ProgId.add_field(4,'Description',8191)
ProgId.add_field(5,'Icon_',7496)
ProgId.add_field(6,'IconIndex',5378)

ComboBox = Table('ComboBox')
ComboBox.add_field(1,'Property',11592)
ComboBox.add_field(2,'Order',9474)
ComboBox.add_field(3,'Value',3392)
ComboBox.add_field(4,'Text',8000)

CompLocator = Table('CompLocator')
CompLocator.add_field(1,'Signature_',11592)
CompLocator.add_field(2,'ComponentId',3366)
CompLocator.add_field(3,'Type',5378)

Complus = Table('Complus')
Complus.add_field(1,'Component_',11592)
Complus.add_field(2,'ExpType',13570)

Directory = Table('Directory')
Directory.add_field(1,'Directory',11592)
Directory.add_field(2,'Directory_Parent',7496)
Directory.add_field(3,'DefaultDir',4095)

Control = Table('Control')
Control.add_field(1,'Dialog_',11592)
Control.add_field(2,'Control',11570)
Control.add_field(3,'Type',3348)
Control.add_field(4,'X',1282)
Control.add_field(5,'Y',1282)
Control.add_field(6,'Width',1282)
Control.add_field(7,'Height',1282)
Control.add_field(8,'Attributes',4356)
Control.add_field(9,'Property',7474)
Control.add_field(10,'Text',7936)
Control.add_field(11,'Control_Next',7474)
Control.add_field(12,'Help',7986)

Dialog = Table('Dialog')
Dialog.add_field(1,'Dialog',11592)
Dialog.add_field(2,'HCentering',1282)
Dialog.add_field(3,'VCentering',1282)
Dialog.add_field(4,'Width',1282)
Dialog.add_field(5,'Height',1282)
Dialog.add_field(6,'Attributes',4356)
Dialog.add_field(7,'Title',8064)
Dialog.add_field(8,'Control_First',3378)
Dialog.add_field(9,'Control_Default',7474)
Dialog.add_field(10,'Control_Cancel',7474)

ControlCondition = Table('ControlCondition')
ControlCondition.add_field(1,'Dialog_',11592)
ControlCondition.add_field(2,'Control_',11570)
ControlCondition.add_field(3,'Action',11570)
ControlCondition.add_field(4,'Condition',11775)

ControlEvent = Table('ControlEvent')
ControlEvent.add_field(1,'Dialog_',11592)
ControlEvent.add_field(2,'Control_',11570)
ControlEvent.add_field(3,'Event',11570)
ControlEvent.add_field(4,'Argument',11775)
ControlEvent.add_field(5,'Condition',15871)
ControlEvent.add_field(6,'Ordering',5378)

CreateFolder = Table('CreateFolder')
CreateFolder.add_field(1,'Directory_',11592)
CreateFolder.add_field(2,'Component_',11592)

CustomAction = Table('CustomAction')
CustomAction.add_field(1,'Action',11592)
CustomAction.add_field(2,'Type',1282)
CustomAction.add_field(3,'Source',7496)
CustomAction.add_field(4,'Target',7679)

DrLocator = Table('DrLocator')
DrLocator.add_field(1,'Signature_',11592)
DrLocator.add_field(2,'Parent',15688)
DrLocator.add_field(3,'Path',15871)
DrLocator.add_field(4,'Depth',5378)

DuplicateFile = Table('DuplicateFile')
DuplicateFile.add_field(1,'FileKey',11592)
DuplicateFile.add_field(2,'Component_',3400)
DuplicateFile.add_field(3,'File_',3400)
DuplicateFile.add_field(4,'DestName',8191)
DuplicateFile.add_field(5,'DestFolder',7496)

Environment = Table('Environment')
Environment.add_field(1,'Environment',11592)
Environment.add_field(2,'Name',4095)
Environment.add_field(3,'Value',8191)
Environment.add_field(4,'Component_',3400)

Error = Table('Error')
Error.add_field(1,'Error',9474)
Error.add_field(2,'Message',7936)

EventMapping = Table('EventMapping')
EventMapping.add_field(1,'Dialog_',11592)
EventMapping.add_field(2,'Control_',11570)
EventMapping.add_field(3,'Event',11570)
EventMapping.add_field(4,'Attribute',3378)

Extension = Table('Extension')
Extension.add_field(1,'Extension',11775)
Extension.add_field(2,'Component_',11592)
Extension.add_field(3,'ProgId_',7679)
Extension.add_field(4,'MIME_',7488)
Extension.add_field(5,'Feature_',3366)

MIME = Table('MIME')
MIME.add_field(1,'ContentType',11584)
MIME.add_field(2,'Extension_',3583)
MIME.add_field(3,'CLSID',7462)

FeatureComponents = Table('FeatureComponents')
FeatureComponents.add_field(1,'Feature_',11558)
FeatureComponents.add_field(2,'Component_',11592)

FileSFPCatalog = Table('FileSFPCatalog')
FileSFPCatalog.add_field(1,'File_',11592)
FileSFPCatalog.add_field(2,'SFPCatalog_',11775)

SFPCatalog = Table('SFPCatalog')
SFPCatalog.add_field(1,'SFPCatalog',11775)
SFPCatalog.add_field(2,'Catalog',2304)
SFPCatalog.add_field(3,'Dependency',7424)

Font = Table('Font')
Font.add_field(1,'File_',11592)
Font.add_field(2,'FontTitle',7552)

IniFile = Table('IniFile')
IniFile.add_field(1,'IniFile',11592)
IniFile.add_field(2,'FileName',4095)
IniFile.add_field(3,'DirProperty',7496)
IniFile.add_field(4,'Section',3936)
IniFile.add_field(5,'Key',3968)
IniFile.add_field(6,'Value',4095)
IniFile.add_field(7,'Action',1282)
IniFile.add_field(8,'Component_',3400)

IniLocator = Table('IniLocator')
IniLocator.add_field(1,'Signature_',11592)
IniLocator.add_field(2,'FileName',3583)
IniLocator.add_field(3,'Section',3424)
IniLocator.add_field(4,'Key',3456)
IniLocator.add_field(5,'Field',5378)
IniLocator.add_field(6,'Type',5378)

InstallExecuteSequence = Table('InstallExecuteSequence')
InstallExecuteSequence.add_field(1,'Action',11592)
InstallExecuteSequence.add_field(2,'Condition',7679)
InstallExecuteSequence.add_field(3,'Sequence',5378)

InstallUISequence = Table('InstallUISequence')
InstallUISequence.add_field(1,'Action',11592)
InstallUISequence.add_field(2,'Condition',7679)
InstallUISequence.add_field(3,'Sequence',5378)

IsolatedComponent = Table('IsolatedComponent')
IsolatedComponent.add_field(1,'Component_Shared',11592)
IsolatedComponent.add_field(2,'Component_Application',11592)

LaunchCondition = Table('LaunchCondition')
LaunchCondition.add_field(1,'Condition',11775)
LaunchCondition.add_field(2,'Description',4095)

ListBox = Table('ListBox')
ListBox.add_field(1,'Property',11592)
ListBox.add_field(2,'Order',9474)
ListBox.add_field(3,'Value',3392)
ListBox.add_field(4,'Text',8000)

ListView = Table('ListView')
ListView.add_field(1,'Property',11592)
ListView.add_field(2,'Order',9474)
ListView.add_field(3,'Value',3392)
ListView.add_field(4,'Text',8000)
ListView.add_field(5,'Binary_',7496)

LockPermissions = Table('LockPermissions')
LockPermissions.add_field(1,'LockObject',11592)
LockPermissions.add_field(2,'Table',11552)
LockPermissions.add_field(3,'Domain',15871)
LockPermissions.add_field(4,'User',11775)
LockPermissions.add_field(5,'Permission',4356)

Media = Table('Media')
Media.add_field(1,'DiskId',9474)
Media.add_field(2,'LastSequence',1282)
Media.add_field(3,'DiskPrompt',8000)
Media.add_field(4,'Cabinet',7679)
Media.add_field(5,'VolumeLabel',7456)
Media.add_field(6,'Source',7496)

MoveFile = Table('MoveFile')
MoveFile.add_field(1,'FileKey',11592)
MoveFile.add_field(2,'Component_',3400)
MoveFile.add_field(3,'SourceName',8191)
MoveFile.add_field(4,'DestName',8191)
MoveFile.add_field(5,'SourceFolder',7496)
MoveFile.add_field(6,'DestFolder',3400)
MoveFile.add_field(7,'Options',1282)

MsiAssembly = Table('MsiAssembly')
MsiAssembly.add_field(1,'Component_',11592)
MsiAssembly.add_field(2,'Feature_',3366)
MsiAssembly.add_field(3,'File_Manifest',7496)
MsiAssembly.add_field(4,'File_Application',7496)
MsiAssembly.add_field(5,'Attributes',5378)

MsiAssemblyName = Table('MsiAssemblyName')
MsiAssemblyName.add_field(1,'Component_',11592)
MsiAssemblyName.add_field(2,'Name',11775)
MsiAssemblyName.add_field(3,'Value',3583)

MsiDigitalCertificate = Table('MsiDigitalCertificate')
MsiDigitalCertificate.add_field(1,'DigitalCertificate',11592)
MsiDigitalCertificate.add_field(2,'CertData',2304)

MsiDigitalSignature = Table('MsiDigitalSignature')
MsiDigitalSignature.add_field(1,'Table',11552)
MsiDigitalSignature.add_field(2,'SignObject',11592)
MsiDigitalSignature.add_field(3,'DigitalCertificate_',3400)
MsiDigitalSignature.add_field(4,'Hash',6400)

MsiFileHash = Table('MsiFileHash')
MsiFileHash.add_field(1,'File_',11592)
MsiFileHash.add_field(2,'Options',1282)
MsiFileHash.add_field(3,'HashPart1',260)
MsiFileHash.add_field(4,'HashPart2',260)
MsiFileHash.add_field(5,'HashPart3',260)
MsiFileHash.add_field(6,'HashPart4',260)

MsiPatchHeaders = Table('MsiPatchHeaders')
MsiPatchHeaders.add_field(1,'StreamRef',11558)
MsiPatchHeaders.add_field(2,'Header',2304)

ODBCAttribute = Table('ODBCAttribute')
ODBCAttribute.add_field(1,'Driver_',11592)
ODBCAttribute.add_field(2,'Attribute',11560)
ODBCAttribute.add_field(3,'Value',8191)

ODBCDriver = Table('ODBCDriver')
ODBCDriver.add_field(1,'Driver',11592)
ODBCDriver.add_field(2,'Component_',3400)
ODBCDriver.add_field(3,'Description',3583)
ODBCDriver.add_field(4,'File_',3400)
ODBCDriver.add_field(5,'File_Setup',7496)

ODBCDataSource = Table('ODBCDataSource')
ODBCDataSource.add_field(1,'DataSource',11592)
ODBCDataSource.add_field(2,'Component_',3400)
ODBCDataSource.add_field(3,'Description',3583)
ODBCDataSource.add_field(4,'DriverDescription',3583)
ODBCDataSource.add_field(5,'Registration',1282)

ODBCSourceAttribute = Table('ODBCSourceAttribute')
ODBCSourceAttribute.add_field(1,'DataSource_',11592)
ODBCSourceAttribute.add_field(2,'Attribute',11552)
ODBCSourceAttribute.add_field(3,'Value',8191)

ODBCTranslator = Table('ODBCTranslator')
ODBCTranslator.add_field(1,'Translator',11592)
ODBCTranslator.add_field(2,'Component_',3400)
ODBCTranslator.add_field(3,'Description',3583)
ODBCTranslator.add_field(4,'File_',3400)
ODBCTranslator.add_field(5,'File_Setup',7496)

Patch = Table('Patch')
Patch.add_field(1,'File_',11592)
Patch.add_field(2,'Sequence',9474)
Patch.add_field(3,'PatchSize',260)
Patch.add_field(4,'Attributes',1282)
Patch.add_field(5,'Header',6400)
Patch.add_field(6,'StreamRef_',7462)

PatchPackage = Table('PatchPackage')
PatchPackage.add_field(1,'PatchId',11558)
PatchPackage.add_field(2,'Media_',1282)

PublishComponent = Table('PublishComponent')
PublishComponent.add_field(1,'ComponentId',11558)
PublishComponent.add_field(2,'Qualifier',11775)
PublishComponent.add_field(3,'Component_',11592)
PublishComponent.add_field(4,'AppData',8191)
PublishComponent.add_field(5,'Feature_',3366)

RadioButton = Table('RadioButton')
RadioButton.add_field(1,'Property',11592)
RadioButton.add_field(2,'Order',9474)
RadioButton.add_field(3,'Value',3392)
RadioButton.add_field(4,'X',1282)
RadioButton.add_field(5,'Y',1282)
RadioButton.add_field(6,'Width',1282)
RadioButton.add_field(7,'Height',1282)
RadioButton.add_field(8,'Text',8000)
RadioButton.add_field(9,'Help',7986)

Registry = Table('Registry')
Registry.add_field(1,'Registry',11592)
Registry.add_field(2,'Root',1282)
Registry.add_field(3,'Key',4095)
Registry.add_field(4,'Name',8191)
Registry.add_field(5,'Value',7936)
Registry.add_field(6,'Component_',3400)

RegLocator = Table('RegLocator')
RegLocator.add_field(1,'Signature_',11592)
RegLocator.add_field(2,'Root',1282)
RegLocator.add_field(3,'Key',3583)
RegLocator.add_field(4,'Name',7679)
RegLocator.add_field(5,'Type',5378)

RemoveFile = Table('RemoveFile')
RemoveFile.add_field(1,'FileKey',11592)
RemoveFile.add_field(2,'Component_',3400)
RemoveFile.add_field(3,'FileName',8191)
RemoveFile.add_field(4,'DirProperty',3400)
RemoveFile.add_field(5,'InstallMode',1282)

RemoveIniFile = Table('RemoveIniFile')
RemoveIniFile.add_field(1,'RemoveIniFile',11592)
RemoveIniFile.add_field(2,'FileName',4095)
RemoveIniFile.add_field(3,'DirProperty',7496)
RemoveIniFile.add_field(4,'Section',3936)
RemoveIniFile.add_field(5,'Key',3968)
RemoveIniFile.add_field(6,'Value',8191)
RemoveIniFile.add_field(7,'Action',1282)
RemoveIniFile.add_field(8,'Component_',3400)

RemoveRegistry = Table('RemoveRegistry')
RemoveRegistry.add_field(1,'RemoveRegistry',11592)
RemoveRegistry.add_field(2,'Root',1282)
RemoveRegistry.add_field(3,'Key',4095)
RemoveRegistry.add_field(4,'Name',8191)
RemoveRegistry.add_field(5,'Component_',3400)

ReserveCost = Table('ReserveCost')
ReserveCost.add_field(1,'ReserveKey',11592)
ReserveCost.add_field(2,'Component_',3400)
ReserveCost.add_field(3,'ReserveFolder',7496)
ReserveCost.add_field(4,'ReserveLocal',260)
ReserveCost.add_field(5,'ReserveSource',260)

SelfReg = Table('SelfReg')
SelfReg.add_field(1,'File_',11592)
SelfReg.add_field(2,'Cost',5378)

ServiceControl = Table('ServiceControl')
ServiceControl.add_field(1,'ServiceControl',11592)
ServiceControl.add_field(2,'Name',4095)
ServiceControl.add_field(3,'Event',1282)
ServiceControl.add_field(4,'Arguments',8191)
ServiceControl.add_field(5,'Wait',5378)
ServiceControl.add_field(6,'Component_',3400)

ServiceInstall = Table('ServiceInstall')
ServiceInstall.add_field(1,'ServiceInstall',11592)
ServiceInstall.add_field(2,'Name',3583)
ServiceInstall.add_field(3,'DisplayName',8191)
ServiceInstall.add_field(4,'ServiceType',260)
ServiceInstall.add_field(5,'StartType',260)
ServiceInstall.add_field(6,'ErrorControl',260)
ServiceInstall.add_field(7,'LoadOrderGroup',7679)
ServiceInstall.add_field(8,'Dependencies',7679)
ServiceInstall.add_field(9,'StartName',7679)
ServiceInstall.add_field(10,'Password',7679)
ServiceInstall.add_field(11,'Arguments',7679)
ServiceInstall.add_field(12,'Component_',3400)
ServiceInstall.add_field(13,'Description',8191)

Shortcut = Table('Shortcut')
Shortcut.add_field(1,'Shortcut',11592)
Shortcut.add_field(2,'Directory_',3400)
Shortcut.add_field(3,'Name',3968)
Shortcut.add_field(4,'Component_',3400)
Shortcut.add_field(5,'Target',3400)
Shortcut.add_field(6,'Arguments',7679)
Shortcut.add_field(7,'Description',8191)
Shortcut.add_field(8,'Hotkey',5378)
Shortcut.add_field(9,'Icon_',7496)
Shortcut.add_field(10,'IconIndex',5378)
Shortcut.add_field(11,'ShowCmd',5378)
Shortcut.add_field(12,'WkDir',7496)

Signature = Table('Signature')
Signature.add_field(1,'Signature',11592)
Signature.add_field(2,'FileName',3583)
Signature.add_field(3,'MinVersion',7444)
Signature.add_field(4,'MaxVersion',7444)
Signature.add_field(5,'MinSize',4356)
Signature.add_field(6,'MaxSize',4356)
Signature.add_field(7,'MinDate',4356)
Signature.add_field(8,'MaxDate',4356)
Signature.add_field(9,'Languages',7679)

TextStyle = Table('TextStyle')
TextStyle.add_field(1,'TextStyle',11592)
TextStyle.add_field(2,'FaceName',3360)
TextStyle.add_field(3,'Size',1282)
TextStyle.add_field(4,'Color',4356)
TextStyle.add_field(5,'StyleBits',5378)

TypeLib = Table('TypeLib')
TypeLib.add_field(1,'LibID',11558)
TypeLib.add_field(2,'Language',9474)
TypeLib.add_field(3,'Component_',11592)
TypeLib.add_field(4,'Version',4356)
TypeLib.add_field(5,'Description',8064)
TypeLib.add_field(6,'Directory_',7496)
TypeLib.add_field(7,'Feature_',3366)
TypeLib.add_field(8,'Cost',4356)

UIText = Table('UIText')
UIText.add_field(1,'Key',11592)
UIText.add_field(2,'Text',8191)

Upgrade = Table('Upgrade')
Upgrade.add_field(1,'UpgradeCode',11558)
Upgrade.add_field(2,'VersionMin',15636)
Upgrade.add_field(3,'VersionMax',15636)
Upgrade.add_field(4,'Language',15871)
Upgrade.add_field(5,'Attributes',8452)
Upgrade.add_field(6,'Remove',7679)
Upgrade.add_field(7,'ActionProperty',3400)

Verb = Table('Verb')
Verb.add_field(1,'Extension_',11775)
Verb.add_field(2,'Verb',11552)
Verb.add_field(3,'Sequence',5378)
Verb.add_field(4,'Command',8191)
Verb.add_field(5,'Argument',8191)

tables=[_Validation, ActionText, AdminExecuteSequence, Condition, AdminUISequence, AdvtExecuteSequence, AdvtUISequence, AppId, AppSearch, Property, BBControl, Billboard, Feature, Binary, BindImage, File, CCPSearch, CheckBox, Class, Component, Icon, ProgId, ComboBox, CompLocator, Complus, Directory, Control, Dialog, ControlCondition, ControlEvent, CreateFolder, CustomAction, DrLocator, DuplicateFile, Environment, Error, EventMapping, Extension, MIME, FeatureComponents, FileSFPCatalog, SFPCatalog, Font, IniFile, IniLocator, InstallExecuteSequence, InstallUISequence, IsolatedComponent, LaunchCondition, ListBox, ListView, LockPermissions, Media, MoveFile, MsiAssembly, MsiAssemblyName, MsiDigitalCertificate, MsiDigitalSignature, MsiFileHash, MsiPatchHeaders, ODBCAttribute, ODBCDriver, ODBCDataSource, ODBCSourceAttribute, ODBCTranslator, Patch, PatchPackage, PublishComponent, RadioButton, Registry, RegLocator, RemoveFile, RemoveIniFile, RemoveRegistry, ReserveCost, SelfReg, ServiceControl, ServiceInstall, Shortcut, Signature, TextStyle, TypeLib, UIText, Upgrade, Verb]

_Validation_records = [
('_Validation','Table','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of table',),
('_Validation','Column','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of column',),
('_Validation','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Description of column',),
('_Validation','Set','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Set of values that are permitted',),
('_Validation','Category','Y',Nic, Nic, Nic, Nic, Nic, 'Text;Formatted;Template;Condition;Guid;Path;Version;Language;Identifier;Binary;UpperCase;LowerCase;Filename;Paths;AnyPath;WildCardFilename;RegPath;KeyFormatted;CustomSource;Property;Cabinet;Shortcut;URL','String category',),
('_Validation','KeyColumn','Y',1,32,Nic, Nic, Nic, Nic, 'Column to which foreign key connects',),
('_Validation','KeyTable','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'For foreign key, Name of table to which data must link',),
('_Validation','MaxValue','Y',-2147483647,2147483647,Nic, Nic, Nic, Nic, 'Maximum value allowed',),
('_Validation','MinValue','Y',-2147483647,2147483647,Nic, Nic, Nic, Nic, 'Minimum value allowed',),
('_Validation','Nullable','N',Nic, Nic, Nic, Nic, Nic, 'Y;N;@','Whether the column jest nullable',),
('ActionText','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Localized description displayed w progress dialog oraz log when action jest executing.',),
('ActionText','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to be described.',),
('ActionText','Template','Y',Nic, Nic, Nic, Nic, 'Template',Nic, 'Optional localized format template used to format action data records dla display during action execution.',),
('AdminExecuteSequence','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to invoke, either w the engine albo the handler DLL.',),
('AdminExecuteSequence','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Optional expression which skips the action jeżeli evaluates to expNieprawda.If the expression syntax jest invalid, the engine will terminate, returning iesBadActionData.',),
('AdminExecuteSequence','Sequence','Y',-4,32767,Nic, Nic, Nic, Nic, 'Number that determines the sort order w which the actions are to be executed.  Leave blank to suppress action.',),
('Condition','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Expression evaluated to determine jeżeli Level w the Feature table jest to change.',),
('Condition','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Reference to a Feature entry w Feature table.',),
('Condition','Level','N',0,32767,Nic, Nic, Nic, Nic, 'New selection Level to set w Feature table jeżeli Condition evaluates to TRUE.',),
('AdminUISequence','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to invoke, either w the engine albo the handler DLL.',),
('AdminUISequence','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Optional expression which skips the action jeżeli evaluates to expNieprawda.If the expression syntax jest invalid, the engine will terminate, returning iesBadActionData.',),
('AdminUISequence','Sequence','Y',-4,32767,Nic, Nic, Nic, Nic, 'Number that determines the sort order w which the actions are to be executed.  Leave blank to suppress action.',),
('AdvtExecuteSequence','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to invoke, either w the engine albo the handler DLL.',),
('AdvtExecuteSequence','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Optional expression which skips the action jeżeli evaluates to expNieprawda.If the expression syntax jest invalid, the engine will terminate, returning iesBadActionData.',),
('AdvtExecuteSequence','Sequence','Y',-4,32767,Nic, Nic, Nic, Nic, 'Number that determines the sort order w which the actions are to be executed.  Leave blank to suppress action.',),
('AdvtUISequence','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to invoke, either w the engine albo the handler DLL.',),
('AdvtUISequence','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Optional expression which skips the action jeżeli evaluates to expNieprawda.If the expression syntax jest invalid, the engine will terminate, returning iesBadActionData.',),
('AdvtUISequence','Sequence','Y',-4,32767,Nic, Nic, Nic, Nic, 'Number that determines the sort order w which the actions are to be executed.  Leave blank to suppress action.',),
('AppId','AppId','N',Nic, Nic, Nic, Nic, 'Guid',Nic, Nic, ),
('AppId','ActivateAtStorage','Y',0,1,Nic, Nic, Nic, Nic, Nic, ),
('AppId','DllSurrogate','Y',Nic, Nic, Nic, Nic, 'Text',Nic, Nic, ),
('AppId','LocalService','Y',Nic, Nic, Nic, Nic, 'Text',Nic, Nic, ),
('AppId','RemoteServerName','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, Nic, ),
('AppId','RunAsInteractiveUser','Y',0,1,Nic, Nic, Nic, Nic, Nic, ),
('AppId','ServiceParameters','Y',Nic, Nic, Nic, Nic, 'Text',Nic, Nic, ),
('AppSearch','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The property associated przy a Signature',),
('AppSearch','Signature_','N',Nic, Nic, 'Signature;RegLocator;IniLocator;DrLocator;CompLocator',1,'Identifier',Nic, 'The Signature_ represents a unique file signature oraz jest also the foreign key w the Signature,  RegLocator, IniLocator, CompLocator oraz the DrLocator tables.',),
('Property','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of property, uppercase jeżeli settable by launcher albo loader.',),
('Property','Value','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'String value dla property.  Never null albo empty.',),
('BBControl','Type','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The type of the control.',),
('BBControl','Y','N',0,32767,Nic, Nic, Nic, Nic, 'Vertical coordinate of the upper left corner of the bounding rectangle of the control.',),
('BBControl','Text','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'A string used to set the initial text contained within a control (jeżeli appropriate).',),
('BBControl','BBControl','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of the control. This name must be unique within a billboard, but can repeat on different billboard.',),
('BBControl','Attributes','Y',0,2147483647,Nic, Nic, Nic, Nic, 'A 32-bit word that specifies the attribute flags to be applied to this control.',),
('BBControl','Billboard_','N',Nic, Nic, 'Billboard',1,'Identifier',Nic, 'External key to the Billboard table, name of the billboard.',),
('BBControl','Height','N',0,32767,Nic, Nic, Nic, Nic, 'Height of the bounding rectangle of the control.',),
('BBControl','Width','N',0,32767,Nic, Nic, Nic, Nic, 'Width of the bounding rectangle of the control.',),
('BBControl','X','N',0,32767,Nic, Nic, Nic, Nic, 'Horizontal coordinate of the upper left corner of the bounding rectangle of the control.',),
('Billboard','Action','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The name of an action. The billboard jest displayed during the progress messages received z this action.',),
('Billboard','Billboard','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of the billboard.',),
('Billboard','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'An external key to the Feature Table. The billboard jest shown only jeżeli this feature jest being installed.',),
('Billboard','Ordering','Y',0,32767,Nic, Nic, Nic, Nic, 'A positive integer. If there jest more than one billboard corresponding to an action they will be shown w the order defined by this column.',),
('Feature','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Longer descriptive text describing a visible feature item.',),
('Feature','Attributes','N',Nic, Nic, Nic, Nic, Nic, '0;1;2;4;5;6;8;9;10;16;17;18;20;21;22;24;25;26;32;33;34;36;37;38;48;49;50;52;53;54','Feature attributes',),
('Feature','Feature','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key used to identify a particular feature record.',),
('Feature','Directory_','Y',Nic, Nic, 'Directory',1,'UpperCase',Nic, 'The name of the Directory that can be configured by the UI. A non-null value will enable the browse button.',),
('Feature','Level','N',0,32767,Nic, Nic, Nic, Nic, 'The install level at which record will be initially selected. An install level of 0 will disable an item oraz prevent its display.',),
('Feature','Title','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Short text identifying a visible feature item.',),
('Feature','Display','Y',0,32767,Nic, Nic, Nic, Nic, 'Numeric sort order, used to force a specific display ordering.',),
('Feature','Feature_Parent','Y',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Optional key of a parent record w the same table. If the parent jest nie selected, then the record will nie be installed. Null indicates a root item.',),
('Binary','Name','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Unique key identifying the binary data.',),
('Binary','Data','N',Nic, Nic, Nic, Nic, 'Binary',Nic, 'The unformatted binary data.',),
('BindImage','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'The index into the File table. This must be an executable file.',),
('BindImage','Path','Y',Nic, Nic, Nic, Nic, 'Paths',Nic, 'A list of ;  delimited paths that represent the paths to be searched dla the zaimportuj DLLS. The list jest usually a list of properties each enclosed within square brackets [] .',),
('File','Sequence','N',1,32767,Nic, Nic, Nic, Nic, 'Sequence przy respect to the media images; order must track cabinet order.',),
('File','Attributes','Y',0,32767,Nic, Nic, Nic, Nic, 'Integer containing bit flags representing file attributes (przy the decimal value of each bit position w parentheses)',),
('File','File','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token, must match identifier w cabinet.  For uncompressed files, this field jest ignored.',),
('File','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key referencing Component that controls the file.',),
('File','FileName','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'File name used dla installation, may be localized.  This may contain a "short name|long name" pair.',),
('File','FileSize','N',0,2147483647,Nic, Nic, Nic, Nic, 'Size of file w bytes (integer).',),
('File','Language','Y',Nic, Nic, Nic, Nic, 'Language',Nic, 'List of decimal language Ids, comma-separated jeżeli more than one.',),
('File','Version','Y',Nic, Nic, 'File',1,'Version',Nic, 'Version string dla versioned files;  Blank dla unversioned files.',),
('CCPSearch','Signature_','N',Nic, Nic, 'Signature;RegLocator;IniLocator;DrLocator;CompLocator',1,'Identifier',Nic, 'The Signature_ represents a unique file signature oraz jest also the foreign key w the Signature,  RegLocator, IniLocator, CompLocator oraz the DrLocator tables.',),
('CheckBox','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A named property to be tied to the item.',),
('CheckBox','Value','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value string associated przy the item.',),
('Class','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Localized description dla the Class.',),
('Class','Attributes','Y',Nic, 32767,Nic, Nic, Nic, Nic, 'Class registration attributes.',),
('Class','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Required foreign key into the Feature Table, specifying the feature to validate albo install w order dla the CLSID factory to be operational.',),
('Class','AppId_','Y',Nic, Nic, 'AppId',1,'Guid',Nic, 'Optional AppID containing DCOM information dla associated application (string GUID).',),
('Class','Argument','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'optional argument dla LocalServers.',),
('Class','CLSID','N',Nic, Nic, Nic, Nic, 'Guid',Nic, 'The CLSID of an OLE factory.',),
('Class','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Required foreign key into the Component Table, specifying the component dla which to zwróć a path when called through LocateComponent.',),
('Class','Context','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The numeric server context dla this server. CLSCTX_xxxx',),
('Class','DefInprocHandler','Y',Nic, Nic, Nic, Nic, 'Filename','1;2;3','Optional default inproc handler.  Only optionally provided jeżeli Context=CLSCTX_LOCAL_SERVER.  Typically "ole32.dll" albo "mapi32.dll"',),
('Class','FileTypeMask','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Optional string containing information dla the HKCRthis CLSID) key. If multiple patterns exist, they must be delimited by a semicolon, oraz numeric subkeys will be generated: 0,1,2...',),
('Class','Icon_','Y',Nic, Nic, 'Icon',1,'Identifier',Nic, 'Optional foreign key into the Icon Table, specifying the icon file associated przy this CLSID. Will be written under the DefaultIcon key.',),
('Class','IconIndex','Y',-32767,32767,Nic, Nic, Nic, Nic, 'Optional icon index.',),
('Class','ProgId_Default','Y',Nic, Nic, 'ProgId',1,'Text',Nic, 'Optional ProgId associated przy this CLSID.',),
('Component','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, "A conditional statement that will disable this component jeżeli the specified condition evaluates to the 'Prawda' state. If a component jest disabled, it will nie be installed, regardless of the 'Action' state associated przy the component.",),
('Component','Attributes','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Remote execution option, one of irsEnum',),
('Component','Component','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key used to identify a particular component record.',),
('Component','ComponentId','Y',Nic, Nic, Nic, Nic, 'Guid',Nic, 'A string GUID unique to this component, version, oraz language.',),
('Component','Directory_','N',Nic, Nic, 'Directory',1,'Identifier',Nic, 'Required key of a Directory table record. This jest actually a property name whose value contains the actual path, set either by the AppSearch action albo przy the default setting obtained z the Directory table.',),
('Component','KeyPath','Y',Nic, Nic, 'File;Registry;ODBCDataSource',1,'Identifier',Nic, 'Either the primary key into the File table, Registry table, albo ODBCDataSource table. This extract path jest stored when the component jest installed, oraz jest used to detect the presence of the component oraz to zwróć the path to it.',),
('Icon','Name','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key. Name of the icon file.',),
('Icon','Data','N',Nic, Nic, Nic, Nic, 'Binary',Nic, 'Binary stream. The binary icon data w PE (.DLL albo .EXE) albo icon (.ICO) format.',),
('ProgId','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Localized description dla the Program identifier.',),
('ProgId','Icon_','Y',Nic, Nic, 'Icon',1,'Identifier',Nic, 'Optional foreign key into the Icon Table, specifying the icon file associated przy this ProgId. Will be written under the DefaultIcon key.',),
('ProgId','IconIndex','Y',-32767,32767,Nic, Nic, Nic, Nic, 'Optional icon index.',),
('ProgId','ProgId','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'The Program Identifier. Primary key.',),
('ProgId','Class_','Y',Nic, Nic, 'Class',1,'Guid',Nic, 'The CLSID of an OLE factory corresponding to the ProgId.',),
('ProgId','ProgId_Parent','Y',Nic, Nic, 'ProgId',1,'Text',Nic, 'The Parent Program Identifier. If specified, the ProgId column becomes a version independent prog id.',),
('ComboBox','Text','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The visible text to be assigned to the item. Optional. If this entry albo the entire column jest missing, the text jest the same jako the value.',),
('ComboBox','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A named property to be tied to this item. All the items tied to the same property become part of the same combobox.',),
('ComboBox','Value','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value string associated przy this item. Selecting the line will set the associated property to this value.',),
('ComboBox','Order','N',1,32767,Nic, Nic, Nic, Nic, 'A positive integer used to determine the ordering of the items within one list.\tThe integers do nie have to be consecutive.',),
('CompLocator','Type','Y',0,1,Nic, Nic, Nic, Nic, 'A boolean value that determines jeżeli the registry value jest a filename albo a directory location.',),
('CompLocator','Signature_','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The table key. The Signature_ represents a unique file signature oraz jest also the foreign key w the Signature table.',),
('CompLocator','ComponentId','N',Nic, Nic, Nic, Nic, 'Guid',Nic, 'A string GUID unique to this component, version, oraz language.',),
('Complus','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key referencing Component that controls the ComPlus component.',),
('Complus','ExpType','Y',0,32767,Nic, Nic, Nic, Nic, 'ComPlus component attributes.',),
('Directory','Directory','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Unique identifier dla directory entry, primary key. If a property by this name jest defined, it contains the full path to the directory.',),
('Directory','DefaultDir','N',Nic, Nic, Nic, Nic, 'DefaultDir',Nic, "The default sub-path under parent's path.",),
('Directory','Directory_Parent','Y',Nic, Nic, 'Directory',1,'Identifier',Nic, 'Reference to the entry w this table specifying the default parent directory. A record parented to itself albo przy a Null parent represents a root of the install tree.',),
('Control','Type','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The type of the control.',),
('Control','Y','N',0,32767,Nic, Nic, Nic, Nic, 'Vertical coordinate of the upper left corner of the bounding rectangle of the control.',),
('Control','Text','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'A string used to set the initial text contained within a control (jeżeli appropriate).',),
('Control','Property','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The name of a defined property to be linked to this control. ',),
('Control','Attributes','Y',0,2147483647,Nic, Nic, Nic, Nic, 'A 32-bit word that specifies the attribute flags to be applied to this control.',),
('Control','Height','N',0,32767,Nic, Nic, Nic, Nic, 'Height of the bounding rectangle of the control.',),
('Control','Width','N',0,32767,Nic, Nic, Nic, Nic, 'Width of the bounding rectangle of the control.',),
('Control','X','N',0,32767,Nic, Nic, Nic, Nic, 'Horizontal coordinate of the upper left corner of the bounding rectangle of the control.',),
('Control','Control','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of the control. This name must be unique within a dialog, but can repeat on different dialogs. ',),
('Control','Control_Next','Y',Nic, Nic, 'Control',2,'Identifier',Nic, 'The name of an other control on the same dialog. This link defines the tab order of the controls. The links have to form one albo more cycles!',),
('Control','Dialog_','N',Nic, Nic, 'Dialog',1,'Identifier',Nic, 'External key to the Dialog table, name of the dialog.',),
('Control','Help','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The help strings used przy the button. The text jest optional. ',),
('Dialog','Attributes','Y',0,2147483647,Nic, Nic, Nic, Nic, 'A 32-bit word that specifies the attribute flags to be applied to this dialog.',),
('Dialog','Height','N',0,32767,Nic, Nic, Nic, Nic, 'Height of the bounding rectangle of the dialog.',),
('Dialog','Width','N',0,32767,Nic, Nic, Nic, Nic, 'Width of the bounding rectangle of the dialog.',),
('Dialog','Dialog','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of the dialog.',),
('Dialog','Control_Cancel','Y',Nic, Nic, 'Control',2,'Identifier',Nic, 'Defines the cancel control. Hitting escape albo clicking on the close icon on the dialog jest equivalent to pushing this button.',),
('Dialog','Control_Default','Y',Nic, Nic, 'Control',2,'Identifier',Nic, 'Defines the default control. Hitting zwróć jest equivalent to pushing this button.',),
('Dialog','Control_First','N',Nic, Nic, 'Control',2,'Identifier',Nic, 'Defines the control that has the focus when the dialog jest created.',),
('Dialog','HCentering','N',0,100,Nic, Nic, Nic, Nic, 'Horizontal position of the dialog on a 0-100 scale. 0 means left end, 100 means right end of the screen, 50 center.',),
('Dialog','Title','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, "A text string specifying the title to be displayed w the title bar of the dialog's window.",),
('Dialog','VCentering','N',0,100,Nic, Nic, Nic, Nic, 'Vertical position of the dialog on a 0-100 scale. 0 means top end, 100 means bottom end of the screen, 50 center.',),
('ControlCondition','Action','N',Nic, Nic, Nic, Nic, Nic, 'Default;Disable;Enable;Hide;Show','The desired action to be taken on the specified control.',),
('ControlCondition','Condition','N',Nic, Nic, Nic, Nic, 'Condition',Nic, 'A standard conditional statement that specifies under which conditions the action should be triggered.',),
('ControlCondition','Dialog_','N',Nic, Nic, 'Dialog',1,'Identifier',Nic, 'A foreign key to the Dialog table, name of the dialog.',),
('ControlCondition','Control_','N',Nic, Nic, 'Control',2,'Identifier',Nic, 'A foreign key to the Control table, name of the control.',),
('ControlEvent','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'A standard conditional statement that specifies under which conditions an event should be triggered.',),
('ControlEvent','Ordering','Y',0,2147483647,Nic, Nic, Nic, Nic, 'An integer used to order several events tied to the same control. Can be left blank.',),
('ControlEvent','Argument','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'A value to be used jako a modifier when triggering a particular event.',),
('ControlEvent','Dialog_','N',Nic, Nic, 'Dialog',1,'Identifier',Nic, 'A foreign key to the Dialog table, name of the dialog.',),
('ControlEvent','Control_','N',Nic, Nic, 'Control',2,'Identifier',Nic, 'A foreign key to the Control table, name of the control',),
('ControlEvent','Event','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'An identifier that specifies the type of the event that should take place when the user interacts przy control specified by the first two entries.',),
('CreateFolder','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table.',),
('CreateFolder','Directory_','N',Nic, Nic, 'Directory',1,'Identifier',Nic, 'Primary key, could be foreign key into the Directory table.',),
('CustomAction','Type','N',1,16383,Nic, Nic, Nic, Nic, 'The numeric custom action type, consisting of source location, code type, entry, option flags.',),
('CustomAction','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, name of action, normally appears w sequence table unless private use.',),
('CustomAction','Source','Y',Nic, Nic, Nic, Nic, 'CustomSource',Nic, 'The table reference of the source of the code.',),
('CustomAction','Target','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Excecution parameter, depends on the type of custom action',),
('DrLocator','Signature_','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The Signature_ represents a unique file signature oraz jest also the foreign key w the Signature table.',),
('DrLocator','Path','Y',Nic, Nic, Nic, Nic, 'AnyPath',Nic, 'The path on the user system. This jest a either a subpath below the value of the Parent albo a full path. The path may contain properties enclosed within [ ] that will be expanded.',),
('DrLocator','Depth','Y',0,32767,Nic, Nic, Nic, Nic, 'The depth below the path to which the Signature_ jest recursively searched. If absent, the depth jest assumed to be 0.',),
('DrLocator','Parent','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The parent file signature. It jest also a foreign key w the Signature table. If null oraz the Path column does nie expand to a full path, then all the fixed drives of the user system are searched using the Path.',),
('DuplicateFile','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'Foreign key referencing the source file to be duplicated.',),
('DuplicateFile','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key referencing Component that controls the duplicate file.',),
('DuplicateFile','DestFolder','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of a property whose value jest assumed to resolve to the full pathname to a destination folder.',),
('DuplicateFile','DestName','Y',Nic, Nic, Nic, Nic, 'Filename',Nic, 'Filename to be given to the duplicate file.',),
('DuplicateFile','FileKey','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key used to identify a particular file entry',),
('Environment','Name','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'The name of the environmental value.',),
('Environment','Value','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value to set w the environmental settings.',),
('Environment','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table referencing component that controls the installing of the environmental value.',),
('Environment','Environment','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Unique identifier dla the environmental variable setting',),
('Error','Error','N',0,32767,Nic, Nic, Nic, Nic, 'Integer error number, obtained z header file IError(...) macros.',),
('Error','Message','Y',Nic, Nic, Nic, Nic, 'Template',Nic, 'Error formatting template, obtained z user ed. albo localizers.',),
('EventMapping','Dialog_','N',Nic, Nic, 'Dialog',1,'Identifier',Nic, 'A foreign key to the Dialog table, name of the Dialog.',),
('EventMapping','Control_','N',Nic, Nic, 'Control',2,'Identifier',Nic, 'A foreign key to the Control table, name of the control.',),
('EventMapping','Event','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'An identifier that specifies the type of the event that the control subscribes to.',),
('EventMapping','Attribute','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The name of the control attribute, that jest set when this event jest received.',),
('Extension','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Required foreign key into the Feature Table, specifying the feature to validate albo install w order dla the CLSID factory to be operational.',),
('Extension','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Required foreign key into the Component Table, specifying the component dla which to zwróć a path when called through LocateComponent.',),
('Extension','Extension','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'The extension associated przy the table row.',),
('Extension','MIME_','Y',Nic, Nic, 'MIME',1,'Text',Nic, 'Optional Context identifier, typically "type/format" associated przy the extension',),
('Extension','ProgId_','Y',Nic, Nic, 'ProgId',1,'Text',Nic, 'Optional ProgId associated przy this extension.',),
('MIME','CLSID','Y',Nic, Nic, Nic, Nic, 'Guid',Nic, 'Optional associated CLSID.',),
('MIME','ContentType','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Primary key. Context identifier, typically "type/format".',),
('MIME','Extension_','N',Nic, Nic, 'Extension',1,'Text',Nic, 'Optional associated extension (without dot)',),
('FeatureComponents','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Foreign key into Feature table.',),
('FeatureComponents','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into Component table.',),
('FileSFPCatalog','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'File associated przy the catalog',),
('FileSFPCatalog','SFPCatalog_','N',Nic, Nic, 'SFPCatalog',1,'Filename',Nic, 'Catalog associated przy the file',),
('SFPCatalog','SFPCatalog','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'File name dla the catalog.',),
('SFPCatalog','Catalog','N',Nic, Nic, Nic, Nic, 'Binary',Nic, 'SFP Catalog',),
('SFPCatalog','Dependency','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Parent catalog - only used by SFP',),
('Font','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'Primary key, foreign key into File table referencing font file.',),
('Font','FontTitle','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Font name.',),
('IniFile','Action','N',Nic, Nic, Nic, Nic, Nic, '0;1;3','The type of modification to be made, one of iifEnum',),
('IniFile','Value','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value to be written.',),
('IniFile','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table referencing component that controls the installing of the .INI value.',),
('IniFile','FileName','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'The .INI file name w which to write the information',),
('IniFile','IniFile','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('IniFile','DirProperty','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Foreign key into the Directory table denoting the directory where the .INI file is.',),
('IniFile','Key','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The .INI file key below Section.',),
('IniFile','Section','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The .INI file Section.',),
('IniLocator','Type','Y',0,2,Nic, Nic, Nic, Nic, 'An integer value that determines jeżeli the .INI value read jest a filename albo a directory location albo to be used jako jest w/o interpretation.',),
('IniLocator','Signature_','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The table key. The Signature_ represents a unique file signature oraz jest also the foreign key w the Signature table.',),
('IniLocator','FileName','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'The .INI file name.',),
('IniLocator','Key','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Key value (followed by an equals sign w INI file).',),
('IniLocator','Section','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Section name within w file (within square brackets w INI file).',),
('IniLocator','Field','Y',0,32767,Nic, Nic, Nic, Nic, 'The field w the .INI line. If Field jest null albo 0 the entire line jest read.',),
('InstallExecuteSequence','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to invoke, either w the engine albo the handler DLL.',),
('InstallExecuteSequence','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Optional expression which skips the action jeżeli evaluates to expNieprawda.If the expression syntax jest invalid, the engine will terminate, returning iesBadActionData.',),
('InstallExecuteSequence','Sequence','Y',-4,32767,Nic, Nic, Nic, Nic, 'Number that determines the sort order w which the actions are to be executed.  Leave blank to suppress action.',),
('InstallUISequence','Action','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of action to invoke, either w the engine albo the handler DLL.',),
('InstallUISequence','Condition','Y',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Optional expression which skips the action jeżeli evaluates to expNieprawda.If the expression syntax jest invalid, the engine will terminate, returning iesBadActionData.',),
('InstallUISequence','Sequence','Y',-4,32767,Nic, Nic, Nic, Nic, 'Number that determines the sort order w which the actions are to be executed.  Leave blank to suppress action.',),
('IsolatedComponent','Component_Application','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Key to Component table item dla application',),
('IsolatedComponent','Component_Shared','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Key to Component table item to be isolated',),
('LaunchCondition','Description','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Localizable text to display when condition fails oraz install must abort.',),
('LaunchCondition','Condition','N',Nic, Nic, Nic, Nic, 'Condition',Nic, 'Expression which must evaluate to TRUE w order dla install to commence.',),
('ListBox','Text','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The visible text to be assigned to the item. Optional. If this entry albo the entire column jest missing, the text jest the same jako the value.',),
('ListBox','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A named property to be tied to this item. All the items tied to the same property become part of the same listbox.',),
('ListBox','Value','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value string associated przy this item. Selecting the line will set the associated property to this value.',),
('ListBox','Order','N',1,32767,Nic, Nic, Nic, Nic, 'A positive integer used to determine the ordering of the items within one list..The integers do nie have to be consecutive.',),
('ListView','Text','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The visible text to be assigned to the item. Optional. If this entry albo the entire column jest missing, the text jest the same jako the value.',),
('ListView','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A named property to be tied to this item. All the items tied to the same property become part of the same listview.',),
('ListView','Value','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The value string associated przy this item. Selecting the line will set the associated property to this value.',),
('ListView','Order','N',1,32767,Nic, Nic, Nic, Nic, 'A positive integer used to determine the ordering of the items within one list..The integers do nie have to be consecutive.',),
('ListView','Binary_','Y',Nic, Nic, 'Binary',1,'Identifier',Nic, 'The name of the icon to be displayed przy the icon. The binary information jest looked up z the Binary Table.',),
('LockPermissions','Table','N',Nic, Nic, Nic, Nic, 'Identifier','Directory;File;Registry','Reference to another table name',),
('LockPermissions','Domain','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Domain name dla user whose permissions are being set. (usually a property)',),
('LockPermissions','LockObject','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Foreign key into Registry albo File table',),
('LockPermissions','Permission','Y',-2147483647,2147483647,Nic, Nic, Nic, Nic, 'Permission Access mask.  Full Control = 268435456 (GENERIC_ALL = 0x10000000)',),
('LockPermissions','User','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'User dla permissions to be set.  (usually a property)',),
('Media','Source','Y',Nic, Nic, Nic, Nic, 'Property',Nic, 'The property defining the location of the cabinet file.',),
('Media','Cabinet','Y',Nic, Nic, Nic, Nic, 'Cabinet',Nic, 'If some albo all of the files stored on the media are compressed w a cabinet, the name of that cabinet.',),
('Media','DiskId','N',1,32767,Nic, Nic, Nic, Nic, 'Primary key, integer to determine sort order dla table.',),
('Media','DiskPrompt','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Disk name: the visible text actually printed on the disk.  This will be used to prompt the user when this disk needs to be inserted.',),
('Media','LastSequence','N',0,32767,Nic, Nic, Nic, Nic, 'File sequence number dla the last file dla this media.',),
('Media','VolumeLabel','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The label attributed to the volume.',),
('ModuleComponents','Component','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Component contained w the module.',),
('ModuleComponents','Language','N',Nic, Nic, 'ModuleSignature',2,Nic, Nic, 'Default language ID dla module (may be changed by transform).',),
('ModuleComponents','ModuleID','N',Nic, Nic, 'ModuleSignature',1,'Identifier',Nic, 'Module containing the component.',),
('ModuleSignature','Language','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Default decimal language of module.',),
('ModuleSignature','Version','N',Nic, Nic, Nic, Nic, 'Version',Nic, 'Version of the module.',),
('ModuleSignature','ModuleID','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Module identifier (String.GUID).',),
('ModuleDependency','ModuleID','N',Nic, Nic, 'ModuleSignature',1,'Identifier',Nic, 'Module requiring the dependency.',),
('ModuleDependency','ModuleLanguage','N',Nic, Nic, 'ModuleSignature',2,Nic, Nic, 'Language of module requiring the dependency.',),
('ModuleDependency','RequiredID','N',Nic, Nic, Nic, Nic, Nic, Nic, 'String.GUID of required module.',),
('ModuleDependency','RequiredLanguage','N',Nic, Nic, Nic, Nic, Nic, Nic, 'LanguageID of the required module.',),
('ModuleDependency','RequiredVersion','Y',Nic, Nic, Nic, Nic, 'Version',Nic, 'Version of the required version.',),
('ModuleExclusion','ModuleID','N',Nic, Nic, 'ModuleSignature',1,'Identifier',Nic, 'String.GUID of module przy exclusion requirement.',),
('ModuleExclusion','ModuleLanguage','N',Nic, Nic, 'ModuleSignature',2,Nic, Nic, 'LanguageID of module przy exclusion requirement.',),
('ModuleExclusion','ExcludedID','N',Nic, Nic, Nic, Nic, Nic, Nic, 'String.GUID of excluded module.',),
('ModuleExclusion','ExcludedLanguage','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Language of excluded module.',),
('ModuleExclusion','ExcludedMaxVersion','Y',Nic, Nic, Nic, Nic, 'Version',Nic, 'Maximum version of excluded module.',),
('ModuleExclusion','ExcludedMinVersion','Y',Nic, Nic, Nic, Nic, 'Version',Nic, 'Minimum version of excluded module.',),
('MoveFile','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'If this component jest nie "selected" dla installation albo removal, no action will be taken on the associated MoveFile entry',),
('MoveFile','DestFolder','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of a property whose value jest assumed to resolve to the full path to the destination directory',),
('MoveFile','DestName','Y',Nic, Nic, Nic, Nic, 'Filename',Nic, 'Name to be given to the original file after it jest moved albo copied.  If blank, the destination file will be given the same name jako the source file',),
('MoveFile','FileKey','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key that uniquely identifies a particular MoveFile record',),
('MoveFile','Options','N',0,1,Nic, Nic, Nic, Nic, 'Integer value specifying the MoveFile operating mode, one of imfoEnum',),
('MoveFile','SourceFolder','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of a property whose value jest assumed to resolve to the full path to the source directory',),
('MoveFile','SourceName','Y',Nic, Nic, Nic, Nic, 'Text',Nic, "Name of the source file(s) to be moved albo copied.  Can contain the '*' albo '?' wildcards.",),
('MsiAssembly','Attributes','Y',Nic, Nic, Nic, Nic, Nic, Nic, 'Assembly attributes',),
('MsiAssembly','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Foreign key into Feature table.',),
('MsiAssembly','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into Component table.',),
('MsiAssembly','File_Application','Y',Nic, Nic, 'File',1,'Identifier',Nic, 'Foreign key into File table, denoting the application context dla private assemblies. Null dla global assemblies.',),
('MsiAssembly','File_Manifest','Y',Nic, Nic, 'File',1,'Identifier',Nic, 'Foreign key into the File table denoting the manifest file dla the assembly.',),
('MsiAssemblyName','Name','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'The name part of the name-value pairs dla the assembly name.',),
('MsiAssemblyName','Value','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'The value part of the name-value pairs dla the assembly name.',),
('MsiAssemblyName','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into Component table.',),
('MsiDigitalCertificate','CertData','N',Nic, Nic, Nic, Nic, 'Binary',Nic, 'A certificate context blob dla a signer certificate',),
('MsiDigitalCertificate','DigitalCertificate','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A unique identifier dla the row',),
('MsiDigitalSignature','Table','N',Nic, Nic, Nic, Nic, Nic, 'Media','Reference to another table name (only Media table jest supported)',),
('MsiDigitalSignature','DigitalCertificate_','N',Nic, Nic, 'MsiDigitalCertificate',1,'Identifier',Nic, 'Foreign key to MsiDigitalCertificate table identifying the signer certificate',),
('MsiDigitalSignature','Hash','Y',Nic, Nic, Nic, Nic, 'Binary',Nic, 'The encoded hash blob z the digital signature',),
('MsiDigitalSignature','SignObject','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Foreign key to Media table',),
('MsiFileHash','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'Primary key, foreign key into File table referencing file przy this hash',),
('MsiFileHash','Options','N',0,32767,Nic, Nic, Nic, Nic, 'Various options oraz attributes dla this hash.',),
('MsiFileHash','HashPart1','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Size of file w bytes (integer).',),
('MsiFileHash','HashPart2','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Size of file w bytes (integer).',),
('MsiFileHash','HashPart3','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Size of file w bytes (integer).',),
('MsiFileHash','HashPart4','N',Nic, Nic, Nic, Nic, Nic, Nic, 'Size of file w bytes (integer).',),
('MsiPatchHeaders','StreamRef','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key. A unique identifier dla the row.',),
('MsiPatchHeaders','Header','N',Nic, Nic, Nic, Nic, 'Binary',Nic, 'Binary stream. The patch header, used dla patch validation.',),
('ODBCAttribute','Value','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Value dla ODBC driver attribute',),
('ODBCAttribute','Attribute','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Name of ODBC driver attribute',),
('ODBCAttribute','Driver_','N',Nic, Nic, 'ODBCDriver',1,'Identifier',Nic, 'Reference to ODBC driver w ODBCDriver table',),
('ODBCDriver','Description','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Text used jako registered name dla driver, non-localized',),
('ODBCDriver','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'Reference to key driver file',),
('ODBCDriver','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Reference to associated component',),
('ODBCDriver','Driver','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized.internal token dla driver',),
('ODBCDriver','File_Setup','Y',Nic, Nic, 'File',1,'Identifier',Nic, 'Optional reference to key driver setup DLL',),
('ODBCDataSource','Description','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Text used jako registered name dla data source',),
('ODBCDataSource','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Reference to associated component',),
('ODBCDataSource','DataSource','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized.internal token dla data source',),
('ODBCDataSource','DriverDescription','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Reference to driver description, may be existing driver',),
('ODBCDataSource','Registration','N',0,1,Nic, Nic, Nic, Nic, 'Registration option: 0=machine, 1=user, others t.b.d.',),
('ODBCSourceAttribute','Value','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Value dla ODBC data source attribute',),
('ODBCSourceAttribute','Attribute','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Name of ODBC data source attribute',),
('ODBCSourceAttribute','DataSource_','N',Nic, Nic, 'ODBCDataSource',1,'Identifier',Nic, 'Reference to ODBC data source w ODBCDataSource table',),
('ODBCTranslator','Description','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'Text used jako registered name dla translator',),
('ODBCTranslator','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'Reference to key translator file',),
('ODBCTranslator','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Reference to associated component',),
('ODBCTranslator','File_Setup','Y',Nic, Nic, 'File',1,'Identifier',Nic, 'Optional reference to key translator setup DLL',),
('ODBCTranslator','Translator','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized.internal token dla translator',),
('Patch','Sequence','N',0,32767,Nic, Nic, Nic, Nic, 'Primary key, sequence przy respect to the media images; order must track cabinet order.',),
('Patch','Attributes','N',0,32767,Nic, Nic, Nic, Nic, 'Integer containing bit flags representing patch attributes',),
('Patch','File_','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token, foreign key to File table, must match identifier w cabinet.',),
('Patch','Header','Y',Nic, Nic, Nic, Nic, 'Binary',Nic, 'Binary stream. The patch header, used dla patch validation.',),
('Patch','PatchSize','N',0,2147483647,Nic, Nic, Nic, Nic, 'Size of patch w bytes (integer).',),
('Patch','StreamRef_','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Identifier. Foreign key to the StreamRef column of the MsiPatchHeaders table.',),
('PatchPackage','Media_','N',0,32767,Nic, Nic, Nic, Nic, 'Foreign key to DiskId column of Media table. Indicates the disk containing the patch package.',),
('PatchPackage','PatchId','N',Nic, Nic, Nic, Nic, 'Guid',Nic, 'A unique string GUID representing this patch.',),
('PublishComponent','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Foreign key into the Feature table.',),
('PublishComponent','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table.',),
('PublishComponent','ComponentId','N',Nic, Nic, Nic, Nic, 'Guid',Nic, 'A string GUID that represents the component id that will be requested by the alien product.',),
('PublishComponent','AppData','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'This jest localisable Application specific data that can be associated przy a Qualified Component.',),
('PublishComponent','Qualifier','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'This jest defined only when the ComponentId column jest an Qualified Component Id. This jest the Qualifier dla ProvideComponentIndirect.',),
('RadioButton','Y','N',0,32767,Nic, Nic, Nic, Nic, 'The vertical coordinate of the upper left corner of the bounding rectangle of the radio button.',),
('RadioButton','Text','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The visible title to be assigned to the radio button.',),
('RadioButton','Property','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A named property to be tied to this radio button. All the buttons tied to the same property become part of the same group.',),
('RadioButton','Height','N',0,32767,Nic, Nic, Nic, Nic, 'The height of the button.',),
('RadioButton','Width','N',0,32767,Nic, Nic, Nic, Nic, 'The width of the button.',),
('RadioButton','X','N',0,32767,Nic, Nic, Nic, Nic, 'The horizontal coordinate of the upper left corner of the bounding rectangle of the radio button.',),
('RadioButton','Value','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value string associated przy this button. Selecting the button will set the associated property to this value.',),
('RadioButton','Order','N',1,32767,Nic, Nic, Nic, Nic, 'A positive integer used to determine the ordering of the items within one list..The integers do nie have to be consecutive.',),
('RadioButton','Help','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The help strings used przy the button. The text jest optional.',),
('Registry','Name','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The registry value name.',),
('Registry','Value','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The registry value.',),
('Registry','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table referencing component that controls the installing of the registry value.',),
('Registry','Key','N',Nic, Nic, Nic, Nic, 'RegPath',Nic, 'The key dla the registry value.',),
('Registry','Registry','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('Registry','Root','N',-1,3,Nic, Nic, Nic, Nic, 'The predefined root key dla the registry value, one of rrkEnum.',),
('RegLocator','Name','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The registry value name.',),
('RegLocator','Type','Y',0,18,Nic, Nic, Nic, Nic, 'An integer value that determines jeżeli the registry value jest a filename albo a directory location albo to be used jako jest w/o interpretation.',),
('RegLocator','Signature_','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The table key. The Signature_ represents a unique file signature oraz jest also the foreign key w the Signature table. If the type jest 0, the registry values refers a directory, oraz _Signature jest nie a foreign key.',),
('RegLocator','Key','N',Nic, Nic, Nic, Nic, 'RegPath',Nic, 'The key dla the registry value.',),
('RegLocator','Root','N',0,3,Nic, Nic, Nic, Nic, 'The predefined root key dla the registry value, one of rrkEnum.',),
('RemoveFile','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key referencing Component that controls the file to be removed.',),
('RemoveFile','FileKey','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key used to identify a particular file entry',),
('RemoveFile','FileName','Y',Nic, Nic, Nic, Nic, 'WildCardFilename',Nic, 'Name of the file to be removed.',),
('RemoveFile','DirProperty','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of a property whose value jest assumed to resolve to the full pathname to the folder of the file to be removed.',),
('RemoveFile','InstallMode','N',Nic, Nic, Nic, Nic, Nic, '1;2;3','Installation option, one of iimEnum.',),
('RemoveIniFile','Action','N',Nic, Nic, Nic, Nic, Nic, '2;4','The type of modification to be made, one of iifEnum.',),
('RemoveIniFile','Value','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The value to be deleted. The value jest required when Action jest iifIniRemoveTag',),
('RemoveIniFile','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table referencing component that controls the deletion of the .INI value.',),
('RemoveIniFile','FileName','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'The .INI file name w which to delete the information',),
('RemoveIniFile','DirProperty','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Foreign key into the Directory table denoting the directory where the .INI file is.',),
('RemoveIniFile','Key','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The .INI file key below Section.',),
('RemoveIniFile','Section','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The .INI file Section.',),
('RemoveIniFile','RemoveIniFile','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('RemoveRegistry','Name','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The registry value name.',),
('RemoveRegistry','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table referencing component that controls the deletion of the registry value.',),
('RemoveRegistry','Key','N',Nic, Nic, Nic, Nic, 'RegPath',Nic, 'The key dla the registry value.',),
('RemoveRegistry','Root','N',-1,3,Nic, Nic, Nic, Nic, 'The predefined root key dla the registry value, one of rrkEnum',),
('RemoveRegistry','RemoveRegistry','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('ReserveCost','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Reserve a specified amount of space jeżeli this component jest to be installed.',),
('ReserveCost','ReserveFolder','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of a property whose value jest assumed to resolve to the full path to the destination directory',),
('ReserveCost','ReserveKey','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key that uniquely identifies a particular ReserveCost record',),
('ReserveCost','ReserveLocal','N',0,2147483647,Nic, Nic, Nic, Nic, 'Disk space to reserve jeżeli linked component jest installed locally.',),
('ReserveCost','ReserveSource','N',0,2147483647,Nic, Nic, Nic, Nic, 'Disk space to reserve jeżeli linked component jest installed to run z the source location.',),
('SelfReg','File_','N',Nic, Nic, 'File',1,'Identifier',Nic, 'Foreign key into the File table denoting the module that needs to be registered.',),
('SelfReg','Cost','Y',0,32767,Nic, Nic, Nic, Nic, 'The cost of registering the module.',),
('ServiceControl','Name','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Name of a service. /, \\, comma oraz space are invalid',),
('ServiceControl','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Required foreign key into the Component Table that controls the startup of the service',),
('ServiceControl','Event','N',0,187,Nic, Nic, Nic, Nic, 'Bit field:  Install:  0x1 = Start, 0x2 = Stop, 0x8 = Delete, Uninstall: 0x10 = Start, 0x20 = Stop, 0x80 = Delete',),
('ServiceControl','ServiceControl','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('ServiceControl','Arguments','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Arguments dla the service.  Separate by [~].',),
('ServiceControl','Wait','Y',0,1,Nic, Nic, Nic, Nic, 'Boolean dla whether to wait dla the service to fully start',),
('ServiceInstall','Name','N',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Internal Name of the Service',),
('ServiceInstall','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'Description of service.',),
('ServiceInstall','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Required foreign key into the Component Table that controls the startup of the service',),
('ServiceInstall','Arguments','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Arguments to include w every start of the service, dalejed to WinMain',),
('ServiceInstall','ServiceInstall','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('ServiceInstall','Dependencies','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Other services this depends on to start.  Separate by [~], oraz end przy [~][~]',),
('ServiceInstall','DisplayName','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'External Name of the Service',),
('ServiceInstall','ErrorControl','N',-2147483647,2147483647,Nic, Nic, Nic, Nic, 'Severity of error jeżeli service fails to start',),
('ServiceInstall','LoadOrderGroup','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'LoadOrderGroup',),
('ServiceInstall','Password','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'password to run service with.  (przy StartName)',),
('ServiceInstall','ServiceType','N',-2147483647,2147483647,Nic, Nic, Nic, Nic, 'Type of the service',),
('ServiceInstall','StartName','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'User albo object name to run service as',),
('ServiceInstall','StartType','N',0,4,Nic, Nic, Nic, Nic, 'Type of the service',),
('Shortcut','Name','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'The name of the shortcut to be created.',),
('Shortcut','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The description dla the shortcut.',),
('Shortcut','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Foreign key into the Component table denoting the component whose selection gates the shortcut creation/deletion.',),
('Shortcut','Icon_','Y',Nic, Nic, 'Icon',1,'Identifier',Nic, 'Foreign key into the File table denoting the external icon file dla the shortcut.',),
('Shortcut','IconIndex','Y',-32767,32767,Nic, Nic, Nic, Nic, 'The icon index dla the shortcut.',),
('Shortcut','Directory_','N',Nic, Nic, 'Directory',1,'Identifier',Nic, 'Foreign key into the Directory table denoting the directory where the shortcut file jest created.',),
('Shortcut','Target','N',Nic, Nic, Nic, Nic, 'Shortcut',Nic, 'The shortcut target. This jest usually a property that jest expanded to a file albo a folder that the shortcut points to.',),
('Shortcut','Arguments','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The command-line arguments dla the shortcut.',),
('Shortcut','Shortcut','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Primary key, non-localized token.',),
('Shortcut','Hotkey','Y',0,32767,Nic, Nic, Nic, Nic, 'The hotkey dla the shortcut. It has the virtual-key code dla the key w the low-order byte, oraz the modifier flags w the high-order byte. ',),
('Shortcut','ShowCmd','Y',Nic, Nic, Nic, Nic, Nic, '1;3;7','The show command dla the application window.The following values may be used.',),
('Shortcut','WkDir','Y',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of property defining location of working directory.',),
('Signature','FileName','N',Nic, Nic, Nic, Nic, 'Filename',Nic, 'The name of the file. This may contain a "short name|long name" pair.',),
('Signature','Signature','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'The table key. The Signature represents a unique file signature.',),
('Signature','Languages','Y',Nic, Nic, Nic, Nic, 'Language',Nic, 'The languages supported by the file.',),
('Signature','MaxDate','Y',0,2147483647,Nic, Nic, Nic, Nic, 'The maximum creation date of the file.',),
('Signature','MaxSize','Y',0,2147483647,Nic, Nic, Nic, Nic, 'The maximum size of the file. ',),
('Signature','MaxVersion','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The maximum version of the file.',),
('Signature','MinDate','Y',0,2147483647,Nic, Nic, Nic, Nic, 'The minimum creation date of the file.',),
('Signature','MinSize','Y',0,2147483647,Nic, Nic, Nic, Nic, 'The minimum size of the file.',),
('Signature','MinVersion','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The minimum version of the file.',),
('TextStyle','TextStyle','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'Name of the style. The primary key of this table. This name jest embedded w the texts to indicate a style change.',),
('TextStyle','Color','Y',0,16777215,Nic, Nic, Nic, Nic, 'An integer indicating the color of the string w the RGB format (Red, Green, Blue each 0-255, RGB = R + 256*G + 256^2*B).',),
('TextStyle','FaceName','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'A string indicating the name of the font used. Required. The string must be at most 31 characters long.',),
('TextStyle','Size','N',0,32767,Nic, Nic, Nic, Nic, 'The size of the font used. This size jest given w our units (1/12 of the system font height). Assuming that the system font jest set to 12 point size, this jest equivalent to the point size.',),
('TextStyle','StyleBits','Y',0,15,Nic, Nic, Nic, Nic, 'A combination of style bits.',),
('TypeLib','Description','Y',Nic, Nic, Nic, Nic, 'Text',Nic, Nic, ),
('TypeLib','Feature_','N',Nic, Nic, 'Feature',1,'Identifier',Nic, 'Required foreign key into the Feature Table, specifying the feature to validate albo install w order dla the type library to be operational.',),
('TypeLib','Component_','N',Nic, Nic, 'Component',1,'Identifier',Nic, 'Required foreign key into the Component Table, specifying the component dla which to zwróć a path when called through LocateComponent.',),
('TypeLib','Directory_','Y',Nic, Nic, 'Directory',1,'Identifier',Nic, 'Optional. The foreign key into the Directory table denoting the path to the help file dla the type library.',),
('TypeLib','Language','N',0,32767,Nic, Nic, Nic, Nic, 'The language of the library.',),
('TypeLib','Version','Y',0,16777215,Nic, Nic, Nic, Nic, 'The version of the library. The minor version jest w the lower 8 bits of the integer. The major version jest w the next 16 bits. ',),
('TypeLib','Cost','Y',0,2147483647,Nic, Nic, Nic, Nic, 'The cost associated przy the registration of the typelib. This column jest currently optional.',),
('TypeLib','LibID','N',Nic, Nic, Nic, Nic, 'Guid',Nic, 'The GUID that represents the library.',),
('UIText','Text','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The localized version of the string.',),
('UIText','Key','N',Nic, Nic, Nic, Nic, 'Identifier',Nic, 'A unique key that identifies the particular string.',),
('Upgrade','Attributes','N',0,2147483647,Nic, Nic, Nic, Nic, 'The attributes of this product set.',),
('Upgrade','Language','Y',Nic, Nic, Nic, Nic, 'Language',Nic, 'A comma-separated list of languages dla either products w this set albo products nie w this set.',),
('Upgrade','ActionProperty','N',Nic, Nic, Nic, Nic, 'UpperCase',Nic, 'The property to set when a product w this set jest found.',),
('Upgrade','Remove','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The list of features to remove when uninstalling a product z this set.  The default jest "ALL".',),
('Upgrade','UpgradeCode','N',Nic, Nic, Nic, Nic, 'Guid',Nic, 'The UpgradeCode GUID belonging to the products w this set.',),
('Upgrade','VersionMax','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The maximum ProductVersion of the products w this set.  The set may albo may nie include products przy this particular version.',),
('Upgrade','VersionMin','Y',Nic, Nic, Nic, Nic, 'Text',Nic, 'The minimum ProductVersion of the products w this set.  The set may albo may nie include products przy this particular version.',),
('Verb','Sequence','Y',0,32767,Nic, Nic, Nic, Nic, 'Order within the verbs dla a particular extension. Also used simply to specify the default verb.',),
('Verb','Argument','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'Optional value dla the command arguments.',),
('Verb','Extension_','N',Nic, Nic, 'Extension',1,'Text',Nic, 'The extension associated przy the table row.',),
('Verb','Verb','N',Nic, Nic, Nic, Nic, 'Text',Nic, 'The verb dla the command.',),
('Verb','Command','Y',Nic, Nic, Nic, Nic, 'Formatted',Nic, 'The command text.',),
]
