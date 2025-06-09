# EDGAR SEC Dashboard

A comprehensive dashboard for accessing and analyzing SEC EDGAR database using the `edgartools` package. This project provides tools for monitoring insider activities, acquiring multi-year financial statements, and analyzing fund participations.

## 🎯 Project Objectives

- **Monitor insider trading activities** - Track and analyze insider transactions in real-time
- **Multi-year financial analysis** - Retrieve and compile financial data across multiple years
- **Fund participation tracking** - Analyze institutional fund holdings and participations
- **Comprehensive visualization** - Interactive dashboard for data exploration and analysis

## 📋 Supported SEC Filing Types

- **10-K**: Annual Reports
- **10-Q**: Quarterly Reports  
- **8-K**: Current Reports
- **DEF 14A**: Proxy Statements
- **13F-HR**: Institutional Holdings
- **Form 4**: Insider Trading
- **S-1**: Registration Statements

## 🛠️ Setup Instructions

### Prerequisites
- Windows Operating System
- Python 3.8 or higher
- PowerShell

### Installation

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd edgar-sec-dashboard
   ```

2. **Create virtual environment**
   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   py -m pip install -r requirements.txt
   ```

4. **Install edgartools package**
   ```powershell
   py -m pip install edgartools
   ```

5. **Verify installation**
   ```powershell
   py -c "import edgartools; print('Installation successful!')"
   ```

## 📁 Project Structure

```
edgar-sec-dashboard/
├── classes/              # Custom classes for EDGAR data processing
├── functions/            # Utility functions and data processors
├── notebooks/            # Testing and development notebooks
├── tests/               # Unit tests for all components
├── dashboard/           # Dashboard application files
├── data/               # Cached data and configuration files
├── docs/               # Documentation and user guides
├── CHANGELOG.md        # Project changelog
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## 🚀 Development Pipeline

### Phase 1: Core Development (Current)
All classes and functions must be created and tested before dashboard development:

1. **Create Classes**:
   - Insider Trading Monitor
   - Multi-year Financial Data Aggregator
   - Fund Participation Analyzer
   - Data Merger and Processor Utilities

2. **Test in Notebooks**:
   - Each class gets a dedicated testing notebook
   - Test with real EDGAR data
   - Document functionality and performance

3. **Approval Required**: Dashboard development only begins after all components are approved

### Phase 2: Dashboard Development (Pending)
- Interactive UI development
- Data visualization implementation
- User controls and filtering
- Performance optimization

## 📓 Usage Examples

### Basic Usage
```python
# Example: Accessing 10-K filings
from classes import FinancialDataAggregator

aggregator = FinancialDataAggregator()
data = aggregator.get_annual_reports('AAPL', years=[2021, 2022, 2023])
```

### Testing Components
```powershell
# Run Jupyter notebook for testing
py -m jupyter notebook notebooks/test_insider_monitor.ipynb
```

## 🧪 Testing

### Running Tests
```powershell
# Run all tests
py -m pytest tests/

# Run specific test file
py -m pytest tests/test_insider_monitor.py

# Run with coverage
py -m pytest --cov=classes tests/
```

### Development Testing
Each component includes dedicated Jupyter notebooks in the `/notebooks/` directory:
- `test_insider_monitor.ipynb`
- `test_financial_aggregator.ipynb`
- `test_fund_analyzer.ipynb`
- `test_data_merger.ipynb`

## 📊 Dashboard Features (Coming Soon)

- **Real-time Insider Trading Monitor**
- **Multi-year Financial Statement Viewer**
- **Fund Participation Analysis Tools**
- **Interactive Data Visualizations**
- **Export Capabilities (CSV, Excel, JSON)**
- **Automated Data Updates**

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```
EDGAR_USER_AGENT=your-email@domain.com
CACHE_DIRECTORY=./data/cache
LOG_LEVEL=INFO
```

### Data Caching
The system uses intelligent caching to optimize performance:
- Cached data stored in `/data/cache/`
- Automatic cache invalidation
- Manual cache clearing options

## 📖 Documentation

- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Filing Types Reference](docs/filing-types.md)
- [Troubleshooting](docs/troubleshooting.md)

## ⚠️ Known Issues & Needed Improvements

### Financial Data Aggregator
- **Date Handling Enhancement Required**: The current implementation of financial data aggregation needs improved date handling:
  - Period end dates are currently approximated from filing dates
  - XBRL contexts contain proper period information that should be extracted
  - Fiscal year and quarter detection logic requires refinement
  - Period type classification (annual/quarterly/interim) needs better accuracy
  - Impact: May affect chronological ordering and period-based analysis accuracy

### Insider Trading Monitor
- ✅ **Fixed**: Visualization NaN value handling resolved
- ✅ **Fixed**: Data quality checks implemented

## 🤝 Contributing

1. **Follow the development pipeline**: Create and test classes before dashboard work
2. **Use PowerShell syntax** for all terminal commands
3. **Test thoroughly** in Jupyter notebooks
4. **Document everything** with clear docstrings and examples
5. **Wait for approval** before proceeding to next phase

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Check the [troubleshooting guide](docs/troubleshooting.md)
- Review existing [issues](../../issues)
- Create a new issue for bugs or feature requests

## 📈 Roadmap

- [x] **Phase 1a**: Core classes foundation
  - [x] Insider Trading Monitor (✅ Completed with visualization fixes)
  - [🔄] Financial Data Aggregator (⚠️ Needs date handling improvements)
  - [ ] Fund Participation Analyzer
  - [ ] Data Merger and Processor Utilities

- [ ] **Phase 1b**: Core classes refinement
  - [ ] Improve Financial Data Aggregator date handling
  - [ ] Enhanced XBRL period extraction
  - [ ] Comprehensive testing and validation

- [ ] **Phase 2**: Dashboard development (Pending approval)
- [ ] **Phase 3**: Advanced analytics features
- [ ] **Phase 4**: Real-time data streaming
- [ ] **Phase 5**: Machine learning integration

### Immediate Priorities
1. **Financial Data Aggregator Date Handling**: Extract proper period dates from XBRL contexts
2. **Fund Participation Analyzer**: Complete implementation
3. **Comprehensive Testing**: Validate all components with real data

---

**Note**: This project is currently in Phase 1 development. Dashboard features will be available after core components are completed and approved.