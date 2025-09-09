# Azure AD Token Utility

A comprehensive utility for obtaining Azure AD access tokens using the Device Code flow.

--> Available in both CLI and Web UI versions. <--

## Features

### 🔧 CLI Version (`cli.py`)
- **Interactive Application Selection**: Choose from top 4 Microsoft applications or search through all available apps
- **Search Functionality**: Search through 4000+ Microsoft applications with pagination
- **Custom Client IDs**: Enter custom client IDs and scopes
- **Color-coded Output**: Clear visual feedback with colored terminal output
- **Enhanced UX**: Clear browser action instructions and Enter key prompts

<img width="1158" height="811" alt="CLI" src="https://github.com/user-attachments/assets/8f065132-e625-4910-ae50-2dafeb41a7f1" />


### 🌐 Web UI Version (`web_app.py`)
- **Modern Web Interface**: Clean, responsive design with gradient backgrounds
- **Real-time Search**: Instant search through all Microsoft applications
- **Auto-polling**: Automatic token retrieval after browser authentication
- **Copy to Clipboard**: One-click copying of tokens
- **Mobile Responsive**: Works on desktop and mobile devices

<img width="656" height="903" alt="Web" src="https://github.com/user-attachments/assets/515e2c00-a988-4e59-bb0f-bd4f2fe3fd64" />


## Top 4 Microsoft Applications

1. **Microsoft Azure CLI** - `04b07795-8ddb-461a-bbee-02f9e1bf7b46`
2. **Microsoft Teams** - `1fec8e78-bce4-4aaf-ab1b-5451cc387264`
3. **Microsoft Outlook** - `5d661950-3475-41cd-a2c3-d671a3162bc1`
4. **Azure Active Directory PowerShell** - `1b730954-1685-4b74-9bfd-dac224a7b894`

## Installation

1. **Clone or download** the utility files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
```bash
python run.py
```

## Data Source

The application uses the Microsoft Apps database from:
https://github.com/merill/microsoft-info/blob/main/_info/MicrosoftApps.csv

This provides access to over 4000 Microsoft applications with their client IDs.

## Security Notes

- **No Token Storage**: Tokens are not stored on disk
- **Session Management**: Web sessions are managed in memory only
- **Token Handling**: Always handle tokens securely and never log them

## Browser Authentication Flow

1. **Device Code Request**: The utility requests a device code from Azure AD
2. **Browser Instructions**: User is shown a URL and code to enter
3. **Authentication**: User completes authentication in their browser
4. **Token Polling**: The utility polls Azure AD for the access token
5. **Token Display**: Tokens are displayed with copy functionality

## Development

### Customization

- **Colors**: Modify the `Colors` class in `cli.py` for different terminal colors
- **Styling**: Edit the CSS in `templates/index.html` for web UI customization
- **Scopes**: Change default scopes in the application configurations

## Troubleshooting

### Common Issues

1. **"MicrosoftApps.csv not found"**: The CSV file will be downloaded automatically on first run
2. **"Session expired"**: Complete browser authentication within 15 minutes
3. **"Network error"**: Check your internet connection and Azure AD availability

### Debug Mode

For web version debugging, the Flask app runs in debug mode by default. For production, set `debug=False` in `web_app.py`.

## License

This utility is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests! 





