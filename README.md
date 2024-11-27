---

# Capstone Project: Feasibility Analysis for Sailing Using IoT and OpenCV

This project analyzes the feasibility of sailing in coastal waters by integrating IoT technology and image processing with OpenCV. It leverages environmental sensors and an IP camera to automatically detect and measure wave parameters, providing reliable information to fishermen and sailors about safe sailing conditions.

---
![3D Model Overview](https://github.com/jramadhannw/Capstone_Analisis-Berlayar_Main/blob/main/output/3dmodel.png)
## Table of Contents
- [Background](#background)
- [Project Objectives](#project-objectives)
- [System Architecture](#system-architecture)
- [Main Features](#main-features)
- [Tools and Technology](#tools-and-technology)
- [Usage](#usage)
- [Project Structure](#project-structure)

---

## Background

Traditional fishermen and sailors often face unexpected dangers at sea due to unpredictable weather and wave conditions. With advancements in technology, it is now possible to automatically analyze sea conditions using IoT systems and image processing. This project aims to be a valuable solution for enhancing sailing safety, especially for traditional fishermen, by providing real-time environmental analysis and recommendations.

---

## Project Objectives

- Develop an IoT-based system to measure marine environmental parameters.
- Apply image processing techniques using OpenCV to detect and measure wave height.
- Provide sailing feasibility recommendations based on real-time data.

---

## System Architecture

1. **IoT Sensors**  
   The system employs various sensors to monitor environmental parameters:  
   - **Anemometer**: Measures wind speed.  
   - **Wind Direction Sensor**: Determines wind direction.  
   - **BME280**: Measures temperature, pressure, and humidity.  

2. **IP Camera**  
   Captures images of the water surface to analyze wave conditions.

3. **Image Processing**  
   OpenCV is used to detect and measure wave height from the captured images. The collected data is processed to assess and recommend safe sailing conditions.

---

## Main Features

- **Weather and Environmental Monitoring**  
  Real-time monitoring of weather conditions using IoT sensors.

- **Wave Height Analysis**  
  Automatic wave detection and measurement using OpenCV image processing.

- **Sailing Feasibility Recommendation**  
  Integration of sensor data and wave analysis to provide sailors with actionable recommendations.

---

## Tools and Technology

- **Programming Language**: Python  
- **Libraries**: OpenCV, Pandas, NumPy, Matplotlib  
- **Sensors**:  
  - **Anemometer** for wind speed  
  - **Wind Direction Sensor** for wind direction  
  - **BME280** for temperature, pressure, and humidity  

- **Hardware**: IP Camera for wave detection  
- **IoT Platform**: For seamless hardware-software integration  

---

## Usage for the OpenCV

1. Clone the repository:
   ```bash
   git clone https://github.com/jramadhannw/Capstone_Analisis-Berlayar_Main.git
   cd Capstone_Analisis-Berlayar_Main
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure sensor connections and camera settings.

4. Run the system:
   ```bash
   python mwt.py
   ```

5. Results and logs will be saved in the `output/` directory.
![Result](https://github.com/jramadhannw/Capstone_Analisis-Berlayar_Main/blob/main/output/Screenshot%202024-11-26%20224805.png)
---

## Project Structure

```plaintext
Capstone_Analisis-Berlayar_Main/
├── 3D Model/           # 3D model design files
├── camera/             # Camera-related scripts and configurations
├── output/             # Analysis results and logs
├── sensor/             # Sensor code and configurations
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
```

---
