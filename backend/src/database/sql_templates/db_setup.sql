-- Create the SupportedCountry table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SupportedCountry')
CREATE TABLE SupportedCountry (
    Code VARCHAR(12) PRIMARY KEY,
    CountryName VARCHAR(255)
);

-- Insert a new row into the SupportedCountry table
-- INSERT INTO SupportedCountry (Code, CountryName)
-- VALUES 
-- ('212', 'Belgium'),
-- ('213', 'France'),
-- ('219', 'Ireland'),
-- ('221', 'United Kingdom'),
-- ('223', 'Italy'),
-- ('224', 'Spain'),
-- ('231', 'Germany'),
-- ('232', 'Switzerland'),
-- ('233', 'Austria');

-- Create the Model table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Model')
CREATE TABLE Model (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the Engine table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Engine')
CREATE TABLE Engine (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CustomName NVARCHAR(MAX),
    Performance VARCHAR(255),
    EngineCategory VARCHAR(255),
    EngineType VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the SalesVersion table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SalesVersion')
CREATE TABLE SalesVersion (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the Gearbox table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Gearbox')
CREATE TABLE Gearbox (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT
);

-- Create the Steering table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Steering')
CREATE TABLE Steering (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the MarketCode table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MarketCode')
CREATE TABLE MarketCode (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the Body table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Body')
CREATE TABLE Body (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the Color table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Color')
CREATE TABLE Color (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the Upholstery table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Upholstery')
CREATE TABLE Upholstery (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the Options table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Options')
CREATE TABLE Options (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the Package table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Package')
CREATE TABLE Package(
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the Feature table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Feature')
CREATE TABLE Feature(
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT
);

-- Create the PNO table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNO')
CREATE TABLE PNO (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    Model VARCHAR(12),
    Engine VARCHAR(12),
    SalesVersion VARCHAR(12),
    Steering VARCHAR(12),
    Gearbox VARCHAR(12),
    Body VARCHAR(12),
    MarketCode VARCHAR(12),
    CountryCode VARCHAR(12),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the PNOColor table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOColor')
CREATE TABLE PNOColor (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    Code VARCHAR(12),
    RuleName VARCHAR(12),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the PNOUpholstery table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOUpholstery')
CREATE TABLE PNOUpholstery (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    Code VARCHAR(12),
    RuleName VARCHAR(12),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the PNOOptions table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOOptions')
CREATE TABLE PNOOptions (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    Code VARCHAR(12),
    RuleName VARCHAR(12),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the PNOPackage table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOPackage')
CREATE TABLE PNOPackage (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    Code VARCHAR(12),
    Title VARCHAR(255),
    RuleCode VARCHAR(12),
    RuleType VARCHAR(12),
    RuleName VARCHAR(12),
    RuleBase VARCHAR(12),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the PNOFeature table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOFeature')
CREATE TABLE PNOFeature (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    Code VARCHAR(12),
    Special CHAR(1),
    Reference VARCHAR(255),
    Options VARCHAR(12),
    RuleName VARCHAR(12),
    CustomName NVARCHAR(MAX),
    CustomCategory VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the PNOCustomFeature table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOCustomFeature')
CREATE TABLE PNOCustomFeature (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    Code VARCHAR(12),
    CustomName NVARCHAR(MAX),
    CustomCategory VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the custom table of PNOs
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOCustom')
CREATE TABLE PNOCustom (
    RelationID UNIQUEIDENTIFIER,
    Price DECIMAL(19,2),
    PriceBeforeTax DECIMAL(19,2),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (RelationID) REFERENCES PNO(ID)
);

-- Create the custom table of PNOColor table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOColorCustom')
CREATE TABLE PNOColorCustom (
    RelationID UNIQUEIDENTIFIER,
    Price DECIMAL(19,2),
    PriceBeforeTax DECIMAL(19,2),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (RelationID) REFERENCES PNOColor(ID)
);

-- Create the custom table of PNOUpholstery table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOUpholsteryCustom')
CREATE TABLE PNOUpholsteryCustom (
    RelationID UNIQUEIDENTIFIER,
    Price DECIMAL(19,2),
    PriceBeforeTax DECIMAL(19,2),
    CustomName NVARCHAR(MAX),
    CustomCategory VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (RelationID) REFERENCES PNOUpholstery(ID)
);

-- Create the custom table of PNOOptions table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOOptionsCustom')
CREATE TABLE PNOOptionsCustom (
    RelationID UNIQUEIDENTIFIER,
    Price DECIMAL(19,2),
    PriceBeforeTax DECIMAL(19,2),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (RelationID) REFERENCES PNOOptions(ID)
);

-- Create the custom table of PNOPackage table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PNOPackageCustom')
CREATE TABLE PNOPackageCustom (
    RelationID UNIQUEIDENTIFIER,
    Price DECIMAL(19,2),
    PriceBeforeTax DECIMAL(19,2),
    CustomName NVARCHAR(MAX),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (RelationID) REFERENCES PNOPackage(ID)
);

-- Create the customization rules table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CustomizationRules')
CREATE TABLE CustomizationRules (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    PNOID UNIQUEIDENTIFIER,
    RuleCode CHAR(3),
    RuleName VARCHAR(100),
    ItemCode VARCHAR(12),
    FeatureCode VARCHAR(12),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (PNOID) REFERENCES PNO(ID)
);

-- Create the VisaFiles table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'VisaFiles')
CREATE TABLE VisaFiles (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Active NVARCHAR(255),
    SalesOrg NVARCHAR(255),
    DistrCh NVARCHAR(255),
    PriceList NVARCHAR(255),
    DealerGroup NVARCHAR(255),
    Country NVARCHAR(255),
    CarType NVARCHAR(255),
    Engine NVARCHAR(255),
    SalesVersion NVARCHAR(255),
    Body NVARCHAR(255),
    Gearbox NVARCHAR(255),
    Steering NVARCHAR(255),
    MarketCode NVARCHAR(255),
    ModelYear NVARCHAR(255),
    StructureWeek NVARCHAR(255),
    DateFrom NVARCHAR(255),
    DateTo NVARCHAR(255),
    Currency NVARCHAR(255),
    Color NVARCHAR(255),
    Options NVARCHAR(255),
    Upholstery NVARCHAR(255),
    Package NVARCHAR(255),
    SNote NVARCHAR(255),
    MSRP NVARCHAR(255),
    TAX2 NVARCHAR(255),
    VAT NVARCHAR(255),
    TAX1 NVARCHAR(255),
    PriceBeforeTax NVARCHAR(255),
    WholesalePrice NVARCHAR(255),
    TransferPrice NVARCHAR(255),
    VisaFile NVARCHAR(255),
    CountryCode VARCHAR(12),
    LoadingDate DATETIME DEFAULT GETDATE()
);

-- Create the sales channel table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SalesChannel')
CREATE TABLE SalesChannel (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    Code VARCHAR(12),
    ChannelName NVARCHAR(MAX),
    Comment NVARCHAR(MAX),
    CountryCode VARCHAR(12),
    DateFrom DATE,
    DateTo DATE,
    ModelYear NVARCHAR(255),
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the discounts table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Discount')
CREATE TABLE Discount (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    ChannelID UNIQUEIDENTIFIER,
    DiscountPercentage DECIMAL(19,2),
    RetailPrice DECIMAL(19,2),
    WholesalePrice DECIMAL(19,2),
    PNOSpecific BIT,
    AffectedVisaFile NVARCHAR(MAX),
    FOREIGN KEY (ChannelID) REFERENCES SalesChannel(ID)
);

-- Create the CustomLocalOption table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CustomLocalOption')
CREATE TABLE CustomLocalOption (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    ChannelID UNIQUEIDENTIFIER,
    FeatureCode VARCHAR(12),
    FeatureRetailPrice DECIMAL(19,2),
    FeatureWholesalePrice DECIMAL(19,2),
    AffectedVisaFile NVARCHAR(MAX),
    DateFrom DATE,
    DateTo DATE,
    FOREIGN KEY (ChannelID) REFERENCES SalesChannel(ID)
);

-- Create the change log table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ChangeLog')
CREATE TABLE ChangeLog (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    CountryCode VARCHAR(12),
    ChangeCode VARCHAR(128),
    ChangeTable VARCHAR(128),
    ChangeDate DATETIME, 
    ChangeType VARCHAR(100), -- Add, Update, Delete
    ChangeField VARCHAR(100),
    ChangeFrom NVARCHAR(MAX),
    ChangeTo NVARCHAR(MAX)
);

-- Create the log table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DataQualityLog')
CREATE TABLE DataQualityLog (
    ID UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
    CountryCode VARCHAR(12),
    LogDate DATETIME,
    LogType VARCHAR(100),
    LogMessage NVARCHAR(MAX),
    LoadingDate DATETIME DEFAULT GETDATE()
);
