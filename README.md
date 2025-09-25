# Fridges - Smart Fridge Management System

A Python application that uses computer vision to scan receipts and automatically update your fridge inventory.

## Features

- 🔍 **Receipt Scanning**: Uses AI to extract items, quantities, and prices from receipt images
- 📦 **Fridge Management**: Automatically updates fridge inventory with scanned items
- 🗄️ **Database Storage**: PostgreSQL backend with connection pooling
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 📊 **CLI Interface**: Easy-to-use command-line interface
- 🔧 **Configuration**: Environment-based configuration management

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fridges
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up the database**
   ```sql
   CREATE DATABASE fridges_db;
   CREATE TABLE fridges (
       uid VARCHAR(255) PRIMARY KEY,
       fridge JSONB
   );
   ```

## Configuration

Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=fridges_db
DB_USER=your_username
DB_PASSWORD=your_password

# AI/ML Configuration
HF_MODEL_NAME=google/gemma-3-27b-it
HF_API_TOKEN=your_huggingface_token_here

# Application Configuration
LOG_LEVEL=INFO
```

## Usage

### Command Line Interface

**Scan a receipt and update fridge:**
```bash
python main.py scan receipt.jpg --user-id user123
```

**Dry run (scan without updating database):**
```bash
python main.py scan receipt.jpg --user-id user123 --dry-run
```

**View fridge contents:**
```bash
python main.py fridge user123
```

**Enable debug logging:**
```bash
python main.py scan receipt.jpg --user-id user123 --log-level DEBUG
```

### Python API

```python
from src.cv import scan_receipt
from src.fridge import update_fridge, get_fridge_by_id

# Scan a receipt
items = scan_receipt("receipt.jpg")

# Update fridge
success, message = update_fridge("user123", items)

# View fridge contents
fridge_contents = get_fridge_by_id("user123")
```

## Project Structure

```
fridges/
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── db/                # Database layer
│   │   ├── __init__.py
│   │   ├── dbconnect.py   # Connection management
│   │   └── db_config.py   # Database config
│   ├── fridge/            # Fridge management
│   │   ├── __init__.py
│   │   ├── update_fridge.py
│   │   └── fridge_utils.py
│   └── cv/                # Computer vision
│       ├── __init__.py
│       ├── get_items.py   # Receipt scanning
│       └── prompts/       # AI prompts
└── tests/                 # Test files
```

## Architecture

### Database Layer
- **Connection Pooling**: Efficient database connection management
- **Context Managers**: Automatic resource cleanup
- **Error Handling**: Comprehensive database error handling

### Fridge Management
- **Item Validation**: Input validation and type checking
- **Price Calculation**: Weighted average pricing for duplicate items
- **Inventory Tracking**: Complete fridge inventory management

### Computer Vision
- **Image Validation**: File format and size validation
- **AI Integration**: Hugging Face model integration
- **Response Parsing**: Robust JSON parsing with fallbacks

### Configuration
- **Environment Variables**: Centralized configuration management
- **Validation**: Configuration validation on startup
- **Flexibility**: Easy environment-specific configuration

## Error Handling

The application includes comprehensive error handling:

- **Custom Exceptions**: Specific exception types for different error conditions
- **Logging**: Structured logging with configurable levels
- **Validation**: Input validation at all entry points
- **Graceful Degradation**: Proper error recovery and user feedback

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Adding New Features

1. **Database Operations**: Add methods to `FridgeManager` or `DatabaseManager`
2. **New Commands**: Add subcommands to `main.py`
3. **Configuration**: Add new settings to `src/config.py`
4. **AI Models**: Extend `ReceiptScanner` for new model types

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | Required |
| `DB_NAME` | Database name | Required |
| `DB_USER` | Database user | Required |
| `DB_PASSWORD` | Database password | Required |
| `HF_MODEL_NAME` | AI model name | `google/gemma-3-27b-it` |
| `HF_API_TOKEN` | Hugging Face API token | Optional |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_IMAGE_SIZE_MB` | Max image size | `10` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please [create an issue](link-to-issues).
