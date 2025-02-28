# Smart Home System

![Image](https://github.com/user-attachments/assets/da42d199-528a-4095-b047-31ba1ed85f99)


## Overview
The **Smart Home System** is an IoT-based home automation project designed to enhance convenience, security, and energy efficiency. <br>
This system integrates various sensors and actuators, allowing users to control and monitor their home remotely via interface.

## Features

- **👤Face ID Authentication**: Provides secure access control using facial recognition technology.
- **🔑RFID KEY**: 

- **🚪Automated Garage Door**: Utilizes OpenCV and EasyOCR for vehicle license plate recognition to grant or deny access.

  - **🚧Obstacle Detection**: The TCRT5000 sensor detects obstacles while closing the garage door <br>
                            and automatically reverses its state to prevent accidents.

- **📱Remote Control**: Allows users to control lights, door, and other appliances via a mobile or web interface.

- **📹Real-time Monitoring**: Displays live data from log and gas sensors.


## Technologies Used

<table align="center">
  <tr>
    <td align="left" width="30%">
      <img src="https://github.com/user-attachments/assets/1a8d6be4-aaf7-4ad8-b8a5-d05e9b1c35ef" width="100%">
    </td>
    <td align="left" width="70%">
      <ul>
        <li> <b>Software</b>: 
          <br>
          <a href="https://skillicons.dev">
            <img src="https://skillicons.dev/icons?i=git,anaconda,aws,python,arduino,flask,qt,opencv,ubuntu,apple,pytorch" />
          </a>
        </li>
        <br>
        <li> <b>Hardware </b>: 
          <br>
          <!-- Add hardware details here -->
          ESP32 Camera, &nbsp;&nbsp;  Arudino Uno3, &nbsp;&nbsp;  Step Motor, &nbsp;&nbsp; Servo Motor, &nbsp;&nbsp; TCRT5000, &nbsp;&nbsp; RFID, &nbsp;&nbsp; Gas Sensor, &nbsp;&nbsp; Speaker, &nbsp;&nbsp; Push Button, &nbsp;&nbsp; LED
        </li>
      </ul>
    </td>
  </tr>
</table>


## Scenario
<p align="center">
  <img width="797" alt="FaceID" src="https://github.com/user-attachments/assets/4a7569e4-3137-4ae3-8614-3cad2de08269" />
  <img width="797" alt="Gas" src="https://github.com/user-attachments/assets/0b3f586e-0202-4cc0-b409-496e79927be3" />
  <img width="797" alt="Image" src="https://github.com/user-attachments/assets/8514f942-678c-4465-8132-71987d0cfbc2" />
</p>

## System Requriements
<table align="center">
  <tr>
    <td valign="top">
      <img src="https://github.com/user-attachments/assets/e4f4f417-b203-4c1d-9f84-a32d16b25a1d" alt="Image 1" width="500">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/fc35b743-2d90-4fc1-9c9e-916ad2c2e09f" alt="Image 2" width="500">
    </td>
  </tr>
</table>


## System Architecture
<img align="center" width="1000" alt="Image" src="https://github.com/user-attachments/assets/7acf757f-749d-47a5-b45f-1d83edd5a831" />

## Database
<p align="center">
  <img  width="800" alt="Image" src="https://github.com/user-attachments/assets/4dfdb029-6a1a-4b57-8d9e-9e952dec49d6" />
</p>

## GUI

<table align="center">
  <tr>
    <td valign="top">
      <img width="335" alt="Image" src="https://github.com/user-attachments/assets/806f69a7-cd5b-40b6-8fe9-eafda187265d" />
    </td>
  </tr>
</table>
<p align="center">
  Once you log in -> the main panel will show up, which allows you to controll your house
</p>
<p>
  <table align="center">
    <tr>
      <td>
        <img width="469" alt="Image" src="https://github.com/user-attachments/assets/eeba5b03-1556-42d2-8583-9552ecb98fda" />
      </td>
      <td> 
        <table>
          <tr>
            <td valign="top">1</td>
            <td>현관 카메라 작동 버튼 및 상태 확인</td>
          </tr>
          <tr>
            <td valign="top">2</td>
            <td>현관 카메라 화면</td>
          </tr>
          <tr>
            <td valign="top">3</td>
            <td>조명 제어 버튼 및 상태 확인</td>
          </tr>
          <tr>
            <td valign="top">4</td>
            <td>차고문 제어 버튼 상태 확인</td>
          </tr>
          <tr>
            <td valign="top">5</td>
            <td>현관문 제어 버튼 및 상태 확인</td>
          </tr>
          <tr>
            <td valign="top">6</td>
            <td>창문 제어 버튼 및 상태 확인</td>
          </tr>
          <tr>
            <td valign="top">7</td>
            <td>현재 가스 상태 확인</td>
          </tr>
          <tr>
            <td valign="top">8</td>
            <td>Usertab 버튼</td>
          </tr>
          <tr>
            <td valign="top">9</td>
            <td>Logtab 버튼</td>
          </tr>
        </table>
      </td>
          
  </table>
  
</p>



