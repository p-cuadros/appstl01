-- Create Accounts Table
CREATE TABLE Accounts (
    AccountID INT IDENTITY(1,1) PRIMARY KEY,
    AccountNumber VARCHAR(20) NOT NULL UNIQUE,
    Balance DECIMAL(18,2) NOT NULL,
    AccountType VARCHAR(50) NOT NULL,
    CreatedDate DATETIME DEFAULT GETDATE(),
    LastUpdated DATETIME DEFAULT GETDATE()
);

-- Insert 10 sample records
INSERT INTO Accounts (AccountNumber, Balance, AccountType)
VALUES 
    ('ACC-10001', 5250.75, 'Savings'),
    ('ACC-10002', 12500.00, 'Checking'),
    ('ACC-10003', 35000.50, 'Investment'),
    ('ACC-10004', 750.25, 'Savings'),
    ('ACC-10005', 27800.00, 'Retirement'),
    ('ACC-10006', 3600.50, 'Checking'),
    ('ACC-10007', 105000.75, 'Investment'),
    ('ACC-10008', 950.00, 'Savings'),
    ('ACC-10009', 18750.50, 'Retirement'),
    ('ACC-10010', 4200.00, 'Checking');

-- Optional: Create a view for account summaries
CREATE VIEW AccountSummary AS
SELECT 
    AccountType,
    COUNT(*) AS AccountCount,
    SUM(Balance) AS TotalBalance,
    AVG(Balance) AS AverageBalance,
    MIN(Balance) AS MinimumBalance,
    MAX(Balance) AS MaximumBalance
FROM Accounts
GROUP BY AccountType;
