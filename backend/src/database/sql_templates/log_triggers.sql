-- Declare a variable to hold your dynamic SQL
DECLARE @sql NVARCHAR(MAX);

-- List of your tables
DECLARE @tables TABLE (TableName NVARCHAR(128));
INSERT INTO @tables (TableName)
VALUES 
    ('Model'),
    ('SalesVersion'),
    ('Gearbox');

-- Cursor to iterate through the table names
DECLARE table_cursor CURSOR FOR 
SELECT TableName FROM @tables;

OPEN table_cursor;
DECLARE @tableName NVARCHAR(128);

FETCH NEXT FROM table_cursor INTO @tableName;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Generate the dynamic SQL for creating the trigger
    SET @sql = N'CREATE TRIGGER [dbo].[trg_' + @tableName + '_InsertUpdate] 
ON [dbo].[' + @tableName + ']
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT CountryCode,
            ID, 
            ''' + @tableName + ''', 
            GETDATE(), 
            ''Insert'',
            ''ID'', 
            '''',
            ID
        FROM inserted;
    END
    
    -- Log Updates for all columns
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''ShortText'', deleted.ShortText, inserted.ShortText
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.ShortText, '''') <> ISNULL(inserted.ShortText, '''')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''MarketText'', deleted.MarketText, inserted.MarketText
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.MarketText, '''') <> ISNULL(inserted.MarketText, '''')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''CustomName'', deleted.CustomName, inserted.CustomName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.CustomName, '''') <> ISNULL(inserted.CustomName, '''')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''EndDate'', CAST(deleted.EndDate AS VARCHAR), CAST(inserted.EndDate AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END';

    -- Execute the dynamic SQL
    EXEC sp_executesql @sql;

    -- Move to the next table
    FETCH NEXT FROM table_cursor INTO @tableName;
END

-- Cleanup
CLOSE table_cursor;
DEALLOCATE table_cursor;
GO

-- Declare a variable to hold your dynamic SQL
DECLARE @sql NVARCHAR(MAX);

-- List of your tables
DECLARE @tables TABLE (TableName NVARCHAR(128));
INSERT INTO @tables (TableName)
VALUES 
    ('Steering'), 
    ('MarketCode'), 
    ('Body'),
    ('Color'), 
    ('Upholstery'), 
    ('Options'), 
    ('Package'), 
    ('Feature');

-- Cursor to iterate through the table names
DECLARE table_cursor CURSOR FOR 
SELECT TableName FROM @tables;

OPEN table_cursor;
DECLARE @tableName NVARCHAR(128);

FETCH NEXT FROM table_cursor INTO @tableName;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Generate the dynamic SQL for creating the trigger
    SET @sql = N'CREATE TRIGGER [dbo].[trg_' + @tableName + '_InsertUpdate] 
ON [dbo].[' + @tableName + ']
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT CountryCode,
            ID, 
            ''' + @tableName + ''', 
            GETDATE(), 
            ''Insert'',
            ''ID'', 
            '''',
            ID
        FROM inserted;
    END
    
    -- Log Updates for all columns
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''ShortText'', deleted.ShortText, inserted.ShortText
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.ShortText, '''') <> ISNULL(inserted.ShortText, '''')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''MarketText'', deleted.MarketText, inserted.MarketText
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.MarketText, '''') <> ISNULL(inserted.MarketText, '''')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''EndDate'', CAST(deleted.EndDate AS VARCHAR), CAST(inserted.EndDate AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END';

    -- Execute the dynamic SQL
    EXEC sp_executesql @sql;

    -- Move to the next table
    FETCH NEXT FROM table_cursor INTO @tableName;
END

-- Cleanup
CLOSE table_cursor;
DEALLOCATE table_cursor;
GO

CREATE TRIGGER [dbo].[trg_Engine_InsertUpdate]
ON [dbo].[Engine]
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT CountryCode,
            ID, 
            'Engine', 
            GETDATE(), 
            'Insert',
            'ID',
            '',
            ID
        FROM inserted;
    END
    -- Log Updates
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'ShortText', deleted.ShortText, inserted.ShortText
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.ShortText, '') <> ISNULL(inserted.ShortText, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'MarketText', deleted.MarketText, inserted.MarketText
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.MarketText, '') <> ISNULL(inserted.MarketText, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'CustomName', deleted.CustomName, inserted.CustomName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.CustomName, '') <> ISNULL(inserted.CustomName, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'Performance', deleted.Performance, inserted.Performance
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Performance, '') <> ISNULL(inserted.Performance, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'EngineCategory', deleted.EngineCategory, inserted.EngineCategory
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.EngineCategory, '') <> ISNULL(inserted.EngineCategory, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'EngineType', deleted.EngineType, inserted.EngineType
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.EngineType, '') <> ISNULL(inserted.EngineType, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'Engine', GETDATE(), 'Update', 'EndDate', CONVERT(VARCHAR, deleted.EndDate, 120), CONVERT(VARCHAR, inserted.EndDate, 120)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END
GO

CREATE TRIGGER [dbo].[trg_PNO_InsertUpdate]
ON [dbo].[PNO]
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT CountryCode,
            ID, 
            'PNO', 
            GETDATE(), 
            'Insert',
            'ID',
            '',
            ID
        FROM inserted;
    END

    -- Log Updates
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'Model', deleted.Model, inserted.Model
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Model, '') <> ISNULL(inserted.Model, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'Engine', deleted.Engine, inserted.Engine
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Engine, '') <> ISNULL(inserted.Engine, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'SalesVersion', deleted.SalesVersion, inserted.SalesVersion
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.SalesVersion, '') <> ISNULL(inserted.SalesVersion, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'Steering', deleted.Steering, inserted.Steering
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Steering, '') <> ISNULL(inserted.Steering, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'Gearbox', deleted.Gearbox, inserted.Gearbox
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Gearbox, '') <> ISNULL(inserted.Gearbox, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'Body', deleted.Body, inserted.Body
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Body, '') <> ISNULL(inserted.Body, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'MarketCode', deleted.MarketCode, inserted.MarketCode
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.MarketCode, '') <> ISNULL(inserted.MarketCode, '')
        UNION ALL
        SELECT inserted.CountryCode, CAST(inserted.ID AS VARCHAR(128)), 'PNO', GETDATE(), 'Update', 'EndDate', CONVERT(VARCHAR, deleted.EndDate, 120), CONVERT(VARCHAR, inserted.EndDate, 120)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END
GO

CREATE TRIGGER [dbo].[trg_PNOPackage_InsertUpdate]
ON [dbo].[PNOPackage]
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '',
            ID, 
            'PNOPackage', 
            GETDATE(), 
            'Insert',
            'ID',
            '',
            ID
        FROM inserted;
    END

    -- Log Updates
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'Title', deleted.Title, inserted.Title
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Title, '') <> ISNULL(inserted.Title, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'RuleCode', deleted.RuleCode, inserted.RuleCode
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.RuleCode, '') <> ISNULL(inserted.RuleCode, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'RuleType', deleted.RuleType, inserted.RuleType
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.RuleType, '') <> ISNULL(inserted.RuleType, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'RuleName', deleted.RuleName, inserted.RuleName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.RuleName, '') <> ISNULL(inserted.RuleName, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'RuleBase', deleted.RuleBase, inserted.RuleBase
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.RuleBase, '') <> ISNULL(inserted.RuleBase, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'EndDate', CONVERT(VARCHAR, deleted.EndDate, 120), CONVERT(VARCHAR, inserted.EndDate, 120)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END
GO

CREATE TRIGGER [dbo].[trg_PNOFeature_InsertUpdate]
ON [dbo].[PNOFeature]
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '',
            ID, 
            'PNOFeature', 
            GETDATE(), 
            'Insert',
            'ID',
            '',
            ID
        FROM inserted;
    END

    -- Log Updates
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'Reference', deleted.Reference, inserted.Reference
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Reference, '') <> ISNULL(inserted.Reference, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'Options', deleted.Options, inserted.Options
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.Options, '') <> ISNULL(inserted.Options, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'RuleName', deleted.RuleName, inserted.RuleName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.RuleName, '') <> ISNULL(inserted.RuleName, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'CustomName', deleted.CustomName, inserted.CustomName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.CustomName, '') <> ISNULL(inserted.CustomName, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'CustomCategory', deleted.CustomCategory, inserted.CustomCategory
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.CustomCategory, '') <> ISNULL(inserted.CustomCategory, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOFeature', GETDATE(), 'Update', 'EndDate', CONVERT(VARCHAR, deleted.EndDate, 120), CONVERT(VARCHAR, inserted.EndDate, 120)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END
GO

CREATE TRIGGER [dbo].[trg_PNOCustomFeature_InsertUpdate]
ON [dbo].[PNOCustomFeature]
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '',
            ID, 
            'PNOCustomFeature', 
            GETDATE(), 
            'Insert',
            'ID',
            '',
            ID
        FROM inserted;
    END

    -- Log Updates
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOCustomFeature', GETDATE(), 'Update', 'CustomName', deleted.CustomName, inserted.CustomName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.CustomName, '') <> ISNULL(inserted.CustomName, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOCustomFeature', GETDATE(), 'Update', 'CustomCategory', deleted.CustomCategory, inserted.CustomCategory
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.CustomCategory, '') <> ISNULL(inserted.CustomCategory, '')
        UNION ALL
        SELECT '', CAST(inserted.ID AS VARCHAR(128)), 'PNOCustomFeature', GETDATE(), 'Update', 'EndDate', CONVERT(VARCHAR, deleted.EndDate, 120), CONVERT(VARCHAR, inserted.EndDate, 120)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END
GO

CREATE TRIGGER [dbo].[trg_PNOUpholsteryCustom_InsertUpdate]
ON [dbo].[PNOUpholsteryCustom]
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '',
            RelationID, 
            'PNOUpholsteryCustom', 
            GETDATE(), 
            'Insert',
            'RelationID',
            '',
            RelationID
        FROM inserted;
    END

    -- Log Updates
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '', CAST(inserted.RelationID AS VARCHAR(128)), 'PNOUpholsteryCustom', GETDATE(), 'Update', 'Price', CAST(deleted.Price AS VARCHAR), CAST(inserted.Price AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.Price, 0) <> ISNULL(inserted.Price, 0)
        UNION ALL
        SELECT '', CAST(inserted.RelationID AS VARCHAR(128)), 'PNOUpholsteryCustom', GETDATE(), 'Update', 'PriceBeforeTax', CAST(deleted.PriceBeforeTax AS VARCHAR), CAST(inserted.PriceBeforeTax AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.PriceBeforeTax, 0) <> ISNULL(inserted.PriceBeforeTax, 0)
        UNION ALL
        SELECT '', CAST(inserted.RelationID AS VARCHAR(128)), 'PNOUpholsteryCustom', GETDATE(), 'Update', 'CustomName', deleted.CustomName, inserted.CustomName
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.CustomName, '') <> ISNULL(inserted.CustomName, '')
        UNION ALL
        SELECT '', CAST(inserted.RelationID AS VARCHAR(128)), 'PNOUpholsteryCustom', GETDATE(), 'Update', 'CustomCategory', deleted.CustomCategory, inserted.CustomCategory
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.CustomCategory, '') <> ISNULL(inserted.CustomCategory, '')
        UNION ALL
        SELECT '', CAST(inserted.RelationID AS VARCHAR(128)), 'PNOUpholsteryCustom', GETDATE(), 'Update', 'EndDate', CAST(deleted.EndDate AS VARCHAR), CAST(inserted.EndDate AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE deleted.EndDate <> inserted.EndDate;

    END
END
GO

-- Declare a variable to hold your dynamic SQL
DECLARE @sql NVARCHAR(MAX);

-- List of your tables
DECLARE @tables TABLE (TableName NVARCHAR(128));
INSERT INTO @tables (TableName)
VALUES 
    ('PNOColor'), 
    ('PNOUpholstery'), 
    ('PNOOptions');

-- Cursor to iterate through the table names
DECLARE table_cursor CURSOR FOR 
SELECT TableName FROM @tables;

OPEN table_cursor;
DECLARE @tableName NVARCHAR(128);

FETCH NEXT FROM table_cursor INTO @tableName;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Generate the dynamic SQL for creating the trigger
    SET @sql = N'CREATE TRIGGER [dbo].[trg_' + @tableName + '_InsertUpdate] 
ON [dbo].[' + @tableName + ']
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '''',
            PNOID, 
            ''' + @tableName + ''', 
            GETDATE(), 
            ''Insert'',
            ''ID'', 
            '''',
            ID
        FROM inserted;
    END
    
    -- Log Updates for all columns
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '''', CAST(inserted.PNOID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''RuleName'', deleted.RuleName, inserted.RuleName
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE ISNULL(deleted.RuleName, 0.00) <> ISNULL(inserted.RuleName, 0.00)
        UNION ALL
        SELECT '''', CAST(inserted.PNOID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''EndDate'', CAST(deleted.EndDate AS VARCHAR), CAST(inserted.EndDate AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.ID = deleted.ID WHERE deleted.EndDate <> inserted.EndDate;
    END
END';

    -- Execute the dynamic SQL
    EXEC sp_executesql @sql;

    -- Move to the next table
    FETCH NEXT FROM table_cursor INTO @tableName;
END

-- Cleanup
CLOSE table_cursor;
DEALLOCATE table_cursor;
GO


-- Declare a variable to hold your dynamic SQL
DECLARE @sql NVARCHAR(MAX);

-- List of your tables
DECLARE @tables TABLE (TableName NVARCHAR(128));
INSERT INTO @tables (TableName)
VALUES 
    ('PNOCustom'), 
    ('PNOColorCustom'), 
    ('PNOOptionsCustom'), 
    ('PNOPackageCustom');

-- Cursor to iterate through the table names
DECLARE table_cursor CURSOR FOR 
SELECT TableName FROM @tables;

OPEN table_cursor;
DECLARE @tableName NVARCHAR(128);

FETCH NEXT FROM table_cursor INTO @tableName;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Generate the dynamic SQL for creating the trigger
    SET @sql = N'CREATE TRIGGER [dbo].[trg_' + @tableName + '_InsertUpdate] 
ON [dbo].[' + @tableName + ']
AFTER UPDATE, INSERT
AS
BEGIN
    -- Log Inserts
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '''',
            RelationID, 
            ''' + @tableName + ''', 
            GETDATE(), 
            ''Insert'',
            ''RelationID'', 
            '''',
            RelationID
        FROM inserted;
    END
    
    -- Log Updates for all columns
    ELSE IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO ChangeLog (CountryCode, ChangeCode, ChangeTable, ChangeDate, ChangeType, ChangeField, ChangeFrom, ChangeTo)
        SELECT '''', CAST(inserted.RelationID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''Price'', CAST(deleted.Price AS VARCHAR), CAST(inserted.Price AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.Price, 0) <> ISNULL(inserted.Price, 0)
        UNION ALL
        SELECT '''', CAST(inserted.RelationID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''PriceBeforeTax'', CAST(deleted.PriceBeforeTax AS VARCHAR), CAST(inserted.PriceBeforeTax AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.PriceBeforeTax, 0) <> ISNULL(inserted.PriceBeforeTax, 0)
        UNION ALL
        SELECT '''', CAST(inserted.RelationID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''CustomName'', deleted.CustomName, inserted.CustomName
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE ISNULL(deleted.CustomName, '''') <> ISNULL(inserted.CustomName, '''')
        UNION ALL
        SELECT '''', CAST(inserted.RelationID AS VARCHAR(128)), ''' + @tableName + ''', GETDATE(), ''Update'', ''EndDate'', CAST(deleted.EndDate AS VARCHAR), CAST(inserted.EndDate AS VARCHAR)
        FROM inserted JOIN deleted ON inserted.RelationID = deleted.RelationID WHERE deleted.EndDate <> inserted.EndDate;
    END
END';

    -- Execute the dynamic SQL
    EXEC sp_executesql @sql;

    -- Move to the next table
    FETCH NEXT FROM table_cursor INTO @tableName;
END

-- Cleanup
CLOSE table_cursor;
DEALLOCATE table_cursor;
GO
