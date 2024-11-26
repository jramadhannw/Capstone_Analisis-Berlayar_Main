# Capstone Project: Feasibility Analysis for Sailing Using IoT and OpenCV

This project aims to analyze the feasibility of sailing in coastal waters using IoT technology and image processing with OpenCV. The system leverages multiple environmental sensors and an IP camera to automatically detect and measure wave parameters. This analysis provides accurate information to fishermen or sailors about safe sailing conditions.

## Table of Contents
- [Background](#background)
- [Project Objectives](#project-objectives)
- [System Architecture](#system-architecture)
- [Main Features](#main-features)
- [Tools and Technology](#tools-and-technology)
- [Usage](#usage)
- [Project Structure](#project-structure)

## Background
Fishermen often face unexpected dangers at sea. With advances in technology, it is now possible to automatically analyze sea conditions using IoT and image processing systems. This project aims to be a valuable solution to enhance sailing safety, especially for traditional fishermen.

## Project Objectives
- Develop an IoT-based system to measure marine environmental parameters.
- Apply image processing with OpenCV to detect and measure wave height.
- Provide sailing feasibility recommendations based on the collected data.

## System Architecture
1. **IoT Sensors**: The system uses various sensors, including:
   - **Anemometer**: Measures wind speed.
   - **Wind Direction Sensor**: Measures wind direction.
   - **BME280**: Measures temperature, pressure, and humidity.
2. **IP Camera**: Captures images of water conditions for further analysis.
3. **Image Processing**: Uses OpenCV to detect and measure waves from captured images.

Data from the sensors and image processing is used to provide recommendations to sailors regarding safe sailing conditions.

## Main Features
- **Weather and Environmental Monitoring**: Obtains weather data from sensors and displays real-time information.
- **Automatic Wave Analysis**: Uses OpenCV to detect and measure wave height.
- **Sailing Feasibility Recommendation**: Provides users with recommendations based on the processed data.

## Tools and Technology
- **Python**: Main programming language.
- **OpenCV**: For image processing and wave measurement.
- **Anemometer, Wind Direction, BME280 Sensors**: For environmental monitoring.
- **IP Camera**: For capturing images of water conditions.
- **IoT Platform**: Connects hardware and software into a single ecosystem.

## Usage
1. Clone this repository:
   ```bash
   git clone https://github.com/jramadhannw/Capstone_Analisis-Berlayar_Main.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the system:
   ```bash
   python mwt.py
   ```

## Project Structure
```
Capstone_Analisis-Berlayar_Main
├── data                # Data and processed images
├── scripts             # Scripts for data and image processing
├── docs                # Project documentation
├── tests               # System testing
├── README.md           # Main project documentation
└── mwt.py             # Main file to run the system
```
