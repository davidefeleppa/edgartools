"""
Insider Trading Monitor Class

This module provides comprehensive monitoring and analysis of insider trading activities
using SEC Form 3, 4, and 5 filings accessed through the edgartools package.

Author: GitHub Copilot
Created: June 8, 2025
"""

from typing import List, Dict, Optional, Union, Tuple
from datetime import datetime, timedelta, date
import pandas as pd
from dataclasses import dataclass
from edgar import Company, get_filings, set_identity
from edgar.ownership import Ownership, Form4
import warnings


@dataclass
class InsiderTransaction:
    """Data class representing a single insider transaction."""
    company_ticker: str
    company_name: str
    filing_date: Union[datetime, date]
    transaction_date: Union[datetime, date]
    insider_name: str
    insider_title: str
    transaction_code: str
    security_title: str
    shares: float
    price_per_share: float
    transaction_value: float
    ownership_type: str
    shares_owned_after: float
    filing_url: str


@dataclass
class InsiderAlert:
    """Data class representing an insider trading alert."""
    alert_type: str
    company_ticker: str
    insider_name: str
    transaction_value: float
    threshold_exceeded: str
    alert_timestamp: datetime
    details: Dict


class InsiderTradingMonitor:
    """
    A comprehensive class for monitoring and analyzing insider trading activities.
    
    This class provides functionality to:
    - Track insider transactions for specific companies or across the market
    - Set up alerts for significant trading activities
    - Analyze insider trading patterns and trends
    - Generate reports and visualizations
    
    Attributes:
        user_agent (str): User identification for SEC requests
        companies (List[str]): List of company tickers to monitor
        alert_thresholds (Dict): Configuration for trading alerts
        cache_data (bool): Whether to cache retrieved data
        data_cache (Dict): Internal cache for retrieved data
    """
    
    def __init__(self, user_agent: str, companies: Optional[List[str]] = None,
                 cache_data: bool = True):
        """
        Initialize the Insider Trading Monitor.
        
        Args:
            user_agent (str): Email address for SEC identification
            companies (Optional[List[str]]): List of company tickers to monitor
            cache_data (bool): Whether to enable data caching
        """
        self.user_agent = user_agent
        self.companies = companies or []
        self.cache_data = cache_data
        self.data_cache = {}
        self.alert_thresholds = {
            'large_transaction': 1000000,  # $1M
            'unusual_volume': 0.05,  # 5% of shares outstanding
            'multiple_transactions': 3,  # 3+ transactions in a day
            'c_suite_threshold': 100000  # $100K for C-suite executives
        }
        
        # Set SEC identity
        set_identity(user_agent)
        
    def add_company(self, ticker: str) -> None:
        """Add a company to the monitoring list."""
        if ticker not in self.companies:
            self.companies.append(ticker.upper())
            
    def remove_company(self, ticker: str) -> None:
        """Remove a company from the monitoring list."""
        ticker = ticker.upper()
        if ticker in self.companies:
            self.companies.remove(ticker)
            
    def set_alert_threshold(self, threshold_type: str, value: Union[int, float]) -> None:
        """
        Set alert thresholds for different types of insider activities.
        
        Args:
            threshold_type (str): Type of threshold ('large_transaction', 
                                'unusual_volume', 'multiple_transactions', 'c_suite_threshold')
            value (Union[int, float]): Threshold value
        """
        if threshold_type in self.alert_thresholds:
            self.alert_thresholds[threshold_type] = value
        else:
            raise ValueError(f"Unknown threshold type: {threshold_type}")
    
    def get_insider_filings(self, ticker: Optional[str] = None, 
                           days_back: int = 30,
                           form_types: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retrieve insider filings for specified companies and time period.
        
        Args:
            ticker (str): Specific company ticker (if None, uses all monitored companies)
            days_back (int): Number of days to look back
            form_types (List[str]): Form types to retrieve (default: ["3", "4", "5"])
            
        Returns:
            pd.DataFrame: DataFrame containing insider filing information
        """
        if form_types is None:
            form_types = ["3", "4", "5"]
            
        companies_to_check = [ticker.upper()] if ticker else self.companies
        
        if not companies_to_check:
            raise ValueError("No companies specified for monitoring")
        
        all_transactions = []
        
        for company_ticker in companies_to_check:
            cache_key = f"{company_ticker}_{days_back}_{'-'.join(form_types)}"
            
            # Check cache first
            if self.cache_data and cache_key in self.data_cache:
                cached_data = self.data_cache[cache_key]
                if (datetime.now() - cached_data['timestamp']).seconds < 3600:  # 1 hour cache
                    all_transactions.extend(cached_data['data'])
                    continue

            try:
                company = Company(company_ticker)
                
                # Get insider filings
                filings = company.get_filings(form=form_types)
                
                # Filter by date
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                # Convert cutoff_date to date for comparison
                recent_filings = []
                for f in filings:
                    if hasattr(f, 'filing_date'):
                        filing_date = f.filing_date
                        # Convert filing_date to datetime if it's a date
                        if isinstance(filing_date, date) and not isinstance(filing_date, datetime):
                            filing_date = datetime.combine(filing_date, datetime.min.time())
                        elif isinstance(filing_date, str):
                            try:
                                filing_date = datetime.strptime(filing_date, '%Y-%m-%d')
                            except:
                                continue
                        
                        if filing_date >= cutoff_date:
                            recent_filings.append(f)
                
                company_transactions = []
                
                for filing in recent_filings:
                    try:
                        ownership = filing.obj()
                        if isinstance(ownership, (Ownership, Form4)):
                            transactions = self._extract_transactions(ownership, company_ticker)
                            company_transactions.extend(transactions)
                    except Exception as e:
                        warnings.warn(f"Error processing filing {filing.accession_number}: {str(e)}")
                        continue
                
                # Cache the results
                if self.cache_data:
                    self.data_cache[cache_key] = {
                        'data': company_transactions,
                        'timestamp': datetime.now()
                    }
                
                all_transactions.extend(company_transactions)
                
            except Exception as e:
                warnings.warn(f"Error retrieving data for {company_ticker}: {str(e)}")
                continue
        
        return pd.DataFrame([t.__dict__ for t in all_transactions])
    
    def _extract_transactions(self, ownership: Ownership, ticker: str) -> List[InsiderTransaction]:
        """
        Extract transaction details from ownership filing.
        
        Args:
            ownership: Ownership object from edgar
            ticker (str): Company ticker
            
        Returns:
            List[InsiderTransaction]: List of transaction objects
        """
        transactions = []
        
        try:
            company_name = getattr(ownership, 'company_name', ticker)
            filing_date = getattr(ownership, 'filing_date', datetime.now().date())
            
            # Convert filing_date to datetime if it's a date
            if isinstance(filing_date, date) and not isinstance(filing_date, datetime):
                filing_date = datetime.combine(filing_date, datetime.min.time())
            
            insider_name = getattr(ownership.reporting_owner, 'name', 'Unknown') if hasattr(ownership, 'reporting_owner') else 'Unknown'
            insider_title = getattr(ownership.reporting_owner, 'title', 'Unknown') if hasattr(ownership, 'reporting_owner') else 'Unknown'
            
            # Handle different form types
            if hasattr(ownership, 'transactions'):
                # Form 4 and 5 - actual transactions
                for transaction in ownership.transactions:
                    transaction_date = getattr(transaction, 'transaction_date', filing_date)
                    if isinstance(transaction_date, date) and not isinstance(transaction_date, datetime):
                        transaction_date = datetime.combine(transaction_date, datetime.min.time())
                    
                    trans = InsiderTransaction(
                        company_ticker=ticker,
                        company_name=company_name,
                        filing_date=filing_date,
                        transaction_date=transaction_date,
                        insider_name=insider_name,
                        insider_title=insider_title,
                        transaction_code=getattr(transaction, 'transaction_code', 'Unknown'),
                        security_title=getattr(transaction, 'security_title', 'Common Stock'),
                        shares=float(getattr(transaction, 'shares', 0)),
                        price_per_share=float(getattr(transaction, 'price_per_share', 0)),
                        transaction_value=float(getattr(transaction, 'shares', 0)) * 
                                        float(getattr(transaction, 'price_per_share', 0)),
                        ownership_type=getattr(transaction, 'ownership_type', 'Direct'),
                        shares_owned_after=float(getattr(transaction, 'shares_owned_after', 0)),
                        filing_url=f"https://www.sec.gov/Archives/edgar/data/{getattr(ownership, 'cik', '')}/"
                    )
                    transactions.append(trans)
            
            elif hasattr(ownership, 'holdings'):
                # Form 3 - initial holdings
                for holding in ownership.holdings:
                    trans = InsiderTransaction(
                        company_ticker=ticker,
                        company_name=company_name,
                        filing_date=filing_date,
                        transaction_date=filing_date,
                        insider_name=insider_name,
                        insider_title=insider_title,
                        transaction_code='H',  # Holding
                        security_title=getattr(holding, 'security_title', 'Common Stock'),
                        shares=float(getattr(holding, 'shares', 0)),
                        price_per_share=0.0,  # Form 3 doesn't have transaction prices
                        transaction_value=0.0,
                        ownership_type=getattr(holding, 'ownership_type', 'Direct'),
                        shares_owned_after=float(getattr(holding, 'shares', 0)),
                        filing_url=f"https://www.sec.gov/Archives/edgar/data/{getattr(ownership, 'cik', '')}/"
                    )
                    transactions.append(trans)
                    
        except Exception as e:
            warnings.warn(f"Error extracting transaction details: {str(e)}")
            
        return transactions
    
    def analyze_insider_patterns(self, ticker: Optional[str] = None, 
                               days_back: int = 90) -> Dict:
        """
        Analyze insider trading patterns for specified companies.
        
        Args:
            ticker (str): Specific company ticker (if None, analyzes all monitored companies)
            days_back (int): Number of days to analyze
            
        Returns:
            Dict: Analysis results including trends, patterns, and statistics
        """
        df = self.get_insider_filings(ticker, days_back)
        
        if df.empty:
            return {"error": "No insider trading data found"}
        
        analysis = {
            "summary": {
                "total_transactions": len(df),
                "unique_insiders": df['insider_name'].nunique(),
                "unique_companies": df['company_ticker'].nunique(),
                "total_value": df['transaction_value'].sum(),
                "date_range": {
                    "start": df['filing_date'].min(),
                    "end": df['filing_date'].max()
                }
            },
            "by_transaction_type": df.groupby('transaction_code').agg({
                'shares': 'sum',
                'transaction_value': 'sum',
                'insider_name': 'count'
            }).to_dict(),
            "by_company": df.groupby('company_ticker').agg({
                'transaction_value': ['sum', 'mean', 'count']
            }).to_dict(),
            "by_insider": df.groupby('insider_name').agg({
                'transaction_value': ['sum', 'mean', 'count'],
                'company_ticker': lambda x: list(set(x))
            }).to_dict(),
            "large_transactions": df[
                df['transaction_value'] > self.alert_thresholds['large_transaction']
            ].to_dict('records'),
            "recent_activity": df.sort_values('filing_date', ascending=False).head(10).to_dict('records')
        }
        
        return analysis
    
    def generate_alerts(self, ticker: Optional[str] = None, 
                       days_back: int = 7) -> List[InsiderAlert]:
        """
        Generate alerts based on recent insider trading activity.
        
        Args:
            ticker (str): Specific company ticker (if None, checks all monitored companies)
            days_back (int): Number of days to check for alert conditions
            
        Returns:
            List[InsiderAlert]: List of generated alerts
        """
        df = self.get_insider_filings(ticker, days_back)
        alerts = []
        
        if df.empty:
            return alerts
        
        # Large transaction alerts
        large_transactions = df[df['transaction_value'] > self.alert_thresholds['large_transaction']]
        for _, transaction in large_transactions.iterrows():
            alert = InsiderAlert(
                alert_type="large_transaction",
                company_ticker=transaction['company_ticker'],
                insider_name=transaction['insider_name'],
                transaction_value=transaction['transaction_value'],
                threshold_exceeded=f"${self.alert_thresholds['large_transaction']:,.0f}",
                alert_timestamp=datetime.now(),
                details=transaction.to_dict()
            )
            alerts.append(alert)
        
        # C-suite executive alerts (lower threshold)
        c_suite_keywords = ['CEO', 'CFO', 'COO', 'CTO', 'President', 'Chairman', 'Director']
        c_suite_transactions = df[
            (df['insider_title'].str.contains('|'.join(c_suite_keywords), case=False, na=False)) &
            (df['transaction_value'] > self.alert_thresholds['c_suite_threshold'])
        ]
        
        for _, transaction in c_suite_transactions.iterrows():
            alert = InsiderAlert(
                alert_type="c_suite_transaction",
                company_ticker=transaction['company_ticker'],
                insider_name=transaction['insider_name'],
                transaction_value=transaction['transaction_value'],
                threshold_exceeded=f"C-Suite ${self.alert_thresholds['c_suite_threshold']:,.0f}",
                alert_timestamp=datetime.now(),
                details=transaction.to_dict()
            )
            alerts.append(alert)
        
        # Multiple transactions by same insider
        insider_counts = df.groupby(['insider_name', 'company_ticker']).size()
        multiple_transactions = insider_counts[
            insider_counts >= self.alert_thresholds['multiple_transactions']
        ]
        
        for (insider, company), count in multiple_transactions.items():
            insider_data = df[(df['insider_name'] == insider) & (df['company_ticker'] == company)]
            total_value = insider_data['transaction_value'].sum()
            
            alert = InsiderAlert(
                alert_type="multiple_transactions",
                company_ticker=company,
                insider_name=insider,
                transaction_value=total_value,
                threshold_exceeded=f"{count} transactions",
                alert_timestamp=datetime.now(),
                details={
                    "transaction_count": count,
                    "total_value": total_value,
                    "transactions": insider_data.to_dict('records')
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def export_data(self, ticker: Optional[str] = None, 
                   days_back: int = 30,
                   file_format: str = 'csv',
                   filename: Optional[str] = None) -> str:
        """
        Export insider trading data to file.
        
        Args:
            ticker (str): Specific company ticker (if None, exports all monitored companies)
            days_back (int): Number of days of data to export
            file_format (str): Export format ('csv', 'excel', 'json')
            filename (str): Custom filename (if None, generates timestamp-based name)
            
        Returns:
            str: Path to exported file
        """
        df = self.get_insider_filings(ticker, days_back)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_suffix = f"_{ticker}" if ticker else "_all_companies"
            filename = f"insider_trading_{timestamp}{company_suffix}"
        
        if file_format.lower() == 'csv':
            filepath = f"{filename}.csv"
            df.to_csv(filepath, index=False)
        elif file_format.lower() == 'excel':
            filepath = f"{filename}.xlsx"
            df.to_excel(filepath, index=False)
        elif file_format.lower() == 'json':
            filepath = f"{filename}.json"
            df.to_json(filepath, orient='records', date_format='iso')
        else:
            raise ValueError("Unsupported file format. Use 'csv', 'excel', or 'json'")
        
        return filepath
    
    def get_summary_statistics(self, ticker: Optional[str] = None, 
                             days_back: int = 30) -> Dict:
        """
        Get summary statistics for insider trading activity.
        
        Args:
            ticker (str): Specific company ticker (if None, analyzes all monitored companies)
            days_back (int): Number of days to analyze
            
        Returns:
            Dict: Summary statistics
        """
        df = self.get_insider_filings(ticker, days_back)
        
        if df.empty:
            return {"error": "No data available for the specified parameters"}
        
        stats = {
            "period": f"{days_back} days",
            "companies_analyzed": df['company_ticker'].nunique(),
            "total_transactions": len(df),
            "unique_insiders": df['insider_name'].nunique(),
            "transaction_value": {
                "total": df['transaction_value'].sum(),
                "mean": df['transaction_value'].mean(),
                "median": df['transaction_value'].median(),
                "std": df['transaction_value'].std(),
                "min": df['transaction_value'].min(),
                "max": df['transaction_value'].max()
            },
            "shares_traded": {
                "total": df['shares'].sum(),
                "mean": df['shares'].mean(),
                "median": df['shares'].median()
            },
            "transaction_codes": df['transaction_code'].value_counts().to_dict(),
            "most_active_insiders": df['insider_name'].value_counts().head(10).to_dict(),
            "most_active_companies": df['company_ticker'].value_counts().head(10).to_dict()
        }
        
        return stats


def example_usage():
    """Example usage of the InsiderTradingMonitor class."""
    
    # Initialize the monitor
    monitor = InsiderTradingMonitor(
        user_agent="your.email@domain.com",
        companies=["AAPL", "MSFT", "GOOGL", "TSLA"]
    )
    
    # Set custom alert thresholds
    monitor.set_alert_threshold('large_transaction', 500000)  # $500K
    monitor.set_alert_threshold('c_suite_threshold', 50000)   # $50K
    
    # Get recent insider filings
    filings_df = monitor.get_insider_filings(days_back=30)
    print(f"Found {len(filings_df)} insider transactions in the last 30 days")
    
    # Analyze patterns
    analysis = monitor.analyze_insider_patterns(days_back=90)
    print(f"Analysis covers {analysis['summary']['total_transactions']} transactions")
    
    # Generate alerts
    alerts = monitor.generate_alerts(days_back=7)
    print(f"Generated {len(alerts)} alerts for recent activity")
    
    # Export data
    export_file = monitor.export_data(days_back=30, file_format='csv')
    print(f"Data exported to: {export_file}")
    
    # Get summary statistics
    stats = monitor.get_summary_statistics(days_back=30)
    print(f"Summary statistics: {stats}")


if __name__ == "__main__":
    example_usage()
