# Interior-Ai-Designer

Overview:

This application is a full-stack solution built with Streamlit and integrated with MySQL, designed to generate realistic interior design transformations using AI. Users can upload room photos or capture them via camera, select room types and design styles, and download the redesigned images.

Features:
AI-Powered Design Generation: Utilizes Stable Diffusion for photorealistic interior redesigns.
Multiple Room Types: Supports Bedroom, Hall (Living Room), Kitchen, and Office transformations.
Design Styles: Offers Modern, Rustic, Bohemian, Scandinavian, and Industrial styles.
User Authentication: Integrates with MySQL for user management with hashed passwords and Google OAuth support.
Realism Control: Adjustable transformation strength and style guidance sliders.
Download Functionality: Allows users to download generated design images.

Installation:
Clone the repository: git clone (https://github.com/MR-MOHITPATEL/Interior-Ai-Designer.git)
Navigate to the project directory: cd interior-design-app

Install Python dependencies: pip install -r requirements.txt (

Set up MySQL:
Install XAMPP or a similar MySQL server.
Update integrate_to_mysql.py with your MySQL root password if needed.
Run python integrate_to_mysql.py to create the database and users table.
Configure environment variables (e.g., database credentials) in a .env file.
Run the application: streamlit run app.py

Usage:
Upload a photo or use the camera to input a room image.
Select the room type and up to three design styles.
Adjust the transformation strength and style guidance sliders.
Click "Generate Designs" to create and download redesigned images.

Technologies Used:
Frontend: Streamlit
Backend: Python
AI Model: Stable Diffusion
Database: MySQL

Authentication: bcrypt for password hashing, Google OAuth
Prerequisites:
Python 3.8+
PyTorch with CUDA support (if available)
MySQL server (e.g., via XAMPP)
Required Python libraries (listed in requirements.txt)

Contributing:
Fork the repository and submit pull requests. For major changes, please open an issue to discuss.

License:
This project is licensed under the MIT License.
