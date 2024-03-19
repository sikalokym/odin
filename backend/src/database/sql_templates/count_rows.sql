DECLARE @TableName nvarchar(128), @SchemaName nvarchar(128), @Query nvarchar(max);

-- Table variable to hold the row counts
DECLARE @RowCounts TABLE
(
    TableName nvarchar(128),
    SchemaName nvarchar(128),
    RowsCount int
);

-- Cursor to iterate through the list of tables
DECLARE table_cursor CURSOR FOR 
SELECT t.name, s.name
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE t.name IN ('SupportedCountry', 'Model', 'Engine', 'SalesVersion', 'Steering', 'MarketCode', 'Gearbox', 'Body', 'Color', 'Upholstery', 'Options', 'Package', 'Feature', 'PNO', 'PNOColor', 'PNOUpholstery', 'PNOOptions', 'PNOPackage', 'PNOFeature', 'PNOCustom', 'PNOColorCustom', 'PNOUpholsteryCustom', 'PNOOptionsCustom', 'CustomizationRules', 'VisaFilesPrices');

OPEN table_cursor;

-- Iterate through the cursor
FETCH NEXT FROM table_cursor INTO @TableName, @SchemaName;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Construct the query to get the row count
    SET @Query = 'SELECT ''' + @TableName + ''' AS TableName, ''' + @SchemaName + ''' AS SchemaName, COUNT(*) AS RowsCount FROM [' + @SchemaName + '].[' + @TableName + '];';

    -- Execute the query and store the result in the table variable
    INSERT INTO @RowCounts
    EXEC sp_executesql @Query;

    FETCH NEXT FROM table_cursor INTO @TableName, @SchemaName;
END

CLOSE table_cursor;
DEALLOCATE table_cursor;

-- Return the row counts
SELECT * FROM @RowCounts ORDER BY TableName;

-- Return sum of all rows
SELECT SUM(RowsCount) AS TotalRows FROM @RowCounts;
