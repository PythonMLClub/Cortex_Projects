/*--
• Database, schema, warehouse, and stage creation
--*/

USE ROLE accountadmin;

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE accountadmin;

select current_user();

-- TODO: Replace <your_user> with your username
GRANT ROLE accountadmin TO USER CORTEXAGENTAPI;

GRANT CREATE DATABASE ON ACCOUNT TO ROLE accountadmin;

USE ROLE accountadmin;

-- Create demo database
CREATE OR REPLACE DATABASE cortex_agent_db;

-- Create schema
CREATE OR REPLACE SCHEMA cortex_agent_db.cortex_agent_schema;

GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE accountadmin;

-- Create warehouse
CREATE OR REPLACE WAREHOUSE cortex_agent_wh
    WAREHOUSE_SIZE = 'large'
    WAREHOUSE_TYPE = 'standard'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
COMMENT = 'Warehouse for Cortex agent';

GRANT USAGE ON WAREHOUSE cortex_agent_wh TO ROLE accountadmin;
GRANT OPERATE ON WAREHOUSE cortex_agent_wh TO ROLE accountadmin;

GRANT OWNERSHIP ON SCHEMA cortex_agent_db.cortex_agent_schema TO ROLE accountadmin;
GRANT OWNERSHIP ON DATABASE cortex_agent_db TO ROLE accountadmin;


-- Use the created warehouse
USE WAREHOUSE cortex_agent_wh;

USE DATABASE cortex_agent_db;
USE SCHEMA cortex_agent_db.cortex_agent_schema;

GRANT USAGE ON DATABASE cortex_agent_db TO ROLE accountadmin;
GRANT USAGE ON SCHEMA cortex_agent_schema TO ROLE accountadmin;

-----------------------------------------------------

-- Create stage for raw data
CREATE OR REPLACE STAGE agent_data DIRECTORY = (ENABLE = TRUE);

LIST @CORTEX_AGENT_DB.CORTEX_AGENT_SCHEMA.agent_data;


list @CORTEX_AGENT_DB.CORTEX_AGENT_SCHEMA.agent_data/business_sam.yaml;

-------------------property table-------------------------------

CREATE OR REPLACE TABLE cortex_agent_db.cortex_agent_schema.property_data (
    PropertyType STRING,           
    State STRING,  
    LandUseCode VARCHAR,
    PrimaryAddress STRING,         
    PrimaryCity STRING,            
    PrimaryZIP STRING,             
    MailingAddress STRING,         
    MailingCity STRING,            
    MailingZIP STRING,             
    StatisticalArea STRING,        
    AcreSize VARCHAR,                
    OwnerName STRING,              
    Zoning STRING,                 
    TaxAmount VARCHAR        
);

COPY INTO cortex_agent_db.cortex_agent_schema.property_data
FROM @agent_data
FILES = ('property_table.csv')
FILE_FORMAT = (
    TYPE=CSV,
    SKIP_HEADER=1,  -- ✅ Ensures header row is ignored
    FIELD_DELIMITER=',',
    TRIM_SPACE=FALSE,
    FIELD_OPTIONALLY_ENCLOSED_BY='NONE',
    REPLACE_INVALID_CHARACTERS=TRUE,
    DATE_FORMAT=AUTO,
    TIME_FORMAT=AUTO,
    TIMESTAMP_FORMAT=AUTO,
    EMPTY_FIELD_AS_NULL=FALSE,  -- ✅ Corrected missing comma
    ERROR_ON_COLUMN_COUNT_MISMATCH=FALSE  -- ✅ Corrected syntax
)
ON_ERROR=CONTINUE
FORCE = TRUE;

select * from property_data;

SELECT COUNT(*) FROM cortex_agent_db.cortex_agent_schema.property_data;


CREATE OR REPLACE VIEW cortex_agent_db.cortex_agent_schema.property_data_view AS
SELECT *
FROM cortex_agent_db.cortex_agent_schema.property_data;

select count(*) from property_data_view;


------------------------business table------------------------------

CREATE TABLE cortex_agent_db.cortex_agent_schema.business_data (
    company VARCHAR,
    telenum VARCHAR,
    zipcode VARCHAR,
    sic_code VARCHAR,
    noofemployees VARCHAR,
    totalnoofemp INT,
    status VARCHAR,
    revenue VARCHAR,
    firstname VARCHAR,
    lastname VARCHAR,
    excityname VARCHAR,
    excountyname VARCHAR,
    resibusi VARCHAR,
    statecode VARCHAR,
    comp_id VARCHAR,
    areacode VARCHAR
);

COPY INTO cortex_agent_db.cortex_agent_schema.business_data
FROM @agent_data
FILES = ('business_data.csv')
FILE_FORMAT = (
    TYPE=CSV,
    SKIP_HEADER=1,  -- ✅ Ensures header row is ignored
    FIELD_DELIMITER=',',
    TRIM_SPACE=FALSE,
    FIELD_OPTIONALLY_ENCLOSED_BY='NONE',
    REPLACE_INVALID_CHARACTERS=TRUE,
    DATE_FORMAT=AUTO,
    TIME_FORMAT=AUTO,
    TIMESTAMP_FORMAT=AUTO,
    EMPTY_FIELD_AS_NULL=FALSE,  -- ✅ Corrected missing comma
    ERROR_ON_COLUMN_COUNT_MISMATCH=FALSE  -- ✅ Corrected syntax
)
ON_ERROR=CONTINUE
FORCE = TRUE;


select * from business_data;

SELECT COUNT(*) FROM cortex_agent_db.cortex_agent_schema.business_data;

CREATE OR REPLACE VIEW cortex_agent_db.cortex_agent_schema.business_data_view AS
SELECT *
FROM cortex_agent_db.cortex_agent_schema.business_data;

SELECT COUNT(*) FROM cortex_agent_db.cortex_agent_schema.business_data_view;

----------------------farm table---------------------------------------

CREATE OR REPLACE TABLE farm_data (
    uniqueid VARCHAR,
    farmid VARCHAR,
    Name_Availablity_Code VARCHAR,
    Telephone_Availablity_Code VARCHAR,
    address_Availablity_Code VARCHAR,
    crop_Availablity_Code VARCHAR,
    email_Availablity_Code VARCHAR,
    livestock_Availablity_Code VARCHAR,
    Crops_Name VARCHAR,
    LiveStock_name VARCHAR,
    state VARCHAR,
    city VARCHAR,
    zipcode VARCHAR,
    latitude VARCHAR,
    longitude VARCHAR,
    Owner_operator_type VARCHAR,
    rural_flag VARCHAR,
    total_farm_exact_acres VARCHAR
);

COPY INTO cortex_agent_db.cortex_agent_schema.farm_data
FROM @agent_data
FILES = ('farm_data.csv')
FILE_FORMAT = (
    TYPE=CSV,
    SKIP_HEADER=1,  -- ✅ Ensures header row is ignored
    FIELD_DELIMITER=',',
    TRIM_SPACE=FALSE,
    FIELD_OPTIONALLY_ENCLOSED_BY='NONE',
    REPLACE_INVALID_CHARACTERS=TRUE,
    DATE_FORMAT=AUTO,
    TIME_FORMAT=AUTO,
    TIMESTAMP_FORMAT=AUTO,
    EMPTY_FIELD_AS_NULL=FALSE,  -- ✅ Corrected missing comma
    ERROR_ON_COLUMN_COUNT_MISMATCH=FALSE  -- ✅ Corrected syntax
)
ON_ERROR=CONTINUE
FORCE = TRUE;


select * from farm_data;

SELECT COUNT(*) FROM cortex_agent_db.cortex_agent_schema.farm_data;

CREATE OR REPLACE VIEW cortex_agent_db.cortex_agent_schema.farm_data_view AS
SELECT *
FROM cortex_agent_db.cortex_agent_schema.farm_data;

SELECT COUNT(*) FROM cortex_agent_db.cortex_agent_schema.farm_data_view;


--------------------------------------------------------------------


----------------------------------

-- use role accountadmin;

-- ALTER USER CORTEXOPENAI SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsSzdwQYGhIBfWfPdbMrl
-- 0gWTe85di5jNOGCgO9DT4Dzif321L+0QqQ0BE6B0fU8qiRoMsHbuhK+hyMqcP4w3
-- HbhpKiJEu0axy22qj+SY39EyjcBltCRhq+vXPfHrvsvWbbQI2ATz8ul1gaXBSqlB
-- 3Kmyzn6ungHeazcAoeZitMq4mYYUPdialAmyroadbAXnTym0jAbEwNtPkD9E4NpW
-- ND3kHm41CjJ9YW1JYsF9hihntyW++LDpIQXLasq82qsT9SKs+XnQ05YYhcCHlIug
-- PcqOCLRI83kJUYxgvYEe1v1Lp3XUJabzbsOrRyxisWmXcvyjq+vn99TYLmWL6yi9
-- DQIDAQAB';


-- SHOW USERS LIKE 'CORTEXOPENAI';

-- DESC USER CORTEXOPENAI;

-- SHOW GRANTS TO USER CORTEXOPENAI;

-- SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), CURRENT_VERSION();

-- SHOW PARAMETERS LIKE '%CORTEX%';


