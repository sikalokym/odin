-- Drop triggers for the first batch of tables
DROP TRIGGER IF EXISTS [dbo].[trg_Model_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_SalesVersion_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Gearbox_InsertUpdate];

-- Drop triggers for the second batch of tables
DROP TRIGGER IF EXISTS [dbo].[trg_Steering_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_MarketCode_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Body_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Color_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Upholstery_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Options_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Package_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_Feature_InsertUpdate];

-- Specific triggers mentioned
DROP TRIGGER IF EXISTS [dbo].[trg_Engine_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNO_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_CustomFeature_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOCustomFeature_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOFeature_InsertUpdate];

DROP TRIGGER IF EXISTS [dbo].[trg_PNOColor_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOUpholstery_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOOptions_InsertUpdate];

-- Drop triggers for the custom tables
DROP TRIGGER IF EXISTS [dbo].[trg_PNOCustom_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOColorCustom_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOUpholsteryCustom_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOOptionsCustom_InsertUpdate];
DROP TRIGGER IF EXISTS [dbo].[trg_PNOPackageCustom_InsertUpdate];
GO

-- Drop all tables in the database
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'VisaFilesPrices')
DROP TABLE VisaFilesPrices

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'CustomizationRules')
DROP TABLE [dbo].[CustomizationRules]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOOptionsCustom')
DROP TABLE [dbo].[PNOOptionsCustom]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOUpholsteryCustom')
DROP TABLE [dbo].[PNOUpholsteryCustom]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOColorCustom')
DROP TABLE [dbo].[PNOColorCustom]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOPackageCustom')
DROP TABLE [dbo].[PNOPackageCustom]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOCustom')
DROP TABLE [dbo].[PNOCustom]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOColor')
DROP TABLE [dbo].[PNOColor]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOModel')
DROP TABLE [dbo].[PNOModel]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOUpholstery')
DROP TABLE [dbo].[PNOUpholstery]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOOptions')
DROP TABLE [dbo].[PNOOptions]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOPackage')
DROP TABLE [dbo].[PNOPackage]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOFeature')
DROP TABLE [dbo].[PNOFeature]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOCustomFeature')
DROP TABLE [dbo].[PNOCustomFeature]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'OptionForbiddsOption')
DROP TABLE [dbo].[OptionForbiddsOption]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'OptionRequiresOption')
DROP TABLE [dbo].[OptionRequiresOption]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'OptionForbiddenWithUpholsteries')
DROP TABLE [dbo].[OptionForbiddenWithUpholsteries]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'OptionForbiddenWithColours')
DROP TABLE [dbo].[OptionForbiddenWithColours]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'UpholsteryRequiresOption')
DROP TABLE [dbo].[UpholsteryRequiresOption]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'PNO')
DROP TABLE [dbo].[PNO]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Model')
DROP TABLE [dbo].[Model]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Engine')
DROP TABLE [dbo].[Engine]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'SalesVersion')
DROP TABLE [dbo].[SalesVersion]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Steering')
DROP TABLE [dbo].[Steering]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'MarketCode')
DROP TABLE [dbo].[MarketCode]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Gearbox')
DROP TABLE [dbo].[Gearbox]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Body')
DROP TABLE [dbo].[Body]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Color')
DROP TABLE [dbo].[Color]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Upholstery')
DROP TABLE [dbo].[Upholstery]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Options')
DROP TABLE [dbo].[Options]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Package')
DROP TABLE [dbo].[Package]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Feature')
DROP TABLE [dbo].[Feature]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'SupportedCountry')
DROP TABLE [dbo].[SupportedCountry]
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'ChangeLog')
DROP TABLE [dbo].[ChangeLog]
GO
