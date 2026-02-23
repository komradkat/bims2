# Certificate Template Placeholder Manual

This guide lists the placeholders you can use in your Word (`.docx`) certificate templates.

## How to Use
1. Open your `certificate_template.docx` file in Microsoft Word.
2. Type the placeholder exactly as shown below (including the double curly braces `{{ }}`).
3. Save the file.
4. The system will automatically replace these text markers with real data when generating certificates.

## Available Placeholders

### Location Info
| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `{{ province }}` | Province name | *Pampanga* |
| `{{ city }}` | City or Municipality name | *San Fernando* |
| `{{ barangay_name }}` | Name of the Barangay | *San Jose* |

### Certificate Info
| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `{{ certificate_title }}` | The type/title of the certificate | *BARANGAY CLEARANCE* |
| `{{ purpose }}` | Purpose of request | *Employment* |

### Resident Info
| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `{{ full_name }}` | Full legal name of the resident | *Juan Dela Cruz* |
| `{{ citizenship }}` | Citizenship/Nationality | *Filipino* |
| `{{ address }}` | Full residential address | *Purok 1, Barangay San Jose* |

### Date Info
| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `{{ day }}` | Day of the month | *19* |
| `{{ month_year }}` | Month and Year | *February, 2026* |

### Digital Authenticity
| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `{{ qr_code }}` | **Verification Image**: Generates a QR code for authenticity tracking. | *(Generates Image)* |
| `{{ transaction_number }}` | The unique identifier for this document instance. | *CERT-20260224-1234* |
| `{{ digital_hash }}` | The **SHA256 signature** of the document for fraud prevention. | *a7c3b2...12df* |

## Advanced Formatting
You can format these placeholders directly in Word. For example:
- To make the name bold, simply highlight `{{ full_name }}` in Word and click **Bold**.
- To change the font size, select the placeholder and change the font size in Word.
- The system preserves all your Word formatting (colors, alignment, fonts).
