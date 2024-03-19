-- Create the SupportedCountry table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SupportedCountry')
CREATE TABLE SupportedCountry (
    Code VARCHAR(12) PRIMARY KEY,
    CountryName VARCHAR(255)
);

-- Insert a new row into the SupportedCountry table
INSERT INTO SupportedCountry (Code, CountryName)
VALUES ('231', 'Germany');

-- Create the Model table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Model')
CREATE TABLE Model (
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CountryText VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the Engine table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Engine')
CREATE TABLE Engine (
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CountryText VARCHAR(255),
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
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CountryText VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (CountryCode) REFERENCES SupportedCountry(Code)
);

-- Create the Gearbox table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Gearbox')
CREATE TABLE Gearbox (
    Code VARCHAR(12),
    Special CHAR(1),
    ShortText VARCHAR(255),
    MarketText VARCHAR(255),
    CountryCode VARCHAR(12),
    CountryText VARCHAR(255),
    StartDate INT,
    EndDate INT
);

-- Create the Steering table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Steering')
CREATE TABLE Steering (
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

-- ['PackageCode', 'Text', 'Code', 'Type', 'Rule', 'Base', 'StartDate', 'EndDate'],
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
    CustomName VARCHAR(255),
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
    CustomName VARCHAR(255),
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
    CustomName VARCHAR(255),
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
    CustomName VARCHAR(255),
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
    CustomName VARCHAR(255),
    StartDate INT,
    EndDate INT,
    FOREIGN KEY (RelationID) REFERENCES PNOOptions(ID)
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

-- Create the customization rules table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'VisaFilesPrices')
CREATE TABLE VisaFilesPrices (
    Model VARCHAR(12),
    Engine VARCHAR(12),
    SalesVersion VARCHAR(12),
    Body VARCHAR(12),
    Gearbox VARCHAR(12),
    Steering VARCHAR(12),
    MarketCode VARCHAR(12),
    ModelYear INT,
    StartDate INT,
    EndDate INT,
    Color VARCHAR(12),
    Options VARCHAR(12),
    Upholstery VARCHAR(12),
    Package VARCHAR(12),
    Price DECIMAL(19,2),
    PriceBeforeTax DECIMAL(19,2),
);
