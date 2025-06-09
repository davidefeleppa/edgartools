"""
Financial Statement Processor - Multi-Year Financial Data Extractor

This class provides functionality to extract and process multi-year financial statements
from SEC EDGAR filings using the edgartools package's XBRL and XBRLS classes.
"""

from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime, timedelta
import logging

from edgar import Company
from edgar.xbrl import XBRL, XBRLS
from edgar._filings import Filings


class FinancialStatementProcessor:
    """
    A comprehensive processor for extracting multi-year financial statements from SEC filings.
    
    This class handles:
    - Multi-year financial data retrieval
    - Statement standardization across different reporting periods
    - Data merging and consolidation
    - Trend analysis preparation
    - Export capabilities (DataFrame, CSV, JSON)
    
    Attributes:
        company_ticker (str): The ticker symbol of the company
        company (Company): Edgar Company object
        max_years (int): Maximum number of years to retrieve
        statement_types (List[str]): Types of statements to process
        filings_cache (Dict): Cache for retrieved filings
        processed_statements (Dict): Cache for processed statements
    """
    
    def __init__(self, 
                 company_ticker: str, 
                 max_years: int = 5,
                 statement_types: Optional[List[str]] = None,
                 include_quarterly: bool = True):
        """
        Initialize the Financial Statement Processor.
        
        Args:
            company_ticker (str): Company ticker symbol (e.g., 'AAPL', 'MSFT')
            max_years (int): Maximum number of years to retrieve (default: 5)
            statement_types (List[str], optional): Statement types to process
            include_quarterly (bool): Whether to include quarterly filings
        """
        self.company_ticker = company_ticker.upper()
        self.max_years = max_years
        self.include_quarterly = include_quarterly
        
        # Default statement types if not provided
        if statement_types is None:
            self.statement_types = [
                'BalanceSheet',
                'IncomeStatement', 
                'CashFlowStatement',
                'StatementOfEquity',
                'ComprehensiveIncome'
            ]
        else:
            self.statement_types = statement_types
            
        # Initialize company object
        try:
            self.company = Company(self.company_ticker)
        except Exception as e:
            raise ValueError(f"Unable to find company with ticker '{self.company_ticker}': {e}")
            
        # Initialize caches
        self.filings_cache = {}
        self.processed_statements = {}
        
        # Set up logging
        self.logger = logging.getLogger(f"FinancialProcessor-{self.company_ticker}")
        
    def get_annual_filings(self, years: Optional[int] = None) -> Filings:
        """
        Retrieve annual 10-K filings for the specified number of years.
        
        Args:
            years (int, optional): Number of years to retrieve. Uses max_years if not specified.
            
        Returns:
            Filings: Collection of annual filings
        """
        if years is None:
            years = self.max_years
            
        cache_key = f"10-K_{years}"
        if cache_key not in self.filings_cache:
            try:
                filings = self.company.get_filings(form="10-K").head(years)
                self.filings_cache[cache_key] = filings
                self.logger.info(f"Retrieved {len(filings)} annual filings for {self.company_ticker}")
            except Exception as e:
                self.logger.error(f"Error retrieving annual filings: {e}")
                raise
                
        return self.filings_cache[cache_key]
    
    def get_quarterly_filings(self, quarters: int = 12) -> Filings:
        """
        Retrieve quarterly 10-Q filings.
        
        Args:
            quarters (int): Number of quarters to retrieve (default: 12, i.e., 3 years)
            
        Returns:
            Filings: Collection of quarterly filings
        """
        cache_key = f"10-Q_{quarters}"
        if cache_key not in self.filings_cache:
            try:
                filings = self.company.get_filings(form="10-Q").head(quarters)
                self.filings_cache[cache_key] = filings
                self.logger.info(f"Retrieved {len(filings)} quarterly filings for {self.company_ticker}")
            except Exception as e:
                self.logger.error(f"Error retrieving quarterly filings: {e}")
                raise
                
        return self.filings_cache[cache_key]
    
    def extract_multi_year_statements(self, 
                                    filing_type: str = "10-K",
                                    years: Optional[int] = None,
                                    use_stitching: bool = True) -> Dict[str, Any]:
        """
        Extract multi-year financial statements using XBRL/XBRLS.
        
        Args:
            filing_type (str): Type of filing to process ("10-K" or "10-Q")
            years (int, optional): Number of years/periods to extract
            use_stitching (bool): Whether to use XBRLS stitching for multi-period analysis
            
        Returns:
            Dict[str, Any]: Dictionary containing extracted statements by type
        """
        if years is None:
            years = self.max_years
            
        cache_key = f"{filing_type}_{years}_{use_stitching}"
        if cache_key in self.processed_statements:
            return self.processed_statements[cache_key]
            
        try:
            # Get appropriate filings
            if filing_type == "10-K":
                filings = self.get_annual_filings(years)
            elif filing_type == "10-Q":
                filings = self.get_quarterly_filings(years * 4)  # 4 quarters per year
            else:
                raise ValueError(f"Unsupported filing type: {filing_type}")
                
            if len(filings) == 0:
                raise ValueError(f"No {filing_type} filings found for {self.company_ticker}")
                
            statements_data = {}
            
            if use_stitching and len(filings) > 1:
                # Use XBRLS for multi-period stitching
                self.logger.info(f"Using XBRLS stitching for {len(filings)} {filing_type} filings")
                xbrls = XBRLS.from_filings(list(filings))
                stitched_statements = xbrls.statements
                
                # Extract each statement type
                for statement_type in self.statement_types:
                    try:
                        if statement_type == 'BalanceSheet':
                            statement = stitched_statements.balance_sheet()
                        elif statement_type == 'IncomeStatement':
                            statement = stitched_statements.income_statement()
                        elif statement_type == 'CashFlowStatement':
                            statement = stitched_statements.cashflow_statement()
                        elif statement_type == 'StatementOfEquity':
                            statement = stitched_statements.statement_of_equity()
                        elif statement_type == 'ComprehensiveIncome':
                            statement = stitched_statements.comprehensive_income_statement()
                        else:
                            # Try to get any other statement type
                            statement = stitched_statements[statement_type]
                            
                        if statement is not None:
                            statements_data[statement_type] = {
                                'statement': statement,
                                'dataframe': statement.to_dataframe(),
                                'periods': len(statement.periods) if hasattr(statement, 'periods') else 1,
                                'type': 'stitched'
                            }
                            self.logger.info(f"Successfully extracted stitched {statement_type}")
                        else:
                            self.logger.warning(f"No {statement_type} found in stitched statements")
                            
                    except Exception as e:
                        self.logger.error(f"Error extracting stitched {statement_type}: {e}")
                        continue
                        
            else:
                # Process individual filings
                self.logger.info(f"Processing {len(filings)} individual {filing_type} filings")
                individual_statements = {}
                
                for i, filing in enumerate(filings):
                    try:
                        xbrl = XBRL.from_filing(filing)
                        if xbrl is None:
                            self.logger.warning(f"XBRL object is None for filing {i}, skipping.")
                            continue
                        filing_statements = xbrl.statements
                        
                        for statement_type in self.statement_types:
                            if statement_type not in individual_statements:
                                individual_statements[statement_type] = []
                                
                            try:
                                if statement_type == 'BalanceSheet':
                                    statement = filing_statements.balance_sheet()
                                elif statement_type == 'IncomeStatement':
                                    statement = filing_statements.income_statement()
                                elif statement_type == 'CashFlowStatement':
                                    statement = filing_statements.cashflow_statement()
                                elif statement_type == 'StatementOfEquity':
                                    statement = filing_statements.statement_of_equity()
                                elif statement_type == 'ComprehensiveIncome':
                                    statement = filing_statements.comprehensive_income_statement()
                                else:
                                    statement = filing_statements[statement_type]
                                    
                                if statement is not None:
                                    individual_statements[statement_type].append({
                                        'filing_date': filing.filing_date,
                                        'accession_number': filing.accession_no,
                                        'statement': statement,
                                        'dataframe': statement.to_dataframe()
                                    })
                                    
                            except Exception as e:
                                self.logger.warning(f"Error extracting {statement_type} from filing {i}: {e}")
                                continue
                                
                    except Exception as e:
                        self.logger.error(f"Error processing filing {i}: {e}")
                        continue
                        
                # Convert individual statements to organized format
                for statement_type, statements_list in individual_statements.items():
                    if statements_list:
                        statements_data[statement_type] = {
                            'statements': statements_list,
                            'periods': len(statements_list),
                            'type': 'individual'
                        }
                        
            # Cache the results
            self.processed_statements[cache_key] = statements_data
            
            self.logger.info(f"Successfully extracted {len(statements_data)} statement types")
            return statements_data
            
        except Exception as e:
            self.logger.error(f"Error extracting multi-year statements: {e}")
            raise
            
    def get_trend_analysis_data(self, 
                              statement_type: str = 'IncomeStatement',
                              filing_type: str = "10-K",
                              years: Optional[int] = None) -> pd.DataFrame:
        """
        Get financial data prepared for trend analysis.
        
        Args:
            statement_type (str): Type of statement to analyze
            filing_type (str): Type of filing ("10-K" or "10-Q")
            years (int, optional): Number of years to analyze
            
        Returns:
            pd.DataFrame: DataFrame optimized for trend analysis
        """
        statements_data = self.extract_multi_year_statements(filing_type, years, use_stitching=True)
        
        if statement_type not in statements_data:
            raise ValueError(f"Statement type '{statement_type}' not found in extracted data")
            
        statement_info = statements_data[statement_type]
        
        if statement_info['type'] == 'stitched':
            df = statement_info['dataframe'].copy()
            # Additional processing for trend analysis could be added here
            return df
        else:
            # Combine individual statements into a trend DataFrame
            combined_data = []
            for stmt_data in statement_info['statements']:
                df = stmt_data['dataframe'].copy()
                df['filing_date'] = stmt_data['filing_date']
                df['accession_number'] = stmt_data['accession_number']
                combined_data.append(df)
                
            if combined_data:
                return pd.concat(combined_data, ignore_index=True)
            else:
                return pd.DataFrame()
                
    def export_to_csv(self, 
                     output_dir: str = "exports",
                     filing_type: str = "10-K",
                     years: Optional[int] = None) -> Dict[str, str]:
        """
        Export all processed statements to CSV files.
        
        Args:
            output_dir (str): Directory to save CSV files
            filing_type (str): Type of filing to export
            years (int, optional): Number of years to export
            
        Returns:
            Dict[str, str]: Dictionary mapping statement types to file paths
        """
        import os
        
        statements_data = self.extract_multi_year_statements(filing_type, years, use_stitching=True)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = {}
        
        for statement_type, statement_info in statements_data.items():
            try:
                if statement_info['type'] == 'stitched':
                    df = statement_info['dataframe']
                    filename = f"{self.company_ticker}_{statement_type}_{filing_type}_{years}years.csv"
                    filepath = os.path.join(output_dir, filename)
                    df.to_csv(filepath, index=False)
                    exported_files[statement_type] = filepath
                    self.logger.info(f"Exported {statement_type} to {filepath}")
                    
            except Exception as e:
                self.logger.error(f"Error exporting {statement_type}: {e}")
                continue
                
        return exported_files
        
    def get_summary_info(self) -> Dict[str, Any]:
        """
        Get summary information about the processor and available data.
        
        Returns:
            Dict[str, Any]: Summary information
        """
        try:
            annual_filings = self.get_annual_filings()
            quarterly_filings = self.get_quarterly_filings() if self.include_quarterly else []
            
            return {
                'company_ticker': self.company_ticker,
                'company_name': self.company.name,
                'max_years': self.max_years,
                'statement_types': self.statement_types,
                'include_quarterly': self.include_quarterly,
                'available_annual_filings': len(annual_filings),
                'available_quarterly_filings': len(quarterly_filings),
                'latest_annual_filing': annual_filings[0].filing_date if len(annual_filings) > 0 else None,
                'latest_quarterly_filing': quarterly_filings[0].filing_date if len(quarterly_filings) > 0 else None,
                'cached_statements': list(self.processed_statements.keys())
            }
        except Exception as e:
            self.logger.error(f"Error generating summary info: {e}")
            return {'error': str(e)}
            
    def clear_cache(self):
        """Clear all cached data to free memory."""
        self.filings_cache.clear()
        self.processed_statements.clear()
        self.logger.info("Cache cleared")
        
    def __repr__(self) -> str:
        return f"FinancialStatementProcessor(ticker='{self.company_ticker}', max_years={self.max_years})"
        
    def __str__(self) -> str:
        summary = self.get_summary_info()
        return (f"Financial Statement Processor for {summary.get('company_name', self.company_ticker)}\n"
                f"Max Years: {self.max_years}\n"
                f"Statement Types: {len(self.statement_types)}\n"
                f"Annual Filings Available: {summary.get('available_annual_filings', 'Unknown')}\n"
                f"Quarterly Filings Available: {summary.get('available_quarterly_filings', 'Unknown')}")
