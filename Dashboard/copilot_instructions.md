# GitHub Copilot Instructions - EDGAR SEC Dashboard Project

## Project Overview
You are tasked with building a comprehensive dashboard for accessing and analyzing SEC EDGAR database using the `edgartools` package. The repository contains the package code and example notebooks that demonstrate various functionalities.

## Primary Objectives
1. **Monitor insider trading activities** - Track and analyze insider transactions
2. **Multi-year financial statement acquisition** - Retrieve and compile financial data across multiple years for one or more companies
3. **Financial statement merging** - Combine multi-year data into unified datasets for analysis
4. **Fund participation analysis** - Extract and analyze institutional fund holdings and participations
5. **Comprehensive data visualization** - Create interactive dashboard for data exploration

## Development Pipeline - MANDATORY WORKFLOW

### Phase 1: Class and Function Development
**CRITICAL**: Before any dashboard development begins, you must:

1. **Create new classes and functions** for each major functionality:
   - Insider trading monitoring class
   - Multi-year financial data aggregator class
   - Fund participation analyzer class
   - Data merger and processor utilities
   - Custom visualization components

2. **Test everything in Jupyter notebooks**:
   - Create dedicated testing notebooks for each class/function
   - Demonstrate functionality with real data examples
   - Include error handling and edge case testing
   - Document expected inputs/outputs clearly

3. **Wait for explicit approval**:
   - Present each completed class/function with test results
   - **DO NOT proceed to dashboard development without explicit approval**
   - Be prepared to iterate based on feedback

### Phase 2: Dashboard Development (Only After Approval)
Once all classes and functions are approved:
- Integrate approved components into dashboard framework
- Create interactive UI components
- Implement data visualization layers
- Add user controls and filtering options
- Ensure responsive design and performance optimization

## Technical Requirements

### Core Technologies
- **Backend**: Python with `edgartools` package
- **Data Processing**: pandas, numpy for data manipulation
- **Visualization**: plotly, dash, or streamlit for interactive components
- **Testing**: Jupyter notebooks for development and validation

### Code Standards
- Write clean, documented code with type hints
- Include comprehensive error handling
- Create modular, reusable components
- Follow PEP 8 style guidelines
- Add docstrings for all classes and functions

### Data Handling
- Implement efficient data caching mechanisms
- Handle large datasets with memory optimization
- Ensure data validation and cleaning processes
- Create backup and recovery procedures for critical data

## Key Functionalities to Implement

### 1. Insider Trading Monitor
- Real-time insider transaction tracking
- Historical insider activity analysis
- Alert systems for significant transactions
- Insider relationship mapping

### 2. Financial Statement Processor
- Automated multi-year data retrieval
- Data standardization across different reporting periods
- Financial ratio calculations
- Trend analysis capabilities

### 3. Fund Participation Analyzer
- Institutional holdings tracking
- Ownership percentage calculations
- Fund performance correlation analysis
- Portfolio overlap identification

### 4. Data Integration Layer
- Seamless merging of different data sources
- Data quality validation
- Automated data updates
- Export capabilities (CSV, Excel, JSON)

## Filing Types Support
The dashboard must support the following SEC filing types:
- **10-K**: Annual Reports
- **10-Q**: Quarterly Reports  
- **8-K**: Current Reports
- **DEF 14A**: Proxy Statements
- **13F-HR**: Institutional Holdings
- **Form 4**: Insider Trading
- **S-1**: Registration Statements

## Platform Requirements
- **Operating System**: Windows
- **Python Command**: Use `py` instead of `python`
- **Terminal**: PowerShell syntax required for all commands
- **Package Manager**: pip (called via `py -m pip`)

## Repository Structure Expectations
```
/classes/           # Custom classes for EDGAR data processing
/functions/         # Utility functions and data processors
/notebooks/         # Testing and development notebooks
/tests/            # Unit tests for all components
/dashboard/        # Dashboard application files
/data/             # Cached data and configuration files
/docs/             # Documentation and user guides
CHANGELOG.md        # Project changelog
README.md           # Project overview and setup
```

## Testing Protocol
For each new class or function:
1. Create a dedicated notebook named `test_[component_name].ipynb`
2. Include at least 3 different use cases
3. Test with both valid and invalid inputs
4. Document performance metrics where relevant
5. Show actual EDGAR data examples
6. Include visualization of results when applicable

## Approval Process
Before proceeding to dashboard development:
1. Present all completed classes with test results
2. Demonstrate integration between components
3. Show performance benchmarks
4. Provide clear documentation
5. **Wait for explicit "APPROVED" confirmation**

## Communication Guidelines
- Always ask for clarification when requirements are unclear
- Provide regular progress updates
- Show working examples rather than just describing functionality
- Be transparent about limitations or challenges encountered
- Request feedback early and often during development phase

## Success Criteria
- All classes and functions pass comprehensive testing
- Code is modular, efficient, and well-documented
- Dashboard provides intuitive access to all EDGAR functionalities
- System handles real-world data volumes effectively
- User can easily monitor insider activities, analyze financial trends, and track fund participations

Remember: **NO DASHBOARD DEVELOPMENT UNTIL ALL COMPONENTS ARE TESTED AND APPROVED**