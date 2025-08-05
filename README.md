# Inventory Control
Simulate Different (s,S) inventory control policies by varying demand and lead time function. 
You can use the web interface to easily understand how and what things you can tweak.
---
## Features
- Editable Variable
    - Threshold Inventory (Reorder Point)
    - Final Inventory (Stock to full upto)
    - Simulation Time (in Days)
    - Lead Time generator function (options)
    - Demand Generator function (options)
- Advanced Settings
    - Seed for Randomization
    - Average Lead time
    - Variance in Lead time
- Results
    - Fill Rate
    - Stockouts
    - Average Inventory Level
    - Total Ordering, Holding Costs
    - Graph of Inventory Levels v/s Time
---
## Installation
```bash
# Clone the repository
git clone https://github.com/harshitsinghbhandari/inventory-control.git

# Navigate into the project directory
cd inventory-control

# Setup virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Run the app
uvicorn website:app --reload
```
Then Open you browser at [127.0.0.1:8000](127.0.0.1:8000)
---
## License
MIT License
Copyright 
© 2025 Harshit Singh Bhandari
---
## Contact
For Any Questions Contact at [harshitsingh.iitb@gmail.com](mailto:harshitsingh.iitb@gmail.com "Mail To Harshit Singh")
